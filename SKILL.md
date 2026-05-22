---
name: pingcode-progress-report
description: PingCode 项目进展与 Bug 量统计报告工具。已部署到 Trae CN Skill 目录，直接调用即可。
---

# PingCode 项目进展与 Bug 量统计报告

## Overview

通过 PingCode REST API 获取项目数据，支持三大功能模块：

1. **项目进展报告** — 迭代进度、Bug 统计、燃尽分析
2. **Bug 全量分析** — 全量 Bug 分类汇总、趋势追踪、AI 总结
3. **绩效表生成** — 按月自动填充绩效数据

## ⚠️ 安全约束

- **只操作用户明确选择的项目**，不擅自访问其他项目
- **绝不修改、删除、创建** PingCode 上的任何数据，只做读取和统计
- **绝不泄露** config.json 中的 client_id、client_secret、access_token

## ⚠️ 执行约束

- **必须使用 scripts/ 目录下的脚本文件**，不要用 `py -c "..."` 内联命令（PowerShell 转义会出错）
- 所有脚本自动定位 config.json，无需手动指定路径

---

## 执行流程

### 步骤 1：查找或创建配置

```
1. 在 Skill 目录中查找 config.json
2. 如果找到 → 进入步骤 2
3. 如果找不到 → 引导用户创建：
   a. 告知用户需要 PingCode 的 client_id 和 client_secret
   b. 用以下模板在 Skill 目录创建 config.json：
```

config.json 模板（不需要填项目 ID，项目由用户运行时选择）：

```json
{
  "api": {
    "base_url": "https://open.pingcode.com",
    "client_id": "<用户的 client_id>",
    "client_secret": "<用户的 client_secret>",
    "grant_type": "client_credentials"
  }
}
```

### 步骤 2：验证配置

```
1. 读取 config.json
2. 验证 api.client_id、api.client_secret 是否存在
3. 缺少任何一项 → 提示用户补充，给出具体缺少的字段名
```

### 步骤 3：获取 Access Token

```bash
py scripts/get_token.py
```

- 成功 → 输出一行 Token 字符串，记录下来进入步骤 4
- 失败 → 报错："PingCode API 认证失败，请检查 client_id 和 client_secret"

### 步骤 4：确定目标项目（从用户输入动态解析）

**必须从用户的输入中提取项目信息，不能写死任何项目。**

```
1. 从用户输入中识别项目名称/标识/ID
   - 用户说"BIMS的bug" → 项目标识 = BIMS
   - 用户说"新云平台的迭代" → 项目名称 = 新云平台
   - 用户说"695c688d76fc97ecec248af0的bug" → 项目ID = 695c688d76fc97ecec248af0
2. 如果用户未指定项目 → 列出所有项目让用户选择
3. 用 list_projects.py 的输出匹配到 project_id
```

列出所有项目：

```bash
py scripts/list_projects.py <token>
```

输出格式：`项目标识  项目名称  项目ID`，匹配后记录 project_id。

### 步骤 5：从用户输入解析过滤条件并获取数据

**核心原则：不要每次都获取全量数据，必须根据用户输入动态匹配过滤条件。**

#### 5.1 从用户输入中提取过滤条件

对用户的自然语言输入进行解析，提取以下维度的过滤条件：

| 提取维度        | 识别方式                                                          | 对应参数                                      |
| --------------- | ----------------------------------------------------------------- | --------------------------------------------- |
| **迭代/版本**   | 用户提到版本号、迭代名、sprint名（如"2.1.0"、"迭代1.40"、"v3.0"） | `--sprint-name <提取的名称>`                  |
| **工作项类型**  | 用户提到"需求"、"任务"、"bug"、"缺陷"等                           | `--type story` / `--type task` / `--type bug` |
| **是否关注Bug** | 用户提到"bug"、"缺陷"、"问题"等                                   | `--bug-only`                                  |
| **时间范围**    | 用户提到"5月份"、"最近一周"、"2026年Q2"等                         | `--start-date` / `--end-date`                 |
| **全量分析**    | 用户明确要求"全量"、"所有"、"全部"                                | 无过滤参数                                    |

**解析示例（注意：以下仅为解析逻辑说明，实际值必须从用户输入中提取）：**

