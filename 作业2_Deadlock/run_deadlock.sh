#!/bin/bash
set -e

# Unix/macOS 入口；实际测试逻辑在 Python 中，Windows/GitHub Actions 也可直接运行同一个脚本。
cd "$(dirname "$0")"

RUNS=${1:-100}
TIMEOUT_SEC=${2:-3}

if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
else
    PYTHON=python
fi

"$PYTHON" test_deadlock.py --runs "$RUNS" --timeout "$TIMEOUT_SEC" --log run.log
