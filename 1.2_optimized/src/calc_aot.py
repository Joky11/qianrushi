# Numba AOT 预编译模块
# 对应原 PythonSpeedTest 项目里的 Numba AOT 方案
# 运行本脚本可生成 calc_aot 扩展模块（.so/.pyd）

import numpy as np
from numba.pycc import CC

cc = CC('calc_aot')
cc.verbose = True


@cc.export('calc_aot', 'f8[:](i4[:])')
def calc_aot(data):
    n = data.shape[0]
    out = np.empty(n, dtype=np.float64)
    for i in range(n):
        v = float(data[i])
        out[i] = np.sqrt(v) + v * v
    return out


if __name__ == '__main__':
    cc.compile()
