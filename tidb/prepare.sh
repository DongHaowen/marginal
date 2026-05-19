#!/usr/bin/env bash

# 添加环境变量
source ./tidb.env

# 安装前置工具
tiup install tidb-lightning

# 所有的数据准备工作都需要判断数据规模
# 现在目前仅考虑所有数据均使用lightning导入的情况

# 设置基本参数
"$MYSQL_CMD" -e "set global tidb_analyze_column_options='ALL';"

# 全局参数
PREPARE_THREADS=32

# TPC-C数据准备
TPCC_DATABASE=tpcc
TPCC_WAREHOUSES=1
TPCC_PARTS=1
 
tiup bench tpcc prepare \ 
  --warehouses $TPCC_WAREHOUSES --parts $TPCC_PARTS 

# TPC-H数据准备
TPCH_DATABASE=tpch
TPCH_SF=1

tiup bench tpch prepare \
  --sf $TPCH_SF --threads $PREPARE_THREADS 


# CH Benchmark数据准备
CH_WAREHOUSES=1
tiup bench ch prepare \
  --warehouses $CH_WAREHOUSES  --threads $PREPARE_THREADS 