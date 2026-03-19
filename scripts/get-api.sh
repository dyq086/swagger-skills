#!/usr/bin/env bash
# 获取指定接口的参数和返回值类型信息（对应 MCP getApi）
# 用法: ./get-api.sh <path> <method> [config_path]
# 示例: ./get-api.sh /api/channelType/list GET
# 依赖: curl, jq

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATH_ARG="${1:?用法: $0 <path> <method> [config_path]}"
METHOD="${2:?用法: $0 <path> <method> [config_path]}"
CONFIG="${3:-$SCRIPT_DIR/../swagger.config.json}"

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

METHOD_LOWER=$(echo "$METHOD" | tr '[:upper:]' '[:lower:]')

# 提取 operation 并解析 $ref
echo "$DOC" | jq -f "$SCRIPT_DIR/get-api.jq" --arg path "$PATH_ARG" --arg method "$METHOD_LOWER"
