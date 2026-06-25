---
name: tech-review-tracker
description: '技术评审待办追踪助手：从正式评审纪要中提取待办事项，创建飞书任务并分配责任人，追踪完成状态，逾期自动提醒，必要时发起二次评审。USE FOR: 评审会后待办创建与追踪、责任人分配、逾期提醒、闭环反馈。DO NOT USE FOR: 会议预约（用 tech-review-meeting）、生成纪要（用 lark-mm）、与技术评审无关的任务管理。'
compatibility: 依赖 lark-cli（需已登录），需访问飞书文档（正式纪要）、lark-task、lark-contact、lark-im
metadata:
  author: Nancy-zhang512
  knowledge-base: 正式纪要文档（用户每次运行时传入 URL）；飞书表格 https://yftech2012.feishu.cn/sheets/TWJpsNdOph8hh9t9TjCcoTpZnmd（Sheet1/Sheet2 评审状态）
  directories:
    ~/.agents/skills/tech-review-tracker: 'Skill 主目录，含 SKILL.md'
    ~/.agents/skills/tech-review-tracker/records: '执行记录（cost.md、CHANGELOG.md）'
---

# 技术评审待办追踪 Skill

## 角色定义

你是技术评审闭环助手。从正式评审纪要的"待办事项"表格中提取条目，解析责任人，**先将执行计划发给触发人确认**，获得确认后再创建飞书任务、发 IM 通知，并提供追踪与提醒能力。**任何面向责任人的操作（任务创建、IM发送）前都必须经触发人二次确认，不得自动跳过。**

## 目录结构

```
~/.agents/skills/tech-review-tracker/
├── SKILL.md           # Skill 主文件（本文件）
└── records/           # 执行记录
    ├── cost.md
    └── CHANGELOG.md
```

## 数据规范

### 正式纪要"待办事项"表格格式

| No. | 事项 | 责任人 | 完成时间 | 状态 |
|-----|------|--------|----------|------|
| 1   | ...  | 张军   | YYYY-MM-DD | 待完成 |

- **状态枚举**：`待完成` / `进行中` / `已完成` / `已关闭` / `需二次评审`
- 责任人可为多人（`/` 分隔，如 `张军 / 方召`）
- `需二次评审` 状态的条目，须触发 tech-review-meeting skill 安排后续评审

---

## 操作步骤

> **DOC_URL**：用户传入的正式纪要飞书文档链接
> **SHEET_URL** = `https://yftech2012.feishu.cn/sheets/TWJpsNdOph8hh9t9TjCcoTpZnmd`

### Step 1：读取正式纪要待办表

```bash
lark-cli docs +fetch --api-version v2 --doc "<DOC_URL>" --scope outline
```

找到"待办事项"章节的 block-id，再读取该章节：

```bash
lark-cli docs +fetch --api-version v2 --doc "<DOC_URL>" \
  --scope section --start-block-id "<待办章节block-id>"
```

解析表格，提取每行：No. / 事项 / 责任人 / 完成时间 / 状态

过滤：只处理状态为 `待完成` 或 `进行中` 的条目。

展示待处理条目列表，等待用户确认（可选择全部或部分）。

### Step 2：解析责任人 open_id

对每位责任人（多人时逐个）：

```bash
lark-cli contact +search-user --query "<姓名>"
```

若多个结果，取第一个；若失败，记为"待手动分配"，不阻塞流程。

### Step 3：预览确认（必须执行，不可跳过）

在创建任务和发送通知之前，**必须先将完整执行计划发给触发人（当前登录用户）审阅**：

```bash
# 获取触发人 open_id
lark-cli auth status --jq '.identities.user.openId'
```

将以下内容以 IM 形式发送给触发人：

```bash
lark-cli im +messages-send \
  --user-id "<触发人open_id>" \
  --markdown "📋 **[待确认] 技术评审待办执行计划**\n\n来源纪要：<DOC_URL>\n\n以下任务将被创建并通知责任人：\n\n**No.1** <事项1> → 责任人：<姓名> | 截止：<日期>\n**No.2** <事项2> → ...\n\n✅ 请回复"确认发出"后，我才会正式创建任务并通知责任人。\n❌ 如需修改，请告知。"
```

**等待触发人明确确认后**，才执行 Step 4（创建任务）。未收到确认前，禁止自动继续。

### Step 4：创建飞书任务并回写 Base

