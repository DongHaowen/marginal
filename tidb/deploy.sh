#!/usr/bin/env bash

# 添加环境变量
source ./tidb.env

# FLAGS: 部署选项
IDENTITY_FLAG="-i $KEY_SAVE_PATH"

# 检查指令
# tiup cluster check ${TOPOLOGY_FILE} ${IDENTITY_FLAG}
# 前置条件检查
tiup cluster check ${TOPOLOGY_FILE} ${IDENTITY_FLAG} --apply

# 部署
tiup cluster deploy ${CLUSTER_NAME} ${CLUSTER_VERSION} ${TOPOLOGY_FILE} ${IDENTITY_FLAG} -y

# 启动
tiup cluster start ${CLUSTER_NAME}