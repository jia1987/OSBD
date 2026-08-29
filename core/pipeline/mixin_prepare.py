import numpy as np
from typing import Dict
from .meta import ModelConfig
from ..config import config
import cv2

_clahe_cache = {}


def _get_clahe():
    """ 按配置创建/复用 CLAHE (配置不变时复用同一实例) """
    clip = float(config.get(config.Prepare_ClipLimit))
    grid = int(config.get(config.Prepare_Grid))
    key = (clip, grid)
    if key not in _clahe_cache:
        _clahe_cache[key] = cv2.createCLAHE(clipLimit=clip, tileGridSize=(grid, grid))
    return _clahe_cache[key]


class PrepareMixin():
    def prepare(self, images: Dict[str, np.ndarray], modelConfig: ModelConfig) -> None:
        clahe = _get_clahe()
        ratio = float(config.get(config.Prepare_RoiRatio))
        for v, image in images.items():
            # 空图片
            if image is None: continue

            h, w = image.shape[:2]
            rectification = modelConfig.rectification.get(v)
            # 未配置或配置为「不校正」(0,1,0,1) 时跳过处理
            # 注意: 从 json 加载后是 list, 必须转 tuple 再比较
            if rectification is None or tuple(rectification) == (0, 1, 0, 1): continue
            top_lower, top_upper, bottom_lower, bottom_upper = rectification

            # 透视变换
            # 原图上的四个点 (顺序很重要：左上, 右上, 左下, 右下)
            pts1 = np.float32([[top_lower * w, 0], [top_upper * w, 0],
                               [bottom_lower * w, h], [bottom_upper * w, h]])
            # 变换后的目标位置 (映射成一个规则矩形)
            new_width = max(top_upper - top_lower, bottom_upper - bottom_lower) * w
            pts2 = np.float32([[0, 0], [new_width, 0], [0, h], [new_width, h]])

            # 计算透视变换矩阵
            M = cv2.getPerspectiveTransform(pts1, pts2)
            # 应用透视变换
            dst = cv2.warpPerspective(image, M, (int(new_width), h))
            # 直方图均衡
            enhanced = clahe.apply(dst)
            # ROI 裁剪: 取中部 (ratio ~ 1-ratio), 默认 1/3 与历史行为一致
            images[v] = enhanced[int(h * ratio):int(h * (1 - ratio))]
