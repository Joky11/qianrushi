# Cython 模块：对每个 i 计算 sqrt(i) + i*i
# 对应原 PythonSpeedTest 项目里的 Cython Module 方案

# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True

import numpy as np
cimport numpy as np
from libc.math cimport sqrt

def calc_cy(np.ndarray[np.int32_t, ndim=1] data):
    cdef Py_ssize_t n = data.shape[0]
    cdef np.ndarray[np.float64_t, ndim=1] out = np.empty(n, dtype=np.float64)
    cdef Py_ssize_t i
    cdef double v
    for i in range(n):
        v = <double>data[i]
        out[i] = sqrt(v) + v * v
    return out
