import time

import cv2
import numpy as np
from typing import List
from dataclasses import dataclass
from .canny import weighted_canny
from .fft import fft_remove_texture
from .anaylsis import anaylsis

line_color = (0, 255, 0)
box_color = (0, 0, 255)

u = 1

# cv2.ocl.setUseOpenCL(True)


@dataclass
class DetectOutput:
    x: int or float
    y: int or float
    w: int or float
    h: int or float
    ftype: str

    def to_tuple(self):
        return (self.x,
                self.y,
                self.w,
                self.h,
                self.ftype)

    def to_dict(self):
        return {'x': self.x,
                'y': self.y,
                'w': self.w,
                'h': self.h,
                'ftype': self.ftype}


def detect(img: np.ndarray) -> List[DetectOutput]:
    # print(img.shape,img.max(),img.min())
    # rgb or gray
    if len(img.shape) == 2:
        gray = img.astype(np.uint8)
        # gray = np.tile(gray[:, :, np.newaxis], (1, 1, 3))
    elif len(img.shape) == 3:
        assert img.shape[2] == 3, 'the channel should be 3'
        img = img.astype(np.uint8)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # height and width
    scale = 0.5
    gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    height, width = gray.shape[:2]

    # 裁剪出需要识别的区域
    #crop_output = crop_detect_area(gray)
    # fft 过滤纹理
    gray = fft_remove_texture(gray)

    # 提取特征
    canny_output = weighted_canny(gray, low_thresh=60, high_thresh=110)


    # 腐蚀膨胀
    feature = cv2.bitwise_or(canny_output.processed_residual, canny_output.processed_gxy)
    # cv2.imshow('feature', gray)

    for _ in range(10):
        feature = cv2.erode(feature, np.ones((3, 3), np.uint8), iterations=1)
        feature = cv2.dilate(feature, np.ones((3, 3), np.uint8), iterations=1)
        #     feature = cv2.erode(feature, np.ones((32, 24), np.uint8), iterations=1)

    # Step 1：去背景（保留局部差异）
    # bg = cv2.GaussianBlur(feature, (1, 1), 0)
    # feature = cv2.subtract(bg, feature)

    clahe = cv2.createCLAHE(2.0, (8, 8))

    # params = cv2.SimpleBlobDetector_Params()
    # # 设置阈值范围
    # params.minThreshold = 0
    # params.maxThreshold = 255
    # # 按面积筛选
    # params.filterByArea = False
    # params.minArea = 50
    # # 按圆度筛选
    # params.filterByCircularity = False
    # # 创建检测器
    # detector = cv2.SimpleBlobDetector_create(params)
    # # 检测
    # keypoints = detector.detect(feature)
    # print(keypoints)
    # 绘制
    # out = cv2.drawKeypoints(feature, keypoints, None, (0, 0, 255),
    #                         cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    #kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21))
    #tophat = cv2.morphologyEx(feature, cv2.MORPH_TOPHAT, kernel)
    # feature_f = feature.astype(np.float32)
    # mean = cv2.blur(feature_f, (15, 15))
    # sqmean = cv2.blur(feature_f ** 2, (15, 15))** 0.5
    # std = np.sqrt(sqmean - mean ).astype(np.uint8)


    # cv2.imshow("blob", out)
    # cv2.imshow("feature", feature)
    # cv2.imshow("sqmean", sqmean.astype(np.uint8))
    # cv2.imwrite("feature.jpg", feature)
    # cv2.waitKey(0)
    #
    # feature = std
    # feature = clahe.apply(feature)
    # th2 = cv2.adaptiveThreshold(
    #     feature,
    #     255,
    #     cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    #     cv2.THRESH_BINARY,
    #     11,
    #     5
    # )
    # feature = th2

    # 找轮廓(可能的缺陷)
    _, binary = cv2.threshold(feature, 75, 255, cv2.THRESH_BINARY)
    binary = cv2.dilate(binary, np.ones((3, 3), np.uint8), iterations=3)
    #binary = cv2.erode(binary, np.ones((3, 3), np.uint8), iterations=3)
    # cv2.imshow('feature', feature)
    #

    # while True:
    #     cv2.imshow('canny_output', feature)
    #     cv2.imwrite('canny_output.png', feature)
    #     cv2.waitKey(1)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # print(contours)
    _contours = []
    for cnt in contours:
        #if cv2.contourArea(cnt) < 0: continue  # 过滤太小的色块
        x, y, w, h = cv2.boundingRect(cnt)
        if x == 0 or x + w == width or y == 0 or y + h == height:
            continue

        # if w < width * 0.01 or h < height * 0.01: continue
        if h > height * 0.5: continue
        _contours.append(cnt)

    # 进一步分析是否是缺陷
    outputs = []
    for cnt in _contours:
        anaylsis_output = anaylsis(cnt=cnt, img=gray,
                                   gxy=canny_output.gxy,
                                   residual=canny_output.residual,
                                   threshold=30)
        if not anaylsis_output.has_fault:
            continue
        x, y, w, h = cv2.boundingRect(cnt)
        # offset_x, offset_y, offset_w, offset_h = crop_output.offset
        # x, y = x + offset_x, y + offset_y
        outputs.append(
            DetectOutput(
                x=x / scale, y=y / scale, w=w / scale, h=h / scale, ftype=anaylsis_output.fault_type
            ))
    # 绘制
    # for detect_output, cnt in zip(outputs, analysis_contours):
    #     x, y, w, h = detect_output.x, detect_output.y, detect_output.w, detect_output.h
    #     area = cv2.contourArea(cnt)
    #
    #     cv2.rectangle(img, (x, y), (x + w, y + h), box_color, 2)
    #     cv2.putText(img, f"Area:{int(area)}", (x, y - 5),
    #                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color, 1)

    # # 霍夫变换
    # lines = cv2.HoughLinesP(canny, 2, np.pi / 180, 180, minLineLength=100, maxLineGap=128)
    # # 绘制直线
    # for line in (lines):
    #     x1, y1, x2, y2 = line[0]
    #     x3, y3 = line_by_two_points(p1=(x1, y1), p2=(x2, y2), y=0)
    #     cv2.line(img, (x1, y1), (x2, y2), line_color, 2)

    # cv2.imwrite('cache/gray.jpg', gray)
    # cv2.imwrite('cache/canny.jpg', residual)
    # cv2.imwrite('cache/img.jpg', img)
    # cv2.imwrite('cache/binary.jpg', binary)
    # cv2.imwrite('cache/feature.jpg', feature)
    # print(time.time() - st)
    return outputs
