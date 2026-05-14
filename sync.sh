#!/usr/bin/env bash

# 添加环境变量
source ./tidb.env

# git同步
git pull

# 安装python依赖
"$PYTHON_CMD" -m pip install -r "$ROOT_DIR/requirements.txt"
