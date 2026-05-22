# 项目进展与 Bug 量统计报告

> **报告日期：** {report_date}
> **项目名称：** {project_name}
> **当前迭代：** {iteration_name}（{iteration_start} ~ {iteration_end}）
> **报告周期：** {stat_period_start} ~ {stat_period_end}

---

## 1. 基本信息概览

| 指标 | 数值 |
|------|------|
| 项目状态 | {project_status} |
| 当前迭代进度 | {iteration_progress}% |
| 迭代剩余天数 | {remaining_days} 天 |
| 团队人数 | {team_size} 人 |
| 总工作项数 | {total_work_items} |
| 总 Bug 数 | {total_bugs} |
| 遗留 Bug 数 | {open_bugs} |

---

## 2. 项目进展

### 2.1 迭代整体进度

```
进度：[████████░░░░░░░░] {iteration_progress}%
```

| 指标 | 数值 | 占比 |
|------|------|------|
| 总工作项 | {total_work_items} | 100% |
| 已完成 | {done_count} | {done_pct}% |
| 进行中 | {in_progress_count} | {in_progress_pct}% |
| 未开始 | {todo_count} | {todo_pct}% |
| 已逾期 | {overdue_count} | {overdue_pct}% |

### 2.2 故事点进度

| 指标 | 故事点 | 占比 |
|------|--------|------|
| 总故事点 | {total_sp} | 100% |
| 已完成故事点 | {done_sp} | {done_sp_pct}% |
| 剩余故事点 | {remaining_sp} | {remaining_sp_pct}% |

### 2.3 逾期风险项

| 工作项 | 负责人 | 截止日期 | 逾期天数 |
|--------|--------|----------|----------|
| {overdue_item_1} | {assignee_1} | {due_date_1} | {overdue_days_1} |
| {overdue_item_2} | {assignee_2} | {due_date_2} | {overdue_days_2} |

---

## 3. Bug 量统计

### 3.1 按状态分布

| 状态 | 数量 | 占比 | 可视化 |
|------|------|------|--------|
| 新建 | {new_count} | {new_pct}% | {new_bar} |
| 处理中 | {processing_count} | {processing_pct}% | {processing_bar} |
| 已解决 | {resolved_count} | {resolved_pct}% | {resolved_bar} |
| 已验证 | {verified_count} | {verified_pct}% | {verified_bar} |
| 已关闭 | {closed_count} | {closed_pct}% | {closed_bar} |
| 已拒绝 | {rejected_count} | {rejected_pct}% | {rejected_bar} |

### 3.2 按优先级分布

| 优先级 | 数量 | 占比 |
|--------|------|------|
| 🔴 紧急 | {urgent_count} | {urgent_pct}% |
| 🟠 高 | {high_count} | {high_pct}% |
| 🟡 中 | {medium_count} | {medium_pct}% |
| 🟢 低 | {low_count} | {low_pct}% |

### 3.3 按严重程度分布

| 严重程度 | 数量 | 占比 |
|----------|------|------|
| 💀 致命 | {fatal_count} | {fatal_pct}% |
| 🔴 严重 | {major_count} | {major_pct}% |
| 🟡 一般 | {normal_count} | {normal_pct}% |
| 🟢 轻微 | {minor_count} | {minor_pct}% |
| 💡 建议 | {suggestion_count} | {suggestion_pct}% |

### 3.4 按模块分布

| 模块 | Bug 数量 | 已解决 | 未解决 | 解决率 |
|------|----------|--------|--------|--------|
| {module_1} | {m1_total} | {m1_resolved} | {m1_open} | {m1_rate}% |
| {module_2} | {m2_total} | {m2_resolved} | {m2_open} | {m2_rate}% |

### 3.5 按负责人分布

| 负责人 | 分配 Bug 数 | 已解决 | 处理中 | 未开始 | 平均解决时长 |
|--------|------------|--------|--------|--------|-------------|
| {dev_1} | {d1_total} | {d1_resolved} | {d1_processing} | {d1_new} | {d1_avg_time} |
| {dev_2} | {d2_total} | {d2_resolved} | {d2_processing} | {d2_new} | {d2_avg_time} |

### 3.6 Bug 趋势分析

| 指标 | 本迭代 | 上迭代 | 变化 |
|------|--------|--------|------|
| 新增 Bug 数 | {new_bugs_current} | {new_bugs_prev} | {new_bugs_delta} |
| 解决 Bug 数 | {resolved_bugs_current} | {resolved_bugs_prev} | {resolved_bugs_delta} |
| Bug 净增量 | {net_bugs_current} | {net_bugs_prev} | {net_bugs_delta} |
| Bug 解决率 | {resolve_rate_current}% | {resolve_rate_prev}% | {resolve_rate_delta} |
| 平均解决时长 | {avg_resolve_current} | {avg_resolve_prev} | {avg_resolve_delta} |
| 遗留 Bug 数 | {open_bugs_current} | {open_bugs_prev} | {open_bugs_delta} |

