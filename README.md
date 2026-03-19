[English](README.md) | [中文](README.zh-CN.md)

# Swagger Skills

Query Swagger/OpenAPI docs via shell scripts to get module list, API list, and full type definitions (including `$ref` resolution).

For Cursor Skills, Codex Skills, or any scenario that needs API schema from Swagger docs.

## Dependencies

- `curl`
- `jq` (1.6+)

## Installation

```bash
# Clone or copy to skills directory
# Project-level: .cursor/skills/swagger-skills/
# Global: ~/.cursor/skills/swagger-skills/
git clone https://github.com/dyq086/swagger-skills.git .cursor/skills/swagger-skills
```

## Configuration

Copy the config template and fill in your Swagger URL:

```bash
cp swagger.config.example.json swagger.config.json
```

Edit `swagger.config.json`:

```json
{
  "swaggerUrl": "http://your-api/v3/api-docs",
  "token": "optional-auth-token"
}
```

## Script Usage

| Script | Description |
|--------|-------------|
| `get-modules.sh` | Get all modules (tags) |
| `get-apis.sh <module>` | Get API list for a module |
| `get-api.sh <path> <method>` | Get full schema for a single API |

```bash
# 1. List modules
./scripts/get-modules.sh

# 2. List APIs in a module
./scripts/get-apis.sh 用户管理

# 3. Get single API details
./scripts/get-api.sh /api/user/list get
```

## Output Examples

**get-modules** → `[{name, description}, ...]`

**get-apis** → `[{path, method, summary}, ...]`

**get-api** → `{path, method, summary, parameters, requestBody, responseType, operation}` — `requestBody` and `responseType` have `$ref` resolved to full schema.

## Query Examples

Trigger with natural language or keywords:

**List modules**
- What modules are in swagger?
- getModules
- List all tags from OpenAPI docs

**List APIs in a module**
- What APIs are in the user module?
- getApis 用户管理
- List order-related APIs

**Get single API details**
- Get the GET API for `/api/user/list`
- getApi /api/user/list get
- What are the request params and return type for the create user API?
- What does the PUT `/api/order/{id}` return?

**Combined queries**
- List all modules, then get APIs for the user module
- Get the schema for the delete API in the user module

## License

MIT