| 用户输入                  | 提取结果                              | 构建的命令参数                                             |
| ------------------------- | ------------------------------------- | ---------------------------------------------------------- |
| "BIMS迭代2.1.0的bug"      | 项目=BIMS, 迭代=2.1.0, 类型=bug       | `--sprint-name "2.1.0" --bug-only`                         |
| "新云平台迭代1.0做了什么" | 项目=新云平台, 迭代=1.0               | `--sprint-name "1.0"`                                      |
| "CRM的bug统计"            | 项目=CRM, 类型=bug                    | `--bug-only`                                               |
| "数据管理平台5月份的bug"  | 项目=数据管理平台, 时间=5月, 类型=bug | `--bug-only --start-date 2026-05-01 --end-date 2026-05-31` |
| "BIMS全量bug报告"         | 项目=BIMS, 全量                       | 无过滤参数                                                 |

#### 5.2 迭代名称解析流程

当从用户输入中提取到迭代/版本名称时，按以下流程处理：

```
1. 将提取的名称传给 --sprint-name 参数
2. 脚本会自动模糊匹配（如用户说"2.1.0"能匹配到"2.1.0（5.12-5.18）"）
3. 如果匹配成功 → 脚本自动通过 sprint_id 在API层面过滤，大幅减少数据量
4. 如果匹配失败（stderr输出WARNING） → 执行以下降级策略：
   a. 调用 list_sprints.py 列出该项目的所有迭代
   b. 让用户从列表中选择正确的迭代
   c. 如果用户无法确认，使用迭代的时间范围作为 --start-date / --end-date 过滤
```

列出迭代列表：

```bash
py scripts/list_sprints.py <token> <project_id>
```

输出格式：每行一个JSON，包含 id、name、status、start_at、end_at

#### 5.3 Bug识别逻辑（不要修改）

Bug的判断标准：

- `type == 'bug'` 的缺陷工作项
- `type == 'story'` 且 `properties.backlog_type` 在 `BUG_BACKLOG_TYPE_IDS` 中的用户故事

使用 `--bug-only` 参数时，脚本自动只拉取 `type=bug` 和 `type=story` 两种类型，避免拉取无关的 task/epic/feature 数据。

#### 5.4 执行获取命令

根据5.1提取的过滤条件，动态拼接命令参数：

```bash
# 通用格式（所有值从用户输入动态提取）
py scripts/fetch_work_items.py <token> <project_id> [动态拼接的过滤参数]

# 可能的参数组合：
# --sprint-name "<用户提到的迭代名>"
# --bug-only
# --type <用户提到的类型>
# --start-date <解析的起始日期> --end-date <解析的结束日期>
```

输出格式：

- 第一行：`TOTAL_ITEMS:数字`
- 第二行：`TOTAL_BUGS:数字`
- 如果无数据：第三行输出 `NO_DATA:No work items found for the given filters`
- 后续每行：一个工作项的 JSON 数据
  - **Bug 项**：包含 id、title、type、state、priority、creator、sprint、module、level、origin、created、completed、hours、investigator（排查人）、resolver（解决人）
  - **非Bug项**（`--all` 模式）：包含 id、title、type、state、priority、assignee、creator、sprint、module、created、completed、hours

Bug 的排查人/解决人通过匹配其下以"排查："或"解决："开头的任务标题来确定。

### 步骤 6：根据用户请求执行对应功能

| 功能类型     | 触发关键词             | 执行方式                                         |
| ------------ | ---------------------- | ------------------------------------------------ |
| **Bug 统计** | bug、缺陷、统计、分析  | 从步骤5数据中筛选 bug，分类统计，AI 总结         |
| **需求分析** | 迭代、需求、完成、汇报 | 从步骤5数据中筛选需求/任务，统计完成率、故事点等 |
| **绩效表**   | 绩效、月报、工作量     | 运行 `py scripts/generate-performance.py`        |

**绩效表生成流程：**

**⚠️ 核心原则：**

- **必须让用户单选一个人**，不能默认生成所有人的绩效表
- **必须读取 `template/template.xlsx`** 的「工作完成情况」Sheet 样式并复用
- **中途产生的分项目文件必须在完成后删除**

**执行步骤：**

