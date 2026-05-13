#!/usr/bin/env bash
set -euo pipefail

# 添加到路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

sudo cp "$ROOT_DIR/haproxy.cfg" /etc/haproxy/haproxy.cfg
sudo systemctl reload haproxy