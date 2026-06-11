#!/usr/bin/env bash

# 添加环境变量
source ./tidb.env

# FLAGS: 部署选项
IDENTITY_FLAG="-i $KEY_SAVE_PATH"
CLUSTER_FLAG="--cluster"

# 检查指令
# tiup cluster check ${TOPOLOGY_FILE} ${IDENTITY_FLAG}
# 前置条件检查
tiup cluster check ${CLUSTER_NAME} ${SCALEOUT_FILE} ${CLUSTER_FLAG} ${IDENTITY_FLAG} --apply

# 部署
tiup cluster scale-out ${CLUSTER_NAME} ${SCALEOUT_FILE} ${IDENTITY_FLAG} -y