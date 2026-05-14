#!/usr/bin/env bash

# 添加环境变量
source ./tidb.env

# 设置基本参数
"$MYSQL_CMD" -e "set global tidb_analyze_column_options='ALL';"

# TPC-C数据准备
TPCC_WAREHOUSES=1
TPCC_PARTS=1
tiup bench tpcc --warehouses $TPCC_WAREHOUSES --parts $TPCC_PARTS prepare

# TPC-H数据准备
TPCH_SF=1
tiup bench tpch --sf $TPCH_SF prepare

# CH Benchmark数据准备
CH_WAREHOUSES=1
tiup bench ch prepare --warehouses $CH_WAREHOUSES