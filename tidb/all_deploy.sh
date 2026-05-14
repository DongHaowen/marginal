#!/usr/bin/env bash

# 按照顺序依次执行以下脚本
# 0. sync.sh: 同步代码并安装python依赖
# 1. deploy.sh: 部署TiDB集群
# 2. haproxy.sh: 配置并重载haproxy服务
# 3. prepare.sh: 准备benchmark数据

# 参数设置
