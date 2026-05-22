#!/usr/bin/env bash
# 一键构建：C 动态库（普通 + OpenMP）、Cython 模块、Numba AOT 模块
set -e

PY=/opt/miniconda3/bin/python
HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="$HERE/src"
OUT="$HERE/build"
mkdir -p "$OUT"

echo "==> [1/4] 编译普通 C 动态库 calc_c"
clang -O3 -ffast-math -shared -fPIC \
    "$SRC/calc_c.c" -o "$OUT/libcalc_c.dylib"

echo "==> [2/4] 编译 OpenMP 并行 C 动态库 calc_omp"
LIBOMP=/opt/homebrew/opt/libomp
clang -O3 -ffast-math -shared -fPIC \
    -Xpreprocessor -fopenmp -I"$LIBOMP/include" \
    "$SRC/calc_omp.c" -o "$OUT/libcalc_omp.dylib" \
    -L"$LIBOMP/lib" -lomp

echo "==> [3/4] 编译 Cython 模块 calc_cy"
"$PY" -m cython -3 "$SRC/calc_cy.pyx" -o "$OUT/calc_cy.c"
NUMPY_INC="$($PY -c 'import numpy; print(numpy.get_include())')"
PY_INC="$($PY -c 'import sysconfig; print(sysconfig.get_path("include"))')"
PY_LDLIB="$($PY -c 'import sysconfig; print(sysconfig.get_config_var("LIBDIR"))')"
EXT_SUFFIX="$($PY -c 'import sysconfig; print(sysconfig.get_config_var("EXT_SUFFIX"))')"
clang -O3 -ffast-math -shared -fPIC \
    -I"$PY_INC" -I"$NUMPY_INC" \
    "$OUT/calc_cy.c" -o "$OUT/calc_cy${EXT_SUFFIX}" \
    -L"$PY_LDLIB" -undefined dynamic_lookup

echo "==> [4/4] 生成 Numba AOT 模块 calc_aot"
# numba.pycc 会把产物输出到 calc_aot.py 所在目录，构建后再统一拷贝到 build 目录
"$PY" "$SRC/calc_aot.py"
mv "$SRC"/calc_aot*.so "$OUT"/ 2>/dev/null || true

echo "==> 构建完成，产物位于 $OUT"
ls -la "$OUT"
