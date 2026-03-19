#!/usr/bin/env bash
# 获取 Swagger API 的所有模块列表（对应 MCP getModules）
# 依赖: curl, jq

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="${1:-$SCRIPT_DIR/../swagger.config.json}"

if [[ ! -f "$CONFIG" ]]; then
  echo '{"error": "配置文件不存在，请提供 swagger.config.json 路径"}' >&2
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
  echo "{\"error\": \"请求 Swagger 文档失败: $SWAGGER_URL\"}" >&2
  exit 1
}

echo "$DOC" | jq '.tags // [] | map({name: .name, description: (.description // "")})'