---

## 4. 迭代燃尽分析

### 4.1 燃尽图数据

| 日期 | 理想剩余 | 实际剩余 | 偏差 |
|------|----------|----------|------|
| {date_1} | {ideal_1} | {actual_1} | {diff_1} |
| {date_2} | {ideal_2} | {actual_2} | {diff_2} |

### 4.2 燃尽趋势判断

- **当前偏差：** {burndown_deviation} 故事点
- **预计完成日期：** {estimated_end_date}
- **风险等级：** {risk_level}（低/中/高）

---

## 5. 风险与建议

### 5.1 风险项

{risks_list}

### 5.2 改进建议

{suggestions_list}

---

*本报告由 AI 基于 PingCode API 数据自动生成，数据截止时间：{data_cutoff_time}*

---

# 附录 A: Bug 全量分析报告模板

> **报告日期：** {report_date}
> **统计范围：** {stat_period_start} ~ {stat_period_end}
> **项目名称：** {project_name}

## A.1 汇总概览

| 指标 | 数值 |
|------|------|
| Bug 总数 | {total_bugs} |
| 已解决数 | {resolved_bugs} |
| 未解决数 | {open_bugs} |
| 整体解决率 | {resolve_rate}% |
| 平均解决时长 | {avg_resolve_time} 天 |
| 长期未解决数（>7天） | {long_unresolved_count} |

## A.2 按状态分布

| 状态 | 数量 | 占比 | 可视化 |
|------|------|------|--------|
| 新建 | {new_count} | {new_pct}% | {bar} |
| 处理中 | {processing_count} | {processing_pct}% | {bar} |
| 已解决 | {resolved_count} | {resolved_pct}% | {bar} |
| 已验证 | {verified_count} | {verified_pct}% | {bar} |
| 已关闭 | {closed_count} | {closed_pct}% | {bar} |
| 已拒绝 | {rejected_count} | {rejected_pct}% | {bar} |

## A.3 按优先级分布

| 优先级 | 数量 | 占比 |
|--------|------|------|
| 🔴 紧急 | {urgent_count} | {urgent_pct}% |
| 🟠 高 | {high_count} | {high_pct}% |
| 🟡 中 | {medium_count} | {medium_pct}% |
| 🟢 低 | {low_count} | {low_pct}% |

## A.4 按严重程度分布

| 严重程度 | 数量 | 占比 |
|----------|------|------|
| 💀 致命 | {fatal_count} | {fatal_pct}% |
| 🔴 严重 | {major_count} | {major_pct}% |
| 🟡 一般 | {normal_count} | {normal_pct}% |
| 🟢 轻微 | {minor_count} | {minor_pct}% |
| 💡 建议 | {suggestion_count} | {suggestion_pct}% |

## A.5 按模块分布

| 模块 | Bug 数量 | 已解决 | 未解决 | 解决率 |
|------|----------|--------|--------|--------|
| {module_1} | {m1_total} | {m1_resolved} | {m1_open} | {m1_rate}% |
| {module_2} | {m2_total} | {m2_resolved} | {m2_open} | {m2_rate}% |

## A.6 按负责人分布

| 负责人 | 分配数 | 已解决 | 处理中 | 未开始 | 平均时长 |
|--------|--------|--------|--------|--------|---------|
| {dev_1} | {d1_total} | {d1_resolved} | {d1_processing} | {d1_new} | {d1_avg} |
| {dev_2} | {d2_total} | {d2_resolved} | {d2_processing} | {d2_new} | {d2_avg} |

## A.7 按月份趋势

| 月份 | 新增数 | 解决数 | 净增量 | 累计未解决 |
|------|--------|--------|--------|-----------|
| {month_1} | {m1_new} | {m1_resolved} | {m1_net} | {m1_cumulative} |
| {month_2} | {m2_new} | {m2_resolved} | {m2_net} | {m2_cumulative} |

## A.8 长期未解决 Bug 清单

| Bug 标识 | 标题 | 负责人 | 状态 | 已持续天数 | 优先级 |
|----------|------|--------|------|-----------|--------|
| {bug_id_1} | {bug_title_1} | {assignee_1} | {status_1} | {days_1} | {priority_1} |
| {bug_id_2} | {bug_title_2} | {assignee_2} | {status_2} | {days_2} | {priority_2} |