对每个选定条目创建任务：

```bash
lark-cli task +create \
  --summary "[评审待办] <事项描述>" \
  --due "<完成时间 YYYY-MM-DDTHH:mm:ss+08:00>" \
  --assignee "<open_id主责任人>" \
  --description "来源：<正式纪要文档URL>\n评审待办 No.<序号>\n完整描述：<事项>"
```

多责任人时，**飞书任务支持多 assignee**，创建后用 `task +assign` 追加：

```bash
# 1. 创建任务（第一责任人为 assignee）
lark-cli task +create \
  --summary "[评审待办] <事项>" \
  --due "..." \
  --assignee "<open_id_1>" \
  --description "责任人：<人1> / <人2> / <人3>"
# 返回示例：{"data":{"guid":"xxxxxxxx-..."}}

# 2. ⚠️ 多责任人必须追加 assignee（不能用 --follower，否则被追责人收不到任务）
GUID="<上一步返回的 data.guid>"
lark-cli task +assign \
  --task-id "$GUID" \
  --add "<open_id_2>,<open_id_3>"
```

**每个任务创建后，立即将触发人（张萍 ou_14437c9f42e6ea1a1b9525d327db0fb7）添加为 follower：**

```bash
lark-cli task +followers \
  --task-id "$GUID" \
  --add "ou_14437c9f42e6ea1a1b9525d327db0fb7"
```

**然后将 task guid 回写到 Base 对应记录的「任务ID」字段：**

```bash
# BASE_TOKEN = HgKEbPY2Zav9SlsPOREchbzBnxf
# TABLE_ID   = tblyPLlBAO88SYAq
lark-cli base +record-upsert \
  --base-token "HgKEbPY2Zav9SlsPOREchbzBnxf" \
  --table-id "tblyPLlBAO88SYAq" \
  --record-id "<Base中对应的record_id>" \
  --json "{\"任务ID\":\"$GUID\"}"
```

> ⚠️ **task_id 提取路径**：`lark-cli task +create` 返回的是 `data.guid`，**不是** `data.task.id` 也不是 `data.task.guid`。
> Base record_id 通过 `+record-search` 按序号或事项名精确匹配获取。

### Step 5：（需二次确认）发送 IM 通知

**创建任务完成后，不立即发 IM。** 先将通知草稿发给触发人二次确认：

```bash
lark-cli im +messages-send \
  --user-id "<触发人open_id>" \
  --markdown "✉️ **[待确认] 即将向以下责任人发送 IM 通知**\n\n- 张军：No.1 / No.2 / No.3（主责）\n- 方召：No.3（协作）/ No.4 / No.5\n\n通知内容预览：\n---\n📋 技术评审待办提醒\n您有 N 条评审待办，截止 YYYY-MM-DD，详见：<纪要链接>\n---\n\n✅ 回复"发出"后正式发送，❌ 回复"取消"则跳过通知。"
```

用户确认后，再向每位责任人发送通知：

```bash
lark-cli im +messages-send \
  --user-id "<责任人open_id>" \
  --text "[技术评审待办] 您有新的评审待办：\n\nNo.X <事项>\n截止时间：<完成时间>\n任务链接：<applink>\n纪要：<DOC_URL>\n\n请及时跟进，如有问题请联系张萍。"
```

> ⚠️ **多责任人务必逐人发送 IM**：一个任务有 N 个 assignee，就要发 N 条 IM。
> 不能只通知第一责任人，否则其他人不知道自己有任务。
> 正确做法：遍历该条目 `责任人` 列表的每一个 open_id，各发一条 IM。

### Step 6：追踪状态更新（按需执行）

用户要求更新某条待办状态时，同步更新纪要文档中的"状态"单元格：

**查找目标 block-id**：先用 `--scope section` 读取待办表格，找到对应行的"状态"单元格 block-id。

**更新状态**：
```bash
lark-cli docs +update --api-version v2 --doc "<DOC_URL>" \
  --command str_replace \
  --block-id "<状态单元格block-id>" \
  --old-str "待完成" \
  --new-str "<新状态>"
```

状态枚举：`待完成` → `进行中` → `已完成` / `需二次评审` / `已关闭`

### Step 7：逾期提醒（按需执行）

用户要求检查逾期时：