1. **按项目分别生成中间文件**：对用户选择的每个项目，分别运行 `generate-performance.py`，**必须传递 `--project-name` 参数**（使用项目的标识/名称，如 "BIMS"、"CRM"），确保绩效表的「项目名称」列填入正确的项目名而非模块/迭代名

   ```bash
   py scripts/generate-performance.py --year <年> --month <月> --project-id <项目ID> --project-name "<项目标识>" --output output/performance-YYYYMM-<项目标识>.xlsx
   ```

2. **列出所有人员**：运行合并脚本的 `--list-persons` 模式，获取所有人员名单

   ```bash
   py scripts/merge_performance.py --list-persons
   ```

   输出：每行一个人名

3. **让用户选择一个人**：用 AskUserQuestion 工具展示人员列表，让用户**单选**一个人

4. **询问用户保存位置**：用 AskUserQuestion 工具询问用户希望将最终绩效表保存到哪个路径。提供默认路径 `output/performance-YYYYMM.xlsx`，但允许用户指定任意路径

5. **为选中人员生成最终绩效表**：运行合并脚本，指定 `--assignee` 参数和用户选择的输出路径

   ```bash
   py scripts/merge_performance.py --assignee "<用户选择的人名>" --output "<用户指定的保存路径>"
   ```

6. **中间文件自动清理**：合并脚本成功后会自动删除 `output/performance-YYYYMM-*.xlsx` 中间文件

**最终输出格式：**

列映射通过 `analyze_template_columns()` 智能识别 `template/template.xlsx` 的列结构，不硬编码列顺序。识别逻辑：

1. 先尝试匹配表头关键词（如"项目名称"、"日期"、"工作内容"等）
2. 若无表头，则通过内容特征评分（日期格式→日期列，短文本→项目列，长文本+编号→内容列）

默认映射（无模板或识别失败时）：

| 列  | 内容     | 说明                                                                      |
| --- | -------- | ------------------------------------------------------------------------- |
| A   | 项目名称 | 同一项目多行纵向合并                                                      |
| B   | 日期     | 格式 "M.D"（如 5.12），居中对齐                                           |
| C   | 工作内容 | 编号列表，已完成加"完成："前缀，Bug加"解决："前缀，进行中加"进行中："前缀 |

样式从 `template/template.xlsx` 的「工作完成情况」Sheet 读取并复用。

**脚本参数：**

`generate-performance.py`：

```bash
py scripts/generate-performance.py --year 2026 --month 5 --project-id <id> --project-name "<项目标识>" --output <路径>
```

| 参数             | 必填 | 说明                                                                               |
| ---------------- | ---- | ---------------------------------------------------------------------------------- |
| `--year`         | 否   | 年份，默认当前年                                                                   |
| `--month`        | 否   | 月份，默认当前月                                                                   |
| `--project-id`   | 是   | 项目ID                                                                             |
| `--project-name` | 否   | 项目名称/标识，填入绩效表「项目名称」列。不传则回退使用工作项的 module/sprint 字段 |
| `--output`       | 否   | 输出路径，默认 `output/performance-YYYYMM.xlsx`                                    |
| `--assignee`     | 否   | 指定人员姓名，只生成该人员的 Sheet                                                 |

`merge_performance.py`：

```bash
py scripts/merge_performance.py --list-persons
py scripts/merge_performance.py --assignee "<姓名>" --output <路径>
```

| 参数             | 必填 | 说明                                            |
| ---------------- | ---- | ----------------------------------------------- |
| `--list-persons` | 否   | 列出所有可用人员名单                            |
| `--assignee`     | 是   | 指定人员姓名，只生成该人员的 Sheet              |
| `--output`       | 否   | 输出路径，默认 `output/performance-YYYYMM.xlsx` |

**输出说明：**

- 无数据：`NO_DATA:No work items found for the given period` 或 `NO_DATA:No performance data found for the given period`
- openpyxl 未安装：自动降级生成 CSV 文件
- 成功：`SUCCESS: Performance Excel saved to <路径>`

### 步骤 7：生成报告

根据统计结果，按以下结构生成 Markdown 报告：