## A.9 AI 分析总结

{ai_summary}

---

# 附录 B: 迭代需求汇报模板

> **迭代名称：** {iteration_name}
> **时间范围：** {iteration_start} ~ {iteration_end}
> **项目名称：** {project_name}

## B.1 迭代概览

| 指标 | 数值 |
|------|------|
| 总需求数 | {total_requirements} |
| 已完成数 | {completed_requirements} |
| 进行中数 | {in_progress_requirements} |
| 未开始数 | {todo_requirements} |
| 总故事点 | {total_sp} |
| 已完成故事点 | {done_sp} |
| 完成率 | {completion_rate}% |

## B.2 已完成需求清单（按负责人）

### {assignee_name_1}（共 {count_1} 项，{sp_1} 故事点）

| 需求标识 | 需求名称 | 类型 | 模块 | 完成时间 |
|----------|----------|------|------|----------|
| {req_id_1} | {req_title_1} | {type_1} | {module_1} | {done_date_1} |
| {req_id_2} | {req_title_2} | {type_2} | {module_2} | {done_date_2} |

### {assignee_name_2}（共 {count_2} 项，{sp_2} 故事点）

| 需求标识 | 需求名称 | 类型 | 模块 | 完成时间 |
|----------|----------|------|------|----------|
| {req_id_3} | {req_title_3} | {type_3} | {module_3} | {done_date_3} |

## B.3 已完成需求清单（按模块）

### {module_name_1}

| 需求标识 | 需求名称 | 负责人 | 类型 | 完成时间 |
|----------|----------|--------|------|----------|
| {req_id_4} | {req_title_4} | {assignee_4} | {type_4} | {done_date_4} |

## B.4 需求完成统计

| 维度 | 分类 | 数量 | 故事点 |
|------|------|------|--------|
| 按类型 | 用户故事 | {story_count} | {story_sp} |
| 按类型 | 任务 | {task_count} | {task_sp} |
| 按状态 | 已完成 | {done_count} | {done_sp} |
| 按状态 | 进行中 | {in_progress_count} | {in_progress_sp} |
| 按状态 | 未开始 | {todo_count} | {todo_sp} |

## B.5 亮点需求

> 标记本迭代中重要功能项、紧急需求或高价值交付

| 需求标识 | 需求名称 | 亮点说明 | 负责人 |
|----------|----------|---------|--------|
| {highlight_id_1} | {highlight_title_1} | {highlight_reason_1} | {assignee_5} |

---

# 附录 C: 月度绩效表

> **绩效月份：** {year}年{month}月
> **项目名称：** {project_name}
> **说明：** 数据来源于 PingCode，可直接复制到 Excel 或在线表格

## C.1 成员工作量统计

| 姓名 | 完成需求数 | 完成任务数 | 完成故事点 | 分配 Bug 数 | 解决 Bug 数 | 逾期次数 | 综合得分 |
|------|-----------|-----------|-----------|------------|------------|---------|---------|
| {name_1} | {c1_stories} | {c1_tasks} | {c1_sp} | {c1_assigned_bugs} | {c1_resolved_bugs} | {c1_overdue} | {c1_score} |
| {name_2} | {c2_stories} | {c2_tasks} | {c2_sp} | {c2_assigned_bugs} | {c2_resolved_bugs} | {c2_overdue} | {c2_score} |

## C.2 计算说明

- **完成需求数**：type=story, status=已完成，且 `updated_at` 在当月内的数量
- **完成故事点**：`updated_at` 在当月内且状态为已完成的工作项的故事点之和
- **解决 Bug 数**：`resolved_at` 在当月内的缺陷数
- **逾期次数**：`due_date` 过期且 `updated_at` 在当月内但状态仍非已完成的工作项数
- **综合得分** = (完成故事点 × 权重1) + (解决Bug数 × 权重2) - (逾期次数 × 权重3)

## C.3 详细数据导出（CSV 格式）

可直接复制以下内容保存为 `.csv` 文件：

```
姓名,完成需求数,完成任务数,完成故事点,分配Bug数,解决Bug数,逾期次数,综合得分
{name_1},{c1_stories},{c1_tasks},{c1_sp},{c1_assigned_bugs},{c1_resolved_bugs},{c1_overdue},{c1_score}
{name_2},{c2_stories},{c2_tasks},{c2_sp},{c2_assigned_bugs},{c2_resolved_bugs},{c2_overdue},{c2_score}
```

*本绩效表由 AI 基于 PingCode 数据自动生成，数据截止时间：{data_cutoff_time}*
