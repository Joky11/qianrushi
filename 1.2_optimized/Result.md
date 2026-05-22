###### System Information
| | |
|:---|:---|
| OS | Darwin 25.2.0 (arm64) |
| CPU | arm |
| CPU Threads | 10 |
| Python | 3.9.7 |
| NumPy | 2.0.2 |
| Numba | 0.60.0 |
| Cython | 3.2.4 |
| TIME | 2026-05-18 09:58:28 |

###### Test Information
| | |
|:---|:---|
| Loop Number | 5 * 5 |
| Data Size | 1,000,000 |
| Data Type | int32 |
| Operation | sqrt(i) + i**2 |

###### Test Result
| Name | Information | 1 | 2 | 3 | 4 | 5 | Avg | Faster |
|:---|:---:|---:|---:|---:|---:|---:|---:|---:|
| calc_py | Standard Python Loop | 0.857 | 0.850 | 0.849 | 0.851 | 0.940 | 0.870 | 1.000 |
| calc_np | NumPy Vectorized | 0.040 | 0.034 | 0.036 | 0.034 | 0.036 | 0.036 | 24.297 |
| calc_np_opt | NumPy Optimized (i*i) | 0.020 | 0.011 | 0.010 | 0.009 | 0.009 | 0.012 | 73.253 |
| calc_jit | Numba JIT | 0.004 | 0.003 | 0.004 | 0.003 | 0.003 | 0.003 | 255.008 |
| calc_aot | Numba AOT | 0.006 | 0.005 | 0.005 | 0.005 | 0.005 | 0.005 | 169.577 |
| calc_cy | Cython Module | 0.005 | 0.004 | 0.005 | 0.004 | 0.004 | 0.005 | 192.657 |
| calc_c | C Module (clang -O3) | 0.003 | 0.003 | 0.003 | 0.003 | 0.006 | 0.004 | 232.779 |
| calc_omp | C Module + OpenMP | 0.002 | 0.002 | 0.002 | 0.004 | 0.005 | 0.003 | 302.218 |
