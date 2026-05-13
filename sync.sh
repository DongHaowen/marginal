#!/usr/bin/env bash

# 添加环境变量
source ./tidb.env

# 添加到路径
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# git同步
git pull

# 安装python依赖
if [[ -f "$ROOT_DIR/requirements.txt" ]]; then
    if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
        "$ROOT_DIR/.venv/bin/python" -m pip install -r "$ROOT_DIR/requirements.txt"
    else
        "${python_cmd:-python3}" -m pip install -r "$ROOT_DIR/requirements.txt"
    fi
fi
