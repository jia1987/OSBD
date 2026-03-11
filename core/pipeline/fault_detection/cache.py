import numpy as np
from functools import cache


@cache
def cache_kenel(w, h) -> np.ndarray:
    return np.ones(shape=(h, w),dtype=np.uint8)
