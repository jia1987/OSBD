import pyfftw
import numpy as np

from functools import cache
from . import numba_jit


@cache
def _create_mask(shape, k1, k2):
    rows, cols = shape
    crow, ccol = rows // 2, cols // 2
    mask = np.ones(shape)
    k1, k2 = 0.492, 0.49999999999999999999999999
    mask[int(rows * k1):-int(rows * k1), int(ccol * k1):-int(ccol * k1)] = 0
    mask[int(rows * k2):-int(rows * k2), int(ccol * k2):-int(ccol * k2)] = 1
    mask[crow, ccol] = 1
    return np.fft.ifftshift(mask)


@cache
def fft2_plan(shape):
    in_array = pyfftw.empty_aligned(shape, dtype=np.complex64)
    out_array = pyfftw.empty_aligned(shape, dtype=np.complex64)
    fft_object = pyfftw.FFTW(in_array, out_array, axes=(0, 1), threads=4)
    return in_array, out_array, fft_object


@cache
def ifft2_plan(shape):
    in_array = pyfftw.empty_aligned(shape, dtype=np.complex64)
    out_array = pyfftw.empty_aligned(shape, dtype=np.complex64)
    fft_object = pyfftw.FFTW(in_array, out_array, axes=(0, 1), direction='FFTW_BACKWARD', threads=4)
    return in_array, out_array, fft_object


def fft2_fftw(a, threads=1):
    """
    用 pyFFTW 实现 numpy.fft.fft2 的功能
    :param a: 输入 numpy.ndarray
    :param threads: 使用的线程数
    :return: 复数结果 ndarray
    """
    # 创建计划, 缓存
    in_array, out_array, fft_object = fft2_plan(a.shape)
    in_array[:] = a[:]
    # numba_jit.setter(a=in_array, b=a)
    fft_object()
    return out_array  # .copy()


def ifft2_fftw(a, threads=1):
    """
    用 pyFFTW 实现 numpy.fft.ifft2 的功能
    :param a: 输入复数 ndarray
    :param threads: 使用线程数
    :return: 复数结果 ndarray
    """
    # 创建计划, 缓存
    in_array, out_array, fft_object = ifft2_plan(a.shape)
    in_array[:] = a[:]
    # numba_jit.setter(a=in_array, b=a)
    fft_object()
    return out_array  # .copy()


# @numba.njit
def _jit_fft_remove_texture(img, mask):
    # f = np.fft.fft2(img)
    f = fft2_fftw(img)
    # fshift = np.fft.fftshift(f)

    # 应用 mask
    _fshift = numba_jit.multiplicate(f, mask)

    # 反变换
    # f_ishift = np.fft.ifftshift(_fshift)
    # img_back = np.fft.ifft2(_fshift)
    img_back = ifft2_fftw(_fshift)
    img_back = numba_jit.astype(numba_jit.abs(img_back), dtype=np.uint8)

    return img_back


def fft_remove_texture(img):
    # 手工制作一个mask, 低通，去除高频）
    mask = _create_mask(img.shape, k1=0.492, k2=0.49999999999999999999999999)
    return _jit_fft_remove_texture(img, mask)
