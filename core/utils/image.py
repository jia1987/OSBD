import numpy as np
from PyQt5.QtGui import QImage, QPixmap

def np_2_pixmap(arr: np.ndarray) -> QPixmap:
    """将 NumPy 数组转为 QPixmap"""
    if arr.ndim == 2:  # 灰度图
        h, w = arr.shape
        bytes_per_line = w
        qimg = QImage(arr.data, w, h, bytes_per_line, QImage.Format_Grayscale8)
    elif arr.ndim == 3:
        h, w, ch = arr.shape
        if ch == 3:  # RGB
            bytes_per_line = ch * w
            qimg = QImage(arr.data, w, h, bytes_per_line, QImage.Format_RGB888)
        elif ch == 4:  # RGBA
            bytes_per_line = ch * w
            qimg = QImage(arr.data, w, h, bytes_per_line, QImage.Format_RGBA8888)
        else:
            raise ValueError("通道数必须是 1, 3 或 4")
    else:
        raise ValueError("输入必须是 2D 灰度图或 3D 彩色图")

    # 注意：arr 必须是连续内存，否则 QImage 会显示错乱
    if not arr.flags['C_CONTIGUOUS']:
        arr = np.ascontiguousarray(arr)

    return QPixmap.fromImage(qimg)


