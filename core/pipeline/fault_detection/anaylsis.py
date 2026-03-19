import numba

import cv2, math
import numpy as np
from dataclasses import dataclass
from . import numba_jit


class FaultEnum():
    Sticky_Line = '毛粘线'
    Bubble = '汽包'
    Particle = '粒子'


@dataclass
class AnaylsisOutput:
    has_fault: bool
    fault_type: str = ''


@numba.njit
def _jit_std_with_mask(arr, mean, mask):
    """ 计算 mask区域中的方差 """
    std_outside = np.sum((arr - mean) ** 2 * mask) / np.sum(mask)
    return std_outside


@numba.njit
def _jit_mean_with_mask(arr, mask):
    """ 计算 mask区域中的方差 """
    mean = np.sum(arr * mask) / np.sum(mask)
    return mean


@numba.njit
def _jit_feature_with_gxy_residual(gxy, residual, mask):
    """ 计算 mask区域中的方差 """
    num = np.sum(mask)
    feature_gxy = np.sum(gxy * mask) / num
    feature_residual = np.sum(residual * mask) / num
    return feature_gxy, feature_residual


@numba.njit
def _jit_mask_and_crop(img, x, y, w, h):
    height, width = img.shape[:2]
    edge_w, edge_h = int(w * 0.2), int(h * 0.2)
    edge_left, edge_right = edge_w, edge_w
    edge_top, edge_bottom = edge_h, edge_h
    x1, y1, x2, y2 = int(x - edge_left), int(y - edge_top), int(x + w + edge_right), int(y + h + edge_bottom)
    _x1, _y1, _x2, _y2 = max(x1, 0), max(y1, 0), min(x2, width), min(y2, height)
    edge_left, edge_right = edge_left - abs(x1 - _x1), edge_w - abs(x2 - _x2)
    edge_top, edge_bottom = edge_h - abs(y1 - _y1), edge_h - abs(y2 - _y2)

    crop_img = img[_y1:_y2, _x1:_x2]
    mask = np.ones(shape=crop_img.shape[:2])
    mask[edge_top:-edge_bottom, edge_left:- edge_right] = 0
    return crop_img, mask, _x1, _y1


def anaylsis(cnt: np.ndarray,
             img: np.ndarray,
             gxy: np.ndarray,
             residual: np.ndarray,
             threshold: float, ) -> AnaylsisOutput:
    # # crop
    x, y, w, h = cv2.boundingRect(cnt)

    crop_img, mask, x1, y1 = _jit_mask_and_crop(img=img, x=x, y=y, w=w, h=h)
    mean_outside = _jit_mean_with_mask(arr=crop_img, mask=mask)

    mask[:, :] = 0
    _cnt = numba_jit.add(cnt, np.array((-x1, -y1)))
    cv2.drawContours(mask, [_cnt], -1, 1, -1)

    # 方差
    std_outside = _jit_std_with_mask(arr=crop_img, mean=mean_outside, mask=mask)
    # std_outside = np.sum((crop_img - mean_outside) ** 2 * mask_cnt) / np.sum(mask_cnt)

    # 计算梯度方向
    gx = cv2.Sobel(crop_img, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(crop_img, cv2.CV_32F, 0, 1, ksize=3)
    # angle = np.arctan2(gy, gx)
    # 转成向量（关键！避免角度跳变）
    # cos_a = np.cos(angle)
    # sin_a = np.sin(angle)
    # 在候选区域内计算“方向一致性”
    # mean_cos = np.mean(cos_a)
    # mean_sin = np.mean(sin_a)
    # coherence = np.sqrt(mean_cos ** 2 + mean_sin ** 2)
    # print(coherence.max(), coherence.min())
    Jxx = cv2.GaussianBlur(gx * gx, (9, 9), 0)
    Jyy = cv2.GaussianBlur(gy * gy, (9, 9), 0)
    Jxy = cv2.GaussianBlur(gx * gy, (9, 9), 0)
    tmp = np.sqrt((Jxx - Jyy) ** 2 + 4 * Jxy * Jxy)
    lambda1 = (Jxx + Jyy + tmp) / 2
    lambda2 = (Jxx + Jyy - tmp) / 2
    coherence = (lambda1 - lambda2) / (lambda1 + lambda2 + 1e-5)

    print('coherence:', coherence.min())

    # mask = 255 - mask.astype(np.uint8) * 255
    # result_ns = cv2.inpaint(crop_img, mask, 7, cv2.INPAINT_TELEA)  # Navier-Stokes
    # ssim_index = compute_ssim(crop_img, result_ns)
    # ssim = cv2.compare_ssim(crop_img, mask, multichannel=True)
    # print(u, std_outside, ssim)
    # print()
    # cv2.imwrite(f'cache/anaylsis-crop-{u}.jpg', crop_img)
    # u += 1
    has_fault = std_outside > threshold and coherence.min() < 0.45

    # 没有缺陷
    if not has_fault:
        return AnaylsisOutput(
            has_fault=has_fault
        )

    # ===================
    # 分析缺陷类型
    # ===================
    crop_h, crop_w = crop_img.shape[:2]
    crop_gxy = gxy[y1:y1 + crop_h, x1:x1 + crop_w]
    crop_residual = residual[y1:y1 + crop_h, x1:x1 + crop_w]
    feature_gxy, feature_residual = _jit_feature_with_gxy_residual(gxy=crop_gxy, residual=crop_residual, mask=mask)
    area = cv2.contourArea(cnt)  # 计算面积
    perimeter = cv2.arcLength(cnt, True)  # 计算周长
    a_p_r = area * math.pi * 4 / perimeter # 圆度
    # print(feature_gxy, feature_residual, area, perimeter, a_p_r)

    if a_p_r > 100:
        fault_type = FaultEnum.Sticky_Line
    elif feature_residual < 0:
        fault_type = FaultEnum.Particle
    elif feature_residual >= 0:
        fault_type = FaultEnum.Bubble
    else:
        fault_type = FaultEnum.Particle

    return AnaylsisOutput(
        has_fault=has_fault,
        fault_type=fault_type
    )
    # raise Exception
