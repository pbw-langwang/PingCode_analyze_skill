# PingCode REST API Reference

Base URL: `https://api.pingcode.com`（私有部署替换为自定义域名）

## Authentication

### Personal Access Token (PAT)

在 PingCode 个人设置中生成 API 令牌，请求时通过 Header 传递：

```
Authorization: Bearer {token}
```

### OAuth2.0

适用于第三方应用集成，支持 Authorization Code Grant 流程：

1. 重定向用户到授权页面
2. 用户授权后获取 authorization_code
3. 用 code 换取 access_token
4. 用 access_token 调用 API

---

## Common Response Format

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

分页响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "per_page": 20
  }
}
```

### Pagination Parameters

| 参数     | 类型 | 默认值 | 说明               |
| -------- | ---- | ------ | ------------------ |
| page     | int  | 1      | 页码               |
| per_page | int  | 20     | 每页数量，最大 100 |

---

## User API

### Get Current User Info

验证 Token 有效性的首选接口。

```
GET /v1/user/me
```

**Response:**

```json
{
  "code": 200,
  "data": {
    "id": "user_xxx",
    "name": "张三",
    "email": "zhangsan@example.com",
    "avatar": "https://..."
  }
}
```

---

## Project API

### List Projects

```
GET /v1/projects
```

**Query Parameters:**

| 参数     | 类型   | 说明                     |
| -------- | ------ | ------------------------ |
| page     | int    | 页码                     |
| per_page | int    | 每页数量                 |
| type     | string | 项目类型：scrum / kanban |

**Response:**

```json
{
  "code": 200,
  "data": {
    "items": [
      {
        "id": "proj_xxx",
        "name": "电商平台",
        "identifier": "EC",
        "type": "scrum",
        "status": "active",
        "created_at": "2025-01-15T08:00:00Z",
        "updated_at": "2025-05-14T10:30:00Z"
      }
    ],
    "total": 5
  }
}
```

### Get Project Detail

```
GET /v1/projects/{project_id}
```

### Get Project Members

```
GET /v1/projects/{project_id}/members
```

**Response:**

```json
{
  "code": 200,
  "data": {
    "items": [
      {
        "id": "member_xxx",
        "user_id": "user_xxx",
        "name": "张三",
        "role": "developer",
        "email": "zhangsan@example.com"
      }
    ]
  }
}
```

---

## Iteration API

### List Iterations (Sprints)

实际端点（已验证）：

```
GET /v1/project/projects/{project_id}/sprints
```

**Query Parameters:**

| 参数       | 类型 | 说明              |
| ---------- | ---- | ----------------- |
| page_size  | int  | 每页数量，最大100 |
| page_index | int  | 页码，从0开始     |

**Response:**

```json
{
  "values": [
    {
      "id": "69faaad4dd01a730f1c37b73",
      "name": "2.1.0（5.12-5.18）",
      "status": "in_progress",
      "start_at": 1747008000,
      "end_at": 1747526399
    }
  ],
  "total": 18
}
```

**字段说明：**

| 字段     | 类型   | 说明                                        |
| -------- | ------ | ------------------------------------------- |
| id       | string | 迭代ID，用于工作项的 sprint_id 过滤         |
| name     | string | 迭代名称（如 "2.1.0（5.12-5.18）"）         |
| status   | string | 迭代状态：in_progress / completed / pending |
| start_at | int    | 开始时间（Unix时间戳）                      |
| end_at   | int    | 结束时间（Unix时间戳）                      |

### Get Iteration Detail

```
GET /v1/projects/{project_id}/iterations/{iteration_id}
```

### Get Iteration Burndown

```
GET /v1/projects/{project_id}/iterations/{iteration_id}/burndown
```

**Response:**

```json
{
  "code": 200,
  "data": {
    "ideal_line": [
      { "date": "2025-05-01", "remaining": 50 },
      { "date": "2025-05-02", "remaining": 46.4 }
    ],
    "actual_line": [
      { "date": "2025-05-01", "remaining": 50 },
      { "date": "2025-05-02", "remaining": 48 }
    ],
    "unit": "story_point"
  }
}
```

---

## Work Item API

### List Work Items

实际端点（已验证）：

```
GET /v1/project/work_items
```

**Query Parameters:**

| 参数       | 类型   | 说明                                            |
| ---------- | ------ | ----------------------------------------------- |
| project_id | string | **必填**，项目ID                                |
| type       | string | 工作项类型：story / task / bug / epic / feature |
| sprint_id  | string | 迭代ID，通过迭代列表接口获取                    |
| page_size  | int    | 每页数量，最大100                               |
| page_index | int    | 页码，从0开始                                   |

**重要说明：**

- `type` 和 `sprint_id` 参数已在实际API中验证可用，可大幅减少数据拉取量
- API 不支持日期范围过滤参数，日期过滤需在客户端实现
- `type` 参数只接受单个值，如需多种类型需分别请求后合并

**Response:**

```json
{
  "code": 200,
  "data": {
    "items": [
      {
        "id": "wi_xxx",
        "title": "用户登录功能开发",
        "type_identifier": "story",
        "status_identifier": "done",
        "priority": "high",
        "assignee": {
          "id": "user_xxx",
          "name": "张三"
        },
        "story_point": 5,
        "iteration_id": "iter_xxx",
        "parent_id": null,
        "created_at": "2025-05-01T08:00:00Z",
        "updated_at": "2025-05-10T15:30:00Z",
        "due_date": "2025-05-12",
        "module": {
          "id": "mod_xxx",
          "name": "用户模块"
        }
      }
    ],
    "total": 45
  }
}
```

### Get Work Item Detail

```
GET /v1/projects/{project_id}/work-items/{work_item_id}
```

### Get Work Item Types

获取项目可用的工作项类型列表（用于区分需求/任务/Bug）。

```
GET /v1/projects/{project_id}/work-item-types
```

**Response:**

```json
{
  "code": 200,
  "data": {
    "items": [
      {
        "id": "wit_xxx",
        "identifier": "story",
        "name": "用户故事",
        "icon": "https://..."
      },
      {
        "id": "wit_yyy",
        "identifier": "task",
        "name": "任务",
        "icon": "https://..."
      },
      {
        "id": "wit_zzz",
        "identifier": "bug",
        "name": "缺陷",
        "icon": "https://..."
      }
    ]
  }
}
```

---

## Bug/Defect API

### List Bugs

```
GET /v1/projects/{project_id}/bugs
```

**Query Parameters:**

| 参数           | 类型   | 说明                                                             |
| -------------- | ------ | ---------------------------------------------------------------- |
| iteration_id   | string | 迭代 ID                                                          |
| status         | string | 状态：new / processing / resolved / verified / closed / rejected |
| priority       | string | 优先级：urgent / high / medium / low                             |
| assignee_id    | string | 负责人 ID                                                        |
| module_id      | string | 模块 ID                                                          |
| created_after  | string | 创建时间起始（ISO 8601）                                         |
| created_before | string | 创建时间截止（ISO 8601）                                         |
| page           | int    | 页码                                                             |
| per_page       | int    | 每页数量                                                         |

**Response:**

```json
{
  "code": 200,
  "data": {
    "items": [
      {
        "id": "bug_xxx",
        "title": "登录页面验证码不显示",
        "identifier": "EC-BUG-001",
        "status": "processing",
        "priority": "high",
        "severity": "major",
        "assignee": {
          "id": "user_xxx",
          "name": "张三"
        },
        "creator": {
          "id": "user_yyy",
          "name": "李四"
        },
        "iteration_id": "iter_xxx",
        "module": {
          "id": "mod_xxx",
          "name": "用户模块"
        },
        "created_at": "2025-05-05T10:00:00Z",
        "updated_at": "2025-05-08T14:30:00Z",
        "resolved_at": null,
        "due_date": "2025-05-10",
        "environment": "Chrome 120 / Windows 11",
        "steps_to_reproduce": "1. 打开登录页\n2. 点击获取验证码\n3. 验证码区域空白"
      }
    ],
    "total": 23
  }
}
```

### Get Bug Detail

```
GET /v1/projects/{project_id}/bugs/{bug_id}
```

### Bug Status Flow

| 状态   | 标识       | 说明               |
| ------ | ---------- | ------------------ |
| 新建   | new        | 刚提交，未分配     |
| 处理中 | processing | 已分配，正在修复   |
| 已解决 | resolved   | 已提交修复代码     |
| 已验证 | verified   | 测试验证通过       |
| 已关闭 | closed     | 完整闭环           |
| 已拒绝 | rejected   | 非缺陷/重复/不修复 |

### Bug Priority Levels

| 优先级 | 标识   | 建议处理时间 |
| ------ | ------ | ------------ |
| 紧急   | urgent | 立即修复     |
| 高     | high   | 24小时内     |
| 中     | medium | 当前迭代内   |
| 低     | low    | 排期修复     |

### Bug Severity Levels

| 严重程度 | 标识       | 说明                 |
| -------- | ---------- | -------------------- |
| 致命     | fatal      | 系统崩溃、数据丢失   |
| 严重     | major      | 核心功能不可用       |
| 一般     | normal     | 功能受限但有替代方案 |
| 轻微     | minor      | UI/文案等小问题      |
| 建议     | suggestion | 优化建议             |

---

## Module API

### List Modules

```
GET /v1/projects/{project_id}/modules
```

**Response:**

```json
{
  "code": 200,
  "data": {
    "items": [
      {
        "id": "mod_xxx",
        "name": "用户模块",
        "parent_id": null
      },
      {
        "id": "mod_yyy",
        "name": "支付模块",
        "parent_id": null
      }
    ]
  }
}
```

---

## Error Codes

| HTTP Status | code | 说明                |
| ----------- | ---- | ------------------- |
| 200         | 200  | 成功                |
| 400         | 400  | 请求参数错误        |
| 401         | 401  | 未认证或 Token 无效 |
| 403         | 403  | 无权限访问          |
| 404         | 404  | 资源不存在          |
| 429         | 429  | 请求频率超限        |
| 500         | 500  | 服务器内部错误      |

---

## Rate Limiting

- 默认限制：每分钟 120 次请求
- 响应 Header 包含限流信息：
  - `X-RateLimit-Limit`: 总限额
  - `X-RateLimit-Remaining`: 剩余次数
  - `X-RateLimit-Reset`: 重置时间（Unix 时间戳）

超出限制时返回 429 状态码，需等待后重试。

---

## Data Fetching Best Practices

1. **分页拉取全量数据**：循环请求直到 `page * per_page >= total`
2. **并发控制**：避免同时发起过多请求，建议并发数 ≤ 5
3. **缓存项目/迭代信息**：项目列表和迭代列表变化不频繁，可缓存
4. **时间范围过滤**：利用 `created_after` / `created_before` 缩小查询范围
5. **错误重试**：遇到 429 或 5xx 错误，指数退避重试（1s → 2s → 4s → 8s）
6. **时区处理**：API 返回 UTC 时间，展示时转换为本地时区（Asia/Shanghai）
