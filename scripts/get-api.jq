# get-api.jq - 提取 API 详情并解析 $ref
# 用法: jq -f get-api.jq --arg path "$path" --arg method "$method"

def extract_ref_name:
  if type == "string" then
    if startswith("#/components/schemas/") then split("/") | last
    elif startswith("#/definitions/") then split("/") | last
    else . end
  else null end;

def get_schema($doc; $name): $doc.components.schemas[$name] // $doc.definitions[$name];

def resolve_schema($doc; $visited):
  if . == null then null
  elif .["$ref"] then
    (.["$ref"] | extract_ref_name) as $name |
    if $visited | index($name) then {"$ref": (.["$ref"]), "_circular": true}
    else (get_schema($doc; $name)) as $resolved |
      if $resolved == null then .
      else ($resolved | resolve_schema($doc; $visited + [$name]))
      end
    end
  elif .originalRef then
    (.originalRef | extract_ref_name) as $name |
    if $visited | index($name) then {"originalRef": .originalRef, "_circular": true}
    else (get_schema($doc; $name)) as $resolved |
      if $resolved == null then .
      else ($resolved | resolve_schema($doc; $visited + [$name]))
      end
    end
  elif .properties then
    .properties |= (to_entries | map(.value |= resolve_schema($doc; $visited)) | from_entries)
  elif .items then
    .items |= resolve_schema($doc; $visited)
  elif .allOf then
    .allOf |= map(resolve_schema($doc; $visited))
  else . end;

def get_req_schema:
  .requestBody.content["application/json"].schema // .requestBody.content["*/*"].schema // (.requestBody.content | (to_entries[0].value.schema // empty)) // (.parameters | map(select(.in == "body"))[0].schema) // null;

def get_resp_schema:
  .responses["200"].content["application/json"].schema // .responses["200"].content["*/*"].schema // (.responses["200"].content | (to_entries[0].value.schema // empty)) // .responses["200"].schema // null;

. as $doc |
$doc.paths[$path][$method] as $op |
if $op == null then
  {error: ("API not found: " + ($method | ascii_upcase) + " " + $path)}
else
  ($op | get_req_schema) as $reqRaw |
  ($op | get_resp_schema) as $respRaw |
  ($reqRaw | if . != null then resolve_schema($doc; []) else null end) as $reqBody |
  ($respRaw | if . != null then resolve_schema($doc; []) else null end) as $respType |
  {
    path: $path,
    method: ($method | ascii_upcase),
    summary: $op.summary,
    description: $op.description,
    parameters: $op.parameters,
    requestBody: $reqBody,
    responseType: $respType,
    operation: $op
  }
end
