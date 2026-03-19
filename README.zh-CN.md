[English](README.md) | [中文](README.zh-CN.md)

# Swagger Skills

通过 Python 脚本查询 Swagger/OpenAPI 文档，获取模块列表、接口列表及完整类型定义（含 `$ref` 解析）。

适用于 Cursor Skills、Codex Skills 或任何需要从 Swagger 文档获取 API schema 的场景。

## 依赖

- Python 3.9+

## 安装

```bash
# 克隆或复制到 skills 目录
# 项目级: .cursor/skills/swagger-skills/
# 全局: ~/.cursor/skills/swagger-skills/
git clone https://github.com/dyq086/swagger-skills.git .cursor/skills/swagger-skills
```

## 配置

复制配置模板并填写你的 Swagger 地址：

```bash
cp swagger.config.example.json swagger.config.json
```

编辑 `swagger.config.json`：

```json
{
  "swaggerUrl": "http://your-api/v3/api-docs",
  "token": "optional-auth-token"
}
```

## 脚本用法

| 脚本 | 说明 |
|------|------|
| `get-modules.py` | 获取所有模块（tags） |
| `get-apis.py <module>` | 获取指定模块下的接口列表 |
| `get-api.py <path> <method>` | 获取单个接口的完整 schema |

```bash
# 1. 查模块
python3 scripts/get-modules.py

# 2. 查某模块的接口
python3 scripts/get-apis.py 用户管理

# 3. 查单个接口详情
python3 scripts/get-api.py /api/user/list get
```

## 输出示例

**get-modules** → `[{name, description}, ...]`

**get-apis** → `[{path, method, summary}, ...]`

**get-api** → `{path, method, summary, parameters, requestBody, responseType, operation}`，其中 `requestBody` 和 `responseType` 已解析 `$ref` 为完整 schema。

## 提问示例

可通过以下方式触发（自然语言或关键词）：

**查模块列表**
- 查一下 swagger 里有哪些模块
- getModules
- 列出 OpenAPI 文档的所有 tags

**查某模块的接口**
- 用户模块下有哪些接口？
- getApis 用户管理
- 订单相关的 API 列表

**查单个接口详情**
- 查 `/api/user/list` 的 GET 接口
- getApi /api/user/list get
- 创建用户接口的请求参数和返回值是什么？
- `/api/order/{id}` 的 PUT 接口返回什么类型？

**组合查询**
- 先列出所有模块，再查用户模块的接口
- 查用户模块里删除接口的 schema

## License

MIT
