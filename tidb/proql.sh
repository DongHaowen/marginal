#!/usr/bin/env bash
set -euo pipefail

PROM_URL="http://127.0.0.1:9090/api/v1/query"

if [[ $# -lt 1 ]]; then
	echo "Usage: $0 '<promql_query>'" >&2
	exit 1
fi

# Allow passing the query either as a single quoted string or multiple words.
QUERY="$*"

curl -sS -G "$PROM_URL" --data-urlencode "query=$QUERY"
echo

# Example PromQL Query
# 查询 TiDB 每秒执行的 SQL 语句数量
# sum(rate(tidb_server_query_total[1m])) by (instance)
