#!/usr/bin/env bash

# 添加环境变量
source ./tidb.env

# 添加到路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC_DIR="$ROOT_DIR/src"

# 通过src/cluster.py中Cluster类初始化haproxy的配置文件


# 重载haproxy服务
sudo cp haproxy.cfg /etc/haproxy/haproxy.cfg
sudo systemctl reload haproxy