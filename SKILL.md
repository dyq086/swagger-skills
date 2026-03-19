---
name: swagger-skills
description: Queries Swagger/OpenAPI docs via Python scripts. Use when fetching API modules (tags), listing APIs by module, or getting full API schema (params, requestBody, responseType with $ref resolved). Trigger on swagger, OpenAPI, API docs, getModules, getApis, getApi, get-modules, get-apis, get-api, or API schema lookup.
---

# Swagger Skills

通过 Python 脚本查询 Swagger/OpenAPI 文档，获取模块列表、接口列表及完整类型定义。

**触发关键词**：swagger、OpenAPI、API 文档、getModules、getApis、getApi、get-modules、get-apis、get-api

## 前置依赖

- Python 3.9+

## 配置

在 skill 根目录的 `swagger.config.json` 中配置：

```json
{
  "swaggerUrl": "http://your-api/v3/api-docs",
  "token": "optional-auth-token"
}
```

脚本默认读取 `scripts/../swagger.config.json`，可传入可选参数指定配置路径。

## 脚本用法

### 1. get-modules.py — 获取所有模块

```bash
python3 scripts/get-modules.py [config_path]
```

输出：`[{name, description}, ...]`

### 2. get-apis.py — 获取某模块下的接口列表

```bash
python3 scripts/get-apis.py <module> [config_path]
```

示例：`python3 scripts/get-apis.py 用户管理`

输出：`[{path, method, summary}, ...]`

### 3. get-api.py — 获取单个接口的类型信息

```bash
python3 scripts/get-api.py <path> <method> [config_path]
```

示例：`python3 scripts/get-api.py /api/user/list get`

输出：`{path, method, summary, description, parameters, requestBody, responseType, operation}`

`requestBody` 和 `responseType` 会自动解析 `$ref`，展开为完整 schema（含 properties、items、allOf 等）。

## 使用流程

1. **查模块**：`get-modules.py` → 得到模块名
2. **查接口列表**：`get-apis.py <module>` → 得到 path + method
3. **查接口详情**：`get-api.py <path> <method>` → 得到参数、请求体、响应类型

## 错误处理

脚本失败时输出 `{"error": "..."}` 到 stderr，退出码非 0。解析配置或请求失败会直接报错。
