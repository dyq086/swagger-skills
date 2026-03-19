#!/usr/bin/env python3
"""获取 Swagger API 的所有模块列表（对应 MCP getModules）"""

import argparse
import json
import sys
from pathlib import Path

import urllib.request


def load_config(config_path: Path) -> dict:
    if not config_path.exists():
        print('{"error": "配置文件不存在，请提供 swagger.config.json 路径"}', file=sys.stderr)
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
        print(json.dumps({"error": f"请求 Swagger 文档失败: {url}", "detail": str(e)}), file=sys.stderr)
        sys.exit(1)


def main():
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="获取 Swagger 模块列表")
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
    tags = doc.get("tags") or []
    result = [{"name": t.get("name", ""), "description": t.get("description", "")} for t in tags]
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