1. 重新读取待办表（Step 1）
2. 找出 完成时间 < 今日 且 状态 ≠ `已完成` / `已关闭` 的条目
3. 向责任人发送逾期提醒（同 Step 4 格式，标题改为 `⚠️ 逾期提醒`）
4. 询问用户是否将状态改为 `需二次评审`

### Step 9：状态自动同步（一键回填进度）

当用户要求同步进度时，扫描 Base 中所有「任务ID」非空且「状态」不是「已完成」的记录，查询对应飞书任务状态并回写：

**飞书任务状态 → Base 状态映射：**

| 飞书任务 completed_at | Base 状态 |
|---|---|
| 空（未完成） | 保持原状态不变 |
| 非空（已完成） | `已完成` |

**执行步骤：**

```bash
# Step 9-1: 读取所有有任务ID且未完成的记录
lark-cli base +record-list \
  --base-token "HgKEbPY2Zav9SlsPOREchbzBnxf" \
  --table-id "tblyPLlBAO88SYAq" \
  --format json \
  --filter-json '{"conjunction":"and","conditions":[{"field_name":"任务ID","operator":"isNotEmpty"}]}'

# Step 9-2: 对每条记录，查询飞书任务状态（注意：用 task tasks get，不是 task +get）
lark-cli task tasks get \
  --params '{"task_guid":"<guid>"}' \
  --format json
# 取 data.task.completed_at → 大于0表示已完成

# Step 9-3: 若已完成，更新 Base 状态字段
lark-cli base +record-upsert \
  --base-token "HgKEbPY2Zav9SlsPOREchbzBnxf" \
  --table-id "tblyPLlBAO88SYAq" \
  --record-id "<record_id>" \
  --json '{"状态":"已完成"}'
```

执行完毕后，向触发人汇报同步结果：
- ✅ 已完成 N 条（列出事项名）
- ⏳ 仍在进行 M 条
- ⚠️ 逾期未完成 K 条（列出事项名+责任人）

---

### Step 8：触发二次评审（按需执行）

当某条待办状态变为 `需二次评审` 时：

1. 提示：此条目需安排二次评审，建议调用 tech-review-meeting skill
2. 将该事项的描述作为新议题写入评审表格（Sheet1 或 Sheet2）：

```bash
lark-cli sheets +cells-set --url "$SHEET_URL" \
  --sheet-name "新技术评审内容收集" \
  --range "<下一空行的A:N范围>" \
  --cells '[{"values":[["", "<事项描述>", "", "...", "", "", "", "", "", "", "", "", "未开始", ""]]}]'
```

3. 输出提示，让用户运行 tech-review-meeting 安排新会议

---

## 错误处理

| 异常场景 | 处理方式 |
|---------|---------|
| 责任人不在飞书通讯录 | 记为"待手动分配"，任务照常创建但无 assignee |
| 纪要格式不标准（非表格） | 尝试读取 checkbox 格式的待办，提取文本 + @用户 |
| 任务创建失败 | 记录失败条目，其余继续；最后汇报 |
| 文档无待办章节 | 提示用户确认文档 URL 或纪要格式 |

---

## 完整运行示例

```
用户：请从 https://...doc/Wjsfd78VDoMNh8xCdLQc5nCdnze 提取待办并创建飞书任务

→ Step 1：读取到 5 条待完成事项
→ Step 2：解析责任人：张军(ou_xxx) / 方召(ou_yyy)
→ Step 3：创建 5 个飞书任务，关联对应责任人和截止日期
→ Step 4：发送 IM 通知给张军和方召
→ 结果：5条任务已创建，链接：...
```

---

## 与其他 Skill 的协作关系

```
tech-review-meeting  →  会议结束  →  lark-mm（生成纪要）
                                     ↓
                              tech-review-tracker（本 Skill）
                                     ↓
                         任务完成 / 需二次评审
                                     ↓
                              tech-review-meeting（循环）
```

---

<!-- TOKEN & COST -->
## 📊 Token & 费用参考

单次完整执行估算约 **3500 token**（读取纪要 ~800 + 联系人解析×3 ~300 + 任务创建×5 ~1500 + IM 通知 ~600 + 状态更新 ~300）。
详细历史用量见 [`records/cost.md`](records/cost.md)。

---

<!-- VERSION RECORDS -->
## 📝 版本记录

详见 [`records/CHANGELOG.md`](records/CHANGELOG.md)。当前版本：**v1.2.0**（2026-06-25）
