import cv2, math
import numpy as np
from typing import Tuple
import cv2
import numpy as np
from dataclasses import dataclass

line_color = (0, 255, 0)
box_color = (0, 0, 255)


@dataclass
class Output:
    crop: np.ndarray
    offset: Tuple[int, int, int, int,]


def distance_origin_from_line(k, x0, y0):
    """
    k: 斜率；若为 None 或 math.isinf(k) 表示竖直线
    (x0, y0): 直线上一点
    返回: 到原点的距离
    """
    if k is None or math.isinf(k):
        return abs(x0)  # x = x0
    return abs(y0 - k * x0) / math.sqrt(k ** 2 + 1)


def crop_detect_area(gray: np.ndarray):
    def cluster_by_distance(data, threshold):
        data = sorted(data)
        clusters = []
        cluster = [data[0]]

        for i in range(1, len(data)):
            if data[i] - data[i - 1] <= threshold:
                cluster.append(data[i])
            else:
                clusters.append(cluster)
                cluster = [data[i]]
        clusters.append(cluster)
        return clusters

    # 梯度图裁剪
    gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    gx = np.abs(gx)
    gx = ((gx - gx.min()) / gx.ptp() * 255).astype(np.uint8)
    _, gx = cv2.threshold(gx, 100, 255, cv2.THRESH_BINARY)
    img = np.tile(gray[:, :, np.newaxis], (1, 1, 3))

    # 霍夫变换
    _lines = cv2.HoughLinesP(gx, 2, np.pi / 180, 180, minLineLength=100, maxLineGap=128)

    if _lines is not None:
        # 坐标 -> 角度
        lines = []
        for line in _lines:
            x1, y1, x2, y2 = line[0]
            k = abs(y1 - y2) / abs(x1 - x2) if x1 != x2 else None
            distance = distance_origin_from_line(k=k, x0=x1, y0=y1)
            lines.append((distance, k))

        # 聚类
        kmeans = cluster_by_distance(data=[l[0] for l in lines], threshold=10)
    else:
        kmeans = []

    # 有两个以上的簇
    if len(kmeans) >= 2:
        left, right = max(kmeans[0]) + 10, min(kmeans[-1]) - 10
        left, right = int(left), int(right)
    else:
        left, right = 0, gray.shape[1]


    # cv2.imwrite('cache/crop.jpg', gx)

    if _lines is not None:
        for line in (_lines):
            x1, y1, x2, y2 = line[0]
            cv2.line(img, (x1, y1), (x2, y2), line_color, 2)
    # cv2.imwrite('cache/crop-img.jpg', img)
    return Output(
        crop=gray[:, left:right],
        offset=(left, 0, right - left, gray.shape[0]),
    )
