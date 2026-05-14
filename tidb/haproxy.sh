#!/usr/bin/env bash

# 添加环境变量
source ./tidb.env

# 运行src/cluster.py进行初始化
"$PYTHON_CMD" "$SRC_DIR/cluster.py"

# 重载haproxy服务
sudo cp haproxy.cfg /etc/haproxy/haproxy.cfg
sudo systemctl reload haproxy