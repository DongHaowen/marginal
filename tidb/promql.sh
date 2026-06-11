#!/usr/bin/env bash
set -euo pipefail

PROM_URL="http://127.0.0.1:9090/api/v1/query"

if [[ $# -lt 1 ]]; then
	echo "Usage: $0 '<promql_query>'" >&2
	exit 1
fi

# Allow passing the query either as a single quoted string or multiple words.
QUERY="$*"

RESPONSE="$(curl -sS -G "$PROM_URL" --data-urlencode "query=$QUERY")"

if command -v jq >/dev/null 2>&1; then
	echo "$RESPONSE" | jq .
elif command -v python3 >/dev/null 2>&1; then
	echo "$RESPONSE" | python3 -m json.tool
else
	echo "$RESPONSE"
	echo "Warning: jq/python3 not found, output is not pretty-printed." >&2
fi

# Example PromQL Query
# 查询 TiDB 每秒执行的 SQL 语句数量
# sum(rate(tidb_server_query_total[1m])) by (instance)