1. **总体概览** — Bug 总数、已关闭/未关闭、解决率
2. **Bug 深度分析**（重点，不是简单罗列，要归纳总结）：
   - **模块/功能分布**：Bug 集中在哪些模块或功能领域？占比如何？
   - **根因归类**：将 Bug 按根本原因归类（如：数据同步问题、前端校验缺失、字段缺失、权限问题、旧数据兼容等），分析每类原因的 Bug 数量
   - **高频问题总结**：哪些问题反复出现？是否存在共性原因？
   - **排查/解决分工**：谁排查的多、谁解决的多，是否有瓶颈
   - **解决效率**：平均解决时长，哪些 Bug 耗时最长，为什么
3. **趋势分析** — 按月创建趋势、解决时长分析
4. **风险提示与改进建议** — 基于分析结果给出具体可执行的改进建议（如：某模块需加强测试、某类问题需从架构层面解决等）

**Bug 分析原则**：

- 不要逐条罗列 Bug，要归纳分类后总结
- 从 Bug 标题和模块字段中提取业务领域，按领域汇总
- 从排查人/解决人信息分析团队分工情况
- 从解决时长分析效率瓶颈
- 给出的改进建议要具体，不要泛泛而谈

---

## 脚本清单

| 脚本                              | 用途                           | 用法                                                                                                                     |
| --------------------------------- | ------------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| `scripts/get_token.py`            | 获取 Access Token              | `py scripts/get_token.py`                                                                                                |
| `scripts/list_projects.py`        | 列出所有项目                   | `py scripts/list_projects.py <token>`                                                                                    |
| `scripts/list_sprints.py`         | 列出项目迭代                   | `py scripts/list_sprints.py <token> <project_id>`                                                                        |
| `scripts/fetch_work_items.py`     | 拉取项目工作项（支持过滤）     | `py scripts/fetch_work_items.py <token> <project_id> [过滤参数]`                                                         |
| `scripts/fetch_bugs.py`           | Bug 全量统计报告（独立运行）   | `py scripts/fetch_bugs.py [项目标识/ID]`                                                                                 |
| `scripts/generate-performance.py` | 生成绩效表（每日工作日志格式） | `py scripts/generate-performance.py --year 2026 --month 5 --project-id <id> --project-name "<项目标识>" --output <路径>` |
| `scripts/merge_performance.py`    | 合并多项目绩效表、人员筛选     | `py scripts/merge_performance.py --list-persons` 或 `--assignee "<姓名>" --output <路径>`                                |
| `scripts/http_tool.py`            | 通用 HTTP 工具                 | `py scripts/http_tool.py token <client_id> <client_secret>`                                                              |

---

## API 参考

| 功能         | 端点                                                                                              | 方法 |
| ------------ | ------------------------------------------------------------------------------------------------- | ---- |
| 获取 Token   | `/v1/auth/token?grant_type=client_credentials&client_id={id}&client_secret={secret}`              | GET  |
| 获取项目列表 | `/v1/project/projects`                                                                            | GET  |
| 获取迭代列表 | `/v1/project/projects/{project_id}/sprints`                                                       | GET  |
| 获取工作项   | `/v1/project/work_items?project_id={id}&page_size=100&page_index={n}&type={type}&sprint_id={sid}` | GET  |

Base URL：`https://open.pingcode.com`（从 config.json 读取）

### 工作项 API 支持的过滤参数

| 参数       | 类型   | 说明                                            |
| ---------- | ------ | ----------------------------------------------- |
| project_id | string | 必填，项目ID                                    |
| type       | string | 工作项类型：story / task / bug / epic / feature |
| sprint_id  | string | 迭代ID，通过迭代列表接口获取                    |
| page_size  | int    | 每页数量，最大100                               |
| page_index | int    | 页码，从0开始                                   |

注意：API 不支持日期范围过滤参数，日期过滤在客户端通过 `--start-date` / `--end-date` 实现。

分页说明：循环请求直到 `len(all_items) >= total`，每页 100 条。

---

## 错误处理

| 错误情况           | 处理方式                                   |
| ------------------ | ------------------------------------------ |
| 找不到 config.json | 引导用户创建，提供模板和说明               |
| 配置不完整         | 提示缺少的具体字段名                       |
| API 认证失败       | 提示检查 client_id 和 client_secret        |
| API 请求失败       | 提示网络或权限问题，建议重试               |
| 项目无数据         | 告知用户该项目当前无工作项或 Bug           |
| 迭代名称未匹配     | 列出可用迭代让用户选择，或改用时间范围过滤 |
