#!/usr/bin/env bash

# 添加环境变量
source ./tidb.env

IDENTITY_FLAG="-i $KEY_SAVE_PATH"

# tiup cluster check ${TOPOLOGY_FILE} ${IDENTITY_FLAG}
# 前置条件检查
tiup cluster check ${TOPOLOGY_FILE} ${IDENTITY_FLAG} --apply

# 部署
tiup cluster deploy ${CLUSTER_NAME} ${CLUSTER_VERSION} ${TOPOLOGY_FILE} ${IDENTITY_FLAG}  

# 启动
tiup cluster start ${CLUSTER_NAME}