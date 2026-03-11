import cv2, numba
import numpy as np
from dataclasses import dataclass
from .cache import cache_kenel
from . import numba_jit

@dataclass
class Output:
    gx: np.ndarray
    gy: np.ndarray
    gxy: np.ndarray
    residual: np.ndarray
    # processed
    processed_gxy: np.ndarray
    processed_residual: np.ndarray


@numba.jit(nopython=True)
def gamma_format(img, gamma=2.) -> np.ndarray:
    img = ((img.astype(np.float32) - img.min()) / (img.max()-img.min()))
    img = img ** gamma
    return (img * 255).astype(np.uint8)


@numba.jit(nopython=True)
def _jit_gxy(gx, gy):
    gxy = (0.75 * gx ** 2 + 1.25 * gy ** 2) ** 0.5
    return gxy


#@numba.jit(nopython=True)
def _jit_uniform(a):
    b = ((a - a.min()) / (a.max() - a.min()) * 255).astype(np.uint8)
    return b


@numba.jit(nopython=True)
def _jit_get_residual(gray, mean):
    residual = gray - mean
    return residual


def _jit_weighted_canny(gray, low_thresh=50, high_thresh=150) -> Output:
    # Sobel 梯度
    _gx: np.ndarray = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    _gy: np.ndarray = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    _gxy = _jit_gxy(gx=_gx, gy=_gy)
    # gx, gy = np.gradient(gray)  # .astype(np.uint8)
    # gxy = ((gxy - gxy.min()) / gxy.ptp() * 255).astype(np.uint8)

    # 腐蚀膨胀
    gxy = _jit_uniform(_gxy.astype(np.float32))
    for _ in range(1):
        # gxy = cv2.dilate(gxy, np.ones((3, 15), np.uint8), iterations=1)
        # gxy = cv2.erode(gxy, np.ones((7, 7), np.uint8), iterations=1)
        gxy = cv2.blur(gxy, (5, 5))
        gxy = gamma_format(gxy, gamma=1.1)
        # gxy = cv2.dilate(gxy, cache_kenel(w=7, h=7), iterations=1)
        # gxy = cv2.erode(gxy, cache_kenel(w=7, h=7), iterations=1)
        gxy = cv2.morphologyEx(gxy, cv2.MORPH_CLOSE, cache_kenel(w=7, h=7))
        # print(np.bincount(gxy.reshape((gxy.shape[0] * gxy.shape[1]))))
        # print(gxy.max())

    # residual
    mean = np.mean(gray, axis=0)
    _residual = _jit_get_residual(gray=gray, mean=mean[np.newaxis])
    residual = _jit_uniform(numba_jit.abs(_residual))
    for _ in range(1):
        # residual = cv2.dilate(residual, np.ones((7, 7), np.uint8), iterations=1)
        # residual = cv2.erode(residual, np.ones((7, 7), np.uint8), iterations=1)
        residual = cv2.blur(residual, (5, 5))
        residual = gamma_format(residual, gamma=1.1)
        # residual = cv2.dilate(residual, cache_kenel(w=7, h=7), iterations=1)
        # residual = cv2.erode(residual, cache_kenel(w=7, h=7), iterations=1)
        # dilate -> erode = close
        residual = cv2.morphologyEx(residual, cv2.MORPH_CLOSE, cache_kenel(w=7, h=7))
        # residual
        # print(np.bincount(residual.flatten()))
        # print(np.where(residual == 255,))

    # cv2.imwrite('cache/gx.jpg', gx)
    # cv2.imwrite('cache/gy.jpg', gy)
    # cv2.imwrite('cache/gxy.jpg', gxy)
    #cv2.imwrite('cache/residual.jpg', _jit_uniform_residual))

    return {
        "gx": _gx,
        "gy": _gy,
        "gxy": _gxy,
        "residual": _residual,
        "processed_gxy": gxy,
        "processed_residual": residual,
    }


def weighted_canny(img, low_thresh=50, high_thresh=150):
    # canny = cv2.Canny(gxy, low_thresh, high_thresh)
    return Output(**_jit_weighted_canny(img))
