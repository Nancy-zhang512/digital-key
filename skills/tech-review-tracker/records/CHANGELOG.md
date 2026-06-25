# CHANGELOG — tech-review-tracker

## v1.2.0（2026-06-25）

### 修复：多责任人任务创建 + IM 通知遗漏问题

**Bug 根因**：当任务有多个责任人时（如 No.5 李高文/李富/王国强，No.15 黄晓群/韩财学/李高文/蒋国平），旧版 Step 4 将第2+人设为 `--follower`，导致他们不是任务 assignee；IM 通知也未逐人发送。

**修复内容：**

1. **Step 4 多责任人处理** ：
   - 修正为：先用 `task +create --assignee <op_id_1>` 创建任务，再用 `task +assign --task-id "<guid>" --add "<ou2>,<ou3>"` 追加剩余人为 assignee
   - 删除"其余人用 `--follower`"的错误说明
   - 明确 guid 提取路径：`data.guid`（不是 `data.task.id` 也不是 `data.task.guid`）

2. **Step 5 IM 通知** ：
   - 明确要求：多责任人必须逐人发送 IM，N 个 assignee 发 N 条
   - 禁止只通知第一责任人

3. **IM 命令修正** ：
   - 正确命令：`lark-cli im +messages-send --user-id ... --text ...`（不是 `im message send` 也不是 `im messages send`）

## v1.1.0（2026-06-24）

### 新增：任务ID回写 + 状态自动同步
- Step 4 增强：飞书任务创建成功后，立即将 task_id 回写到 Base「技术评审管理中台」对应记录的「任务ID」字段
- 新增 Step 9：状态自动同步（一键回填进度）
  - 扫描 Base 中所有「任务ID」非空的记录
  - 逐一查询飞书任务的 completed_at 状态
  - 已完成的任务自动回写 Base 状态为「已完成」
  - 汇报同步结果：已完成/进行中/逾期未完成分类列出
- Base 配置：新增「任务ID」字段（fldGTJfMTb，text类型）到 tblyPLlBAO88SYAq

## v1.0.1（2026-06-24）

### 修复：加入"预览确认"双重防护机制
- Step 3 新增：创建任务前将完整执行计划发给触发人（当前登录用户）审阅，等待明确确认才继续
- Step 5（原Step 4）改为：任务创建后不立即发 IM，先将通知草稿发给触发人二次确认，确认后才向责任人发送
- 角色定义更新：明确"任何面向责任人的操作前必须经触发人二次确认"
- 背景：初次执行时直接向张军/方召发出了任务和通知，用户反馈需先测试

## v1.0.0（2026-06-24）

### 初始版本
- 支持从飞书正式纪要"待办事项"表格提取待办（No./事项/责任人/完成时间/状态）
- 支持解析责任人 open_id（lark-contact）
- 支持批量创建飞书任务（lark-task），含 assignee 和 due 时间
- 支持发送 IM 通知给责任人
- 支持更新纪要文档中的状态单元格（str_replace）
- 支持逾期检测与提醒
- 支持触发二次评审（写入评审表格 + 提示运行 tech-review-meeting）
- 支持 checkbox 格式备用解析（AI妙记纪要格式）
