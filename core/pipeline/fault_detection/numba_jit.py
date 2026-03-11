from numba import jit
import numpy as np


@jit(nopython=True)
def multiplicate(a, b):
    return a * b


@jit(nopython=True)
def add(a, b):
    return a + b


@jit(nopython=True)
def sum(a):
    return np.sum(a)


@jit(nopython=True)
def abs(a):
    return np.abs(a)


@jit(nopython=True)
def astype(a, dtype):
    return a.astype(dtype)


@jit(nopython=True)
def setter(a, b):
    a[:] = b[:]
