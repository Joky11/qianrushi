#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
作业 1.2 综合加速测试

参考 https://github.com/riverzhou/PythonSpeedTest 的方案，针对作业 1.1 中的
计算 sqrt(i) + pow(i, 2) 进行多种优化：
    1. calc_py        : 标准 Python 循环（基线，对应 1.1 题目）
    2. calc_np        : NumPy 向量化（矩阵运算）
    3. calc_np_opt    : NumPy 向量化 + 用 i*i 代替 pow(i, 2)
    4. calc_jit       : Numba JIT 即时编译
    5. calc_aot       : Numba AOT 预编译模块
    6. calc_cy        : Cython 编译扩展
    7. calc_c         : ctypes 调用 C 动态库（O3 + ffast-math）
    8. calc_omp       : ctypes 调用 OpenMP 并行 C 动态库

为便于复现，所有原生扩展都通过同目录下的 build.sh 构建。
"""

import math
import os
import platform
import sys
from ctypes import c_int
from time import strftime, localtime
from timeit import timeit

import numpy as np
import numpy.ctypeslib as npct
from numba import njit

# 让脚本能加载 build/ 下的 .so 与 .dylib
HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, 'build')
sys.path.insert(0, BUILD)

# ------------------------------------------------------------
# 基础参数：与 PythonSpeedTest 保持一致的 5*5 配置
# ------------------------------------------------------------
LOOP = 5            # 外层循环次数（用于多次取平均）
SUBLOOP = 5         # 每次内部 timeit 的 number 参数
LENGTH = 1_000_000  # 数据规模
DATA = np.arange(LENGTH, dtype=np.int32)


# ------------------------------------------------------------
# 1) 标准 Python 循环：与作业 1.1 等价的基线
# ------------------------------------------------------------
def calc_py(d):
    n = d.size
    out = np.empty(n, dtype=np.float64)
    for i in range(n):
        v = int(d[i])
        out[i] = math.sqrt(v) + math.pow(v, 2)
    return out


# ------------------------------------------------------------
# 2) NumPy 向量化（最直接的"矩阵化"思路）
# ------------------------------------------------------------
def calc_np(d):
    v = d.astype(np.float64)
    return np.sqrt(v) + np.power(v, 2)


# ------------------------------------------------------------
# 3) NumPy 优化版：用 v*v 替代 power(v, 2)
# ------------------------------------------------------------
def calc_np_opt(d):
    v = d.astype(np.float64)
    return np.sqrt(v) + v * v


# ------------------------------------------------------------
# 4) Numba JIT
# ------------------------------------------------------------
@njit(cache=True)
def calc_jit(d):
    n = d.shape[0]
    out = np.empty(n, dtype=np.float64)
    for i in range(n):
        v = float(d[i])
        out[i] = math.sqrt(v) + v * v
    return out


# ------------------------------------------------------------
# 5) Numba AOT：在 build/ 下，由 src/calc_aot.py 预先编译
# ------------------------------------------------------------
from calc_aot import calc_aot as _calc_aot  # noqa: E402


def calc_aot(d):
    return _calc_aot(d)


# ------------------------------------------------------------
# 6) Cython 编译扩展
# ------------------------------------------------------------
from calc_cy import calc_cy as _calc_cy  # noqa: E402


def calc_cy(d):
    return _calc_cy(d)


# ------------------------------------------------------------
# 7) ctypes 调用 C 动态库
# ------------------------------------------------------------
_lib_c = npct.load_library('libcalc_c', BUILD)
_lib_c.calc_c.argtypes = [
    npct.ndpointer(dtype=np.int32, ndim=1, flags='C_CONTIGUOUS'),
    npct.ndpointer(dtype=np.float64, ndim=1, flags='C_CONTIGUOUS'),
    c_int,
]
_lib_c.calc_c.restype = None


def calc_c(d):
    out = np.empty(d.size, dtype=np.float64)
    _lib_c.calc_c(d, out, d.size)
    return out


# ------------------------------------------------------------
# 8) ctypes + OpenMP 并行
# ------------------------------------------------------------
_lib_omp = npct.load_library('libcalc_omp', BUILD)
_lib_omp.calc_omp.argtypes = [
    npct.ndpointer(dtype=np.int32, ndim=1, flags='C_CONTIGUOUS'),
    npct.ndpointer(dtype=np.float64, ndim=1, flags='C_CONTIGUOUS'),
    c_int,
]
_lib_omp.calc_omp.restype = None


def calc_omp(d):
    out = np.empty(d.size, dtype=np.float64)
    _lib_omp.calc_omp(d, out, d.size)
    return out


# ------------------------------------------------------------
# 测试集合（顺序对应输出表的顺序）
# ------------------------------------------------------------
TESTS = [
    ('calc_py',     'Standard Python Loop'),
    ('calc_np',     'NumPy Vectorized'),
    ('calc_np_opt', 'NumPy Optimized (i*i)'),
    ('calc_jit',    'Numba JIT'),
    ('calc_aot',    'Numba AOT'),
    ('calc_cy',     'Cython Module'),
    ('calc_c',      'C Module (clang -O3)'),
    ('calc_omp',    'C Module + OpenMP'),
]


def check_results():
    """对比所有实现的结果，确保一致"""
    # Python 基线对 100 万数据太慢了，这里用前 1 万做正确性校验
    small = DATA[:10000]
    ref = calc_np_opt(small)
    funcs = dict(globals())
    for name, _ in TESTS:
        fn = funcs[name]
        out = fn(small)
        if not np.allclose(out, ref, rtol=1e-9, atol=1e-6):
            diff = np.max(np.abs(out - ref))
            raise RuntimeError(f'{name} 结果不一致，最大差值 = {diff}')
    print('结果一致性检查：通过')


def get_sys_info():
    info = {}
    info['OS'] = f'{platform.system()} {platform.release()} ({platform.machine()})'
    info['CPU'] = platform.processor() or platform.machine()
    info['CPU Threads'] = str(os.cpu_count())
    info['Python'] = sys.version.split()[0]
    info['NumPy'] = np.__version__
    try:
        import numba
        info['Numba'] = numba.__version__
    except Exception:
        info['Numba'] = 'N/A'
    try:
        import Cython
        info['Cython'] = Cython.__version__
    except Exception:
        info['Cython'] = 'N/A'
    info['TIME'] = strftime('%Y-%m-%d %H:%M:%S', localtime())
    return info


def get_test_info():
    return {
        'Loop Number': f'{LOOP} * {SUBLOOP}',
        'Data Size': f'{LENGTH:,}',
        'Data Type': str(DATA.dtype),
        'Operation': 'sqrt(i) + i**2',
    }


def render_markdown(result):
    out = []

    # System Information
    out.append('###### System Information')
    out.append('| | |')
    out.append('|:---|:---|')
    for k, v in get_sys_info().items():
        out.append(f'| {k} | {v} |')
    out.append('')

    # Test Information
    out.append('###### Test Information')
    out.append('| | |')
    out.append('|:---|:---|')
    for k, v in get_test_info().items():
        out.append(f'| {k} | {v} |')
    out.append('')

    # Test Result
    out.append('###### Test Result')
    header = '| Name | Information ' + ''.join(f'| {i + 1} ' for i in range(LOOP)) + '| Avg | Faster |'
    sep = '|:---|:---:' + '|---:' * (LOOP + 2) + '|'
    out.append(header)
    out.append(sep)
    for name, info in TESTS:
        row = result[name]  # [info, t1, ..., tL, avg, faster]
        cells = [name, info] + [f'{x:.3f}' for x in row[1:]]
        out.append('| ' + ' | '.join(cells) + ' |')
    out.append('')
    return '\n'.join(out)


def main():
    print('==> 一致性检查')
    check_results()

    # 结果字典：name -> [info, t1..tL, avg, faster]
    result = {name: [info] for name, info in TESTS}

    print('\n==> 开始计时（每项跑 LOOP={} 轮，每轮 SUBLOOP={} 次）'.format(LOOP, SUBLOOP))
    setup_lines = [f'from __main__ import {name}' for name, _ in TESTS]
    setup_lines.append('from __main__ import DATA')
    setup = '\n'.join(setup_lines)

    for r in range(LOOP):
        print(f'\n--- 第 {r + 1} 轮 ---')
        for name, _ in TESTS:
            cmd = f'{name}(DATA)'
            t = timeit(cmd, setup=setup, number=SUBLOOP)
            result[name].append(t)
            print(f'  {name:<12s} : {t:.4f} s')

    # 计算平均值与加速比（以 calc_py 为基准）
    base_avg = sum(result['calc_py'][1:]) / LOOP
    for name, _ in TESTS:
        avg = sum(result[name][1:]) / LOOP
        result[name].append(avg)
        result[name].append(base_avg / avg)

    # 输出 Markdown 报告
    md = render_markdown(result)
    out_path = os.path.join(HERE, 'Result.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f'\n==> 结果已写入 {out_path}')
    print('\n' + md)


if __name__ == '__main__':
    main()
