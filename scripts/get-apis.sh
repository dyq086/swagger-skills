#!/usr/bin/env bash
# 获取指定模块下的所有接口列表（对应 MCP getApis）
# 用法: ./get-apis.sh <module> [config_path]
# 依赖: curl, jq

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODULE="${1:?用法: $0 <module> [config_path]}"
CONFIG="${2:-$SCRIPT_DIR/../swagger.config.json}"

if [[ ! -f "$CONFIG" ]]; then
  echo '{"error": "配置文件不存在"}' >&2
  exit 1
fi

SWAGGER_URL=$(jq -r '.swaggerUrl // empty' "$CONFIG")
TOKEN=$(jq -r '.token // empty' "$CONFIG")

if [[ -z "$SWAGGER_URL" ]]; then
  echo '{"error": "swaggerUrl 未配置"}' >&2
  exit 1
fi

CURL_OPTS=(-sS -f -L)
[[ -n "$TOKEN" ]] && CURL_OPTS+=(-H "Authorization: $TOKEN")

DOC=$(curl "${CURL_OPTS[@]}" "$SWAGGER_URL") || {
  echo "{\"error\": \"请求 Swagger 文档失败\"}" >&2
  exit 1
}

# 遍历 paths，筛选 tags 包含 module 的 operation
echo "$DOC" | jq --arg m "$MODULE" '
  [.paths // {} | to_entries[] | .key as $path | .value | to_entries[] |
    select(.key | test("^(get|post|put|delete|patch|options|head)$"; "i")) |
    select(.value.tags? and (.value.tags | index($m))) |
    {path: $path, method: (.key | ascii_upcase), summary: (.value.summary // "")}]
'
