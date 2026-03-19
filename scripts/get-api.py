#!/usr/bin/env python3
"""获取指定接口的参数和返回值类型信息（对应 MCP getApi）"""

import argparse
import copy
import json
import sys
from pathlib import Path

import urllib.request


def extract_ref_name(ref: str) -> str | None:
    if not isinstance(ref, str):
        return None
    if ref.startswith("#/components/schemas/") or ref.startswith("#/definitions/"):
        return ref.split("/")[-1]
    return ref


def get_schema(doc: dict, name: str) -> dict | None:
    schemas = doc.get("components", {}).get("schemas") or doc.get("definitions") or {}
    return schemas.get(name)


def resolve_schema(doc: dict, obj: dict | None, visited: set[str]) -> dict | None:
    if obj is None:
        return None
    obj = copy.deepcopy(obj)

    ref = obj.get("$ref")
    if ref:
        name = extract_ref_name(ref)
        if name and name in visited:
            return {"$ref": ref, "_circular": True}
        resolved = get_schema(doc, name) if name else None
        if resolved is None:
            return obj
        visited.add(name)
        result = resolve_schema(doc, resolved, visited)
        visited.discard(name)
        return result

    original_ref = obj.get("originalRef")
    if original_ref:
        name = extract_ref_name(original_ref)
        if name and name in visited:
            return {"originalRef": original_ref, "_circular": True}
        resolved = get_schema(doc, name) if name else None
        if resolved is None:
            return obj
        visited.add(name)
        result = resolve_schema(doc, resolved, visited)
        visited.discard(name)
        return result

    if "properties" in obj:
        obj["properties"] = {
            k: resolve_schema(doc, v, visited)
            for k, v in obj["properties"].items()
        }
    if "items" in obj:
        obj["items"] = resolve_schema(doc, obj["items"], visited)
    if "allOf" in obj:
        obj["allOf"] = [resolve_schema(doc, x, visited) for x in obj["allOf"]]

    return obj


def get_req_schema(op: dict) -> dict | None:
    rb = op.get("requestBody", {}) or {}
    content = rb.get("content") or {}
    if "application/json" in content:
        return content["application/json"].get("schema")
    if "*/*" in content:
        return content["*/*"].get("schema")
    for v in content.values():
        if isinstance(v, dict) and "schema" in v:
            return v.get("schema")
    params = op.get("parameters") or []
    for p in params:
        if isinstance(p, dict) and p.get("in") == "body" and "schema" in p:
            return p.get("schema")
    return None


def get_resp_schema(op: dict) -> dict | None:
    responses = op.get("responses") or {}
    r200 = responses.get("200") or {}
    if isinstance(r200, dict):
        content = r200.get("content") or {}
        if "application/json" in content:
            return content["application/json"].get("schema")
        if "*/*" in content:
            return content["*/*"].get("schema")
        for v in content.values():
            if isinstance(v, dict) and "schema" in v:
                return v.get("schema")
        if "schema" in r200:
            return r200.get("schema")
    return None


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
    parser = argparse.ArgumentParser(description="获取指定接口详情")
    parser.add_argument("path", help="API path，如 /api/channelType/list")
    parser.add_argument("method", help="HTTP method，如 GET")
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
    path_arg = args.path
    method_lower = args.method.lower()

    paths = doc.get("paths") or {}
    path_item = paths.get(path_arg)
    if not path_item:
        print(json.dumps({"error": f"API not found: {args.method.upper()} {path_arg}"}), file=sys.stderr)
        sys.exit(1)

    op = path_item.get(method_lower)
    if not op:
        print(json.dumps({"error": f"API not found: {args.method.upper()} {path_arg}"}), file=sys.stderr)
        sys.exit(1)

    req_raw = get_req_schema(op)
    resp_raw = get_resp_schema(op)
    req_body = resolve_schema(doc, req_raw, set()) if req_raw else None
    resp_type = resolve_schema(doc, resp_raw, set()) if resp_raw else None

    result = {
        "path": path_arg,
        "method": args.method.upper(),
        "summary": op.get("summary"),
        "description": op.get("description"),
        "parameters": op.get("parameters"),
        "requestBody": req_body,
        "responseType": resp_type,
        "operation": op,
    }
    print(json.dumps(result, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
