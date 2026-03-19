#!/usr/bin/env python3
"""获取指定模块下的所有接口列表（对应 MCP getApis）"""

import argparse
import json
import sys
from pathlib import Path

import urllib.request

HTTP_METHODS = frozenset({"get", "post", "put", "delete", "patch", "options", "head"})


def load_config(config_path: Path) -> dict:
    if not config_path.exists():
        print('{"error": "配置文件不存在"}', file=sys.stderr)
        sys.exit(1)
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


def fetch_swagger(url: str, token: str | None) -> dict:
    req = urllib.request.Request(url)
    if token:
        req.add_header("Authorization", token)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except Exception as e:
        print(json.dumps({"error": "请求 Swagger 文档失败", "detail": str(e)}), file=sys.stderr)
        sys.exit(1)


def main():
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="获取指定模块下的接口列表")
    parser.add_argument("module", help="模块名")
    parser.add_argument("config", nargs="?", default=script_dir.parent / "swagger.config.json", help="配置文件路径")
    args = parser.parse_args()
    config_path = Path(args.config)

    cfg = load_config(config_path)
    swagger_url = cfg.get("swaggerUrl")
    token = cfg.get("token") or None

    if not swagger_url:
        print('{"error": "swaggerUrl 未配置"}', file=sys.stderr)
        sys.exit(1)

    doc = fetch_swagger(swagger_url, token)
    paths = doc.get("paths") or {}
    result = []

    for path_str, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        for method, op in path_item.items():
            if method.lower() not in HTTP_METHODS:
                continue
            tags = op.get("tags") or []
            if args.module not in tags:
                continue
            result.append({
                "path": path_str,
                "method": method.upper(),
                "summary": op.get("summary", ""),
            })

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
