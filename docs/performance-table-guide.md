# 绩效表模板配置指南

> **核心理念：** 你提供完整的 Excel 模板（保留原始格式、公式、样式），AI 读取后按相同格式生成填充好数据的新 Excel 文件。

---

## 模板存放位置

```
f:\myPro\skill\pingcode-progress-report\template\template.xlsx
```

## 配置步骤

1. **把你们公司的绩效表 Excel 原样放过去**，命名为 `template.xlsx`
2. **不需要清空数据** — AI 会读取完整模板来理解结构
3. 告诉 AI："绩效表模板已放好，请生成 2025年5月绩效表"

## AI 如何处理你的模板

```
1. 用 Python openpyxl 读取 template/template.xlsx
2. 分析模板结构：
   ├── 识别表头行位置和列名
   ├── 识别数据行起始位置（表头之后的第一行）
   ├── 识别数据行结束位置（最后一个有数据的行）
   ├── 保留单元格格式（字体、边框、对齐、背景色、数字格式）
   ├── 保留合并单元格
   ├── 保留列宽、行高
   ├── 保留公式（如 SUM 求和行、评分公式）
   └── 识别固定行（如合计行、说明行）vs 数据行
3. 智能匹配列名 → PingCode 数据字段
4. 无法匹配的列 → 询问用户对应什么数据
5. 调用 PingCode API 获取每个成员的绩效数据
6. 复制模板为新文件，清空旧数据行，按模板格式逐行填充
7. 更新公式引用范围（如有合计行）
8. 保存新文件
```

## 输出文件

用户指定输出路径，如："保存到桌面"。

---

## 列名智能匹配规则

AI 会根据 Excel 表头自动匹配 PingCode 数据：

| Excel 表头关键词         | 匹配的 PingCode 数据             |
| ------------------------ | -------------------------------- |
| 姓名、名字、人员、员工   | `{name}` 成员姓名                |
| 需求数、完成需求、故事数 | `{completed_stories}` 完成需求数 |
| 故事点、SP、点数         | `{completed_sp}` 完成故事点      |
| 任务数、完成任务         | `{completed_tasks}` 完成任务数   |
| Bug数、缺陷数、分配Bug   | `{assigned_bugs}` 分配 Bug 数    |
| 解决Bug、修复Bug         | `{resolved_bugs}` 解决 Bug 数    |
| 逾期、超期、延期         | `{overdue_count}` 逾期次数       |
| 得分、评分、分数         | `{score}` 综合得分               |
| 等级、评级               | `{overall_grade}` 综合等级       |

**无法自动匹配时**，AI 会询问：

> "Excel 中有一列名为「XX」，请问它对应什么数据？"

---

## AI 支持的数据字段完整列表

| 字段标识              | 说明           | 数据来源                               |
| --------------------- | -------------- | -------------------------------------- |
| `{name}`              | 成员姓名       | 项目成员列表                           |
| `{completed_stories}` | 完成需求数     | work-items type=story status=已完成    |
| `{completed_sp}`      | 完成故事点     | work-items 已完成的故事点之和          |
| `{completed_tasks}`   | 完成任务数     | work-items type=task status=已完成     |
| `{assigned_bugs}`     | 分配 Bug 数    | bugs assignee                          |
| `{resolved_bugs}`     | 解决 Bug 数    | bugs resolved_at 在月内                |
| `{created_bugs}`      | 新建 Bug 数    | bugs created_at 在月内                 |
| `{open_bugs}`         | 未解决 Bug 数  | bugs status != closed/rejected         |
| `{overdue_count}`     | 逾期次数       | work-items due_date 过期且在月内有更新 |
| `{in_progress_count}` | 进行中工作项数 | work-items status=进行中               |
| `{total_work_items}`  | 总工作项数     | work-items assignee                    |
| `{workload_score}`    | 工作量得分     | 需配置权重                             |
| `{quality_score}`     | 质量得分       | 需配置权重                             |
| `{overall_grade}`     | 综合等级       | A/B/C/D 根据分数划分                   |

---

## 绩效计算权重配置（可选）

如果 Excel 中有"得分"或"评分"列，AI 需要知道计算方式。在对话中告诉 AI 即可：

**示例：**

> "综合得分 = 故事点×2 + 解决Bug数×1 - 逾期次数×5"

**默认权重（未指定时使用）：**

- 每个故事点 2 分
- 每个完成任务 1 分
- 每个解决 Bug 1 分
- 每次逾期扣 5 分

---

## 模板格式保留说明

AI 使用 openpyxl 复制模板格式时，会保留以下内容：

| 保留项     | 说明                                     |
| ---------- | ---------------------------------------- |
| 单元格格式 | 字体、字号、加粗、颜色                   |
| 边框       | 所有边框样式                             |
| 对齐方式   | 水平/垂直对齐、自动换行                  |
| 背景色     | 单元格填充色                             |
| 数字格式   | 百分比、小数位等                         |
| 列宽       | 每列宽度                                 |
| 行高       | 每行高度                                 |
| 合并单元格 | 合并区域保持不变                         |
| 公式       | SUM/AVERAGE 等公式保留，引用范围自动扩展 |

**不保留的内容：**

- VBA 宏（openpyxl 不支持）
- 条件格式（如数据条、色阶）
- 图表

如果模板包含 VBA 宏或条件格式，AI 会在生成后提醒你手动检查。

---

## 依赖

```
pip install openpyxl
```

---

## 常见问题

**Q: 模板有多行表头怎么办？**
A: AI 会自动识别。如果表头跨越多行（如第1行是大类，第2行是子列），AI 会找到数据行开始的位置。

**Q: 模板有多个 Sheet 怎么办？**
A: AI 默认读取第一个 Sheet。如需指定，告诉 AI："绩效数据在第二个 Sheet"。

**Q: 模板中有合并单元格怎么办？**
A: AI 会保留合并单元格结构，在数据行区域避免使用已合并的列。

**Q: 想修改模板怎么办？**
A: 直接替换 `template/template.xlsx` 文件即可，下次生成自动读取新模板。

**Q: 生成的 Excel 格式和原模板不完全一致？**
A: 复杂格式（如条件格式、图表）openpyxl 无法完全保留，AI 会在生成后提醒你检查。
