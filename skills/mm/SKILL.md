---
name: mm
description: '会议纪要自动化工作流：根据飞书文档（会议记录）和/或飞书妙记（智能会议纪要），自动生成标准三段式飞书纪要文档（会议内容/待办事项/下次议题），并在用户明确要求时发送 HTML 格式邮件给全体参会人。USE FOR: 生成纪要、写会议纪要、整理会议记录、发纪要邮件。DO NOT USE FOR: 只读取文档内容、只搜索妙记、不需要产出纪要正文的查询类任务。'
compatibility: 需要已安装并完成认证的 lark-cli；依赖同一 skill 集中的 lark-shared、lark-doc、lark-minutes、lark-contact、lark-mail、lark-autoseq 等能力。
metadata:
  author: Nancy-zhang512
  knowledge-base: 无
  directories:
    skill: 'Skill 定义文件（SKILL.md）'
---

# 会议纪要自动化工作流

> **前置条件：** 先阅读 [`../lark-shared/SKILL.md`](../lark-shared/SKILL.md)，了解认证与权限处理。

---

## 触发场景

| 用户说的话 | 是否触发本 Skill |
|---|---|
| "根据这个文档/妙记帮我生成纪要" | ✅ |
| "整理会议记录，发给参会人" | ✅ |
| "写一个标准的会议纪要飞书文档" | ✅ |
| "把会议内容整理成邮件发出去" | ✅ |
| 只查看文档内容，不需要产出 | ❌ 用 lark-doc |
| 只搜索/下载妙记 | ❌ 用 lark-minutes |

---

## 标准工作流

### Step 1：获取原始素材

根据用户提供的链接，读取以下一种或两种素材：

#### 1a. 飞书文档（会议记录）

```bash
lark-cli docs +fetch --api-version v2 \
  --doc "<文档URL或token>" \
  --doc-format markdown
```

从返回 JSON 取 `data.document.content`，保存为原始素材。

若 `docs +fetch` 失败：

- 若同时有妙记素材，则继续使用妙记生成纪要
- 若没有其他素材，则**停止本次纪要生成流程**

#### 1b. 飞书妙记（智能会议纪要）

从妙记 URL 提取 `minute_token`（URL 末尾路径段），然后获取 AI 总结、待办、章节：

```bash
lark-cli vc +notes --minute-tokens <minute_token> --as user
```

> 若两份素材都有，合并内容后一并用于生成纪要。
>
> 若 `vc +notes` 失败：
> - 若同时有文档素材，则继续使用文档生成纪要
> - 若没有其他素材，则**停止本次纪要生成流程**

---

### Step 2：提取关键信息

从素材中提取：

| 字段 | 说明 | 提取来源 |
|------|------|---------|
| 会议标题 | 文档 title 或妙记标题 | docs +fetch / minutes get |
| 会议时间 | 文档正文或妙记时间 | 文档开头段落 |
| 参会人列表 | 文档正文或妙记参与者 | 文档开头或 `vc +notes` 返回的 `participants` |
| 会议内容 | 各议题讨论要点 | 正文 |
| 待办事项 | 负责人 + 事项 + 截止时间 | 正文中的 action items |
| 下次议题 | 待跟进/下次讨论的议题 | 正文末尾 |

> **重要**：待办事项需仔细检查，避免遗漏：
> - 正文各章节中隐含的 action items（如"X 负责 YY"）
> - 明确的截止时间说明

## 失败处理总则

以下场景必须按明确分支处理，**不要静默跳过，也不要假装成功**：

| 场景 | 处理规则 |
|---|---|
| `docs +fetch` 失败 | 若这是唯一素材来源，则停止生成纪要；若同时有妙记素材，则只用妙记继续 |
| `vc +notes` 失败 | 若这是唯一素材来源，则停止生成纪要；若同时有文档素材，则只用文档继续 |
| 两种素材都不可用 | **立即停止流程**，不要继续生成空纪要 |
| 纪要文档创建失败 | 不要继续写入、编号或发邮件 |
| 纪要文档写入失败 | 停止后续 auto-seq 与邮件流程，先告知用户文档内容未成功落地 |
| auto-seq 失败 | 保留已生成纪要正文，但不要假装编号已完成；直接告知用户“纪要已生成，但自动编号未完成” |
| 联系人搜索无邮箱结果 | 忽略没有明确邮箱的联系人；若全部都无邮箱，则停止邮件发送，仅保留纪要文档 |
| 草稿创建失败 | 不要继续发送邮件，保留纪要文档并告知用户邮件草稿未生成 |
| 草稿发送失败 | 仅保留草稿或草稿信息，不删除纪要文档，不自动重试发送 |

## 快路径原则

Darwin 视角下，`lark-mm` 最容易变慢的地方不是“生成纪要正文”，而是**无差别地执行 auto-seq、联系人搜索、邮件草稿/发送**。默认应按以下快路径运行：

1. **如果用户只要求“生成纪要 / 写纪要 / 整理会议内容”，默认只执行 Step 1-3。**
2. **只有当用户明确要求“发邮件 / 发给参会人 / 通知与会者 / 发送纪要”时，才进入 Step 4-5。**
3. **auto-seq 不是每次都必须执行。** 若纪要文档已经使用固定手写章节标题（如 `一、会议内容 / 二、待办事项 / 三、下次议题`），且用户未明确要求“飞书自动编号”，可直接跳过 auto-seq。
4. **联系人搜索必须批量一次完成**，不要对每个姓名单独查询。
5. **草稿只生成一次。** 正常情况下不要为了“再确认一下”重复创建草稿。

默认快路径：

```text
只生成纪要 → Step 1-3 → 结束
生成纪要并发邮件 → Step 1-3 → Step 4-5
```

---

### Step 3：在目标文档中生成标准纪要

#### 3a. 确定目标文档

- 若用户指定了目标文档 URL → 在该文档中写入
- 若用户未指定 → 新建文档：
  ```bash
  lark-cli docs +create --api-version v2 \
    --title "<会议标题>纪要" --as user
  ```

若目标文档创建失败：

- **不要继续写入纪要内容**
- **不要继续执行 auto-seq**
- **不要继续进入邮件流程**

#### 3b. 写入标准三段式结构

使用 `overwrite` 命令全量写入（或 `append` 追加到空文档）：

```bash
lark-cli docs +update --api-version v2 \
  --doc "<doc_url>" \
  --command overwrite \
  --doc-format markdown \
  --content "$(cat <<'MD'
# 一、会议内容

## <议题1>
- 要点1
- 要点2

## <议题2>
- 要点1

...（重复各议题）

# 二、待办事项

| No. | 事项 | 责任人 | 完成时间 | 状态 |
| --- | --- | --- | --- | --- |
| 1 | 完成 XX 工作 | 张三 | 下周五 | 待完成 |
| 2 | 整理 YY 文档 | 李四 | 7月初 | 待完成 |

# 三、下次议题

1. 议题A
2. 议题B
3. 议题C
MD
)"
```

若 `overwrite` / `append` 失败：

- **立即停止后续流程**
- 不再执行 auto-seq、联系人搜索或邮件草稿生成
- 先告知用户纪要正文未成功写入目标文档

#### 3c. 应用自动有序编号（auto-seq）

**速度优化规则**：

- 若当前纪要正文已经使用固定手写章节标题（例如 `一、会议内容 / 二、待办事项 / 三、下次议题`），且用户**没有明确要求飞书自动编号**，则默认**跳过 auto-seq**
- 只有以下场景才建议执行 auto-seq：
  1. 用户明确要求“自动编号 / 飞书编号”
  2. 文档存在多级标题，需要后续增删章节时自动重排编号
  3. 当前标题没有人工编号，阅读上需要补足层级编号

获取文档中所有标题 block ID，批量设置 `seq="auto"`：

```bash
# 获取标题 block ID
lark-cli docs +fetch --api-version v2 \
  --doc "<doc_url>" \
  --detail with-ids 2>&1 | python3 -c "
import json, sys, re
data = json.load(sys.stdin)
content = data['data']['document']['content']
for m in re.finditer(r'<(h[123])[^>]*id=\"([^\"]+)\"[^>]*>([^<]+)</', content):
    print(f'{m.group(1)}  |  {m.group(2)}  |  {m.group(3)}')
"

# 对每个标题执行（H1 示例，H2 同理）
lark-cli docs +update --api-version v2 \
  --doc "<doc_url>" \
  --command block_replace \
  --block-id "<block_id>" \
  --content '<h1 seq="auto" seq-level="auto">标题文字</h1>'
```

若 auto-seq 失败：

- **不要回滚已经写入的纪要正文**
- 直接保留当前纪要文档
- 告知用户“纪要正文已生成，但标题自动编号未完成”

---

### Step 4：获取参会人邮箱

**只有当用户明确要求发送邮件时，才执行本步骤。**

从文档正文或妙记参与者中提取参会人姓名，批量查询邮箱：

```bash
lark-cli contact +search-user \
  --queries "张三,李四,王五,..." \
  --as user 2>&1 | python3 -c "
import json, sys
d = json.load(sys.stdin)
for u in d.get('data', {}).get('users', []):
    print(u.get('name'), '|', u.get('enterprise_email') or u.get('email',''))
"
```

收集所有非空 `enterprise_email`（没有企业邮箱时可回退到 `email`），以逗号分隔备用。

处理规则：

- **联系人邮箱不全则忽略该联系人**，不要因为个别人缺邮箱而阻断整封纪要邮件。
- **不要猜测收件人邮箱**。搜索结果里没有邮箱、邮箱为空、或姓名匹配不唯一时，都不得自行拼接、推断或补全地址。
- 最终邮件只发送给**已确认且邮箱明确存在**的收件人。
- 若所有联系人都没有可用邮箱，则停止邮件发送流程，只保留纪要文档并告知用户原因。
- 若联系人搜索命中为空、姓名不唯一或邮箱字段为空，则**忽略该联系人**，不要阻断已有可用收件人的发送准备。

---

### Step 5：撰写 HTML 邮件并确认

#### 5a. 构建邮件正文（三段式 HTML）

**只有当用户明确要求发送邮件时，才执行本步骤。**

将纪要内容转为 HTML 格式，结构如下：

```html
<div style="font-family:sans-serif;font-size:14px;color:#222;line-height:1.8;max-width:760px">
  <p>各位好，</p>
  <p>以下是 <strong>{会议标题}</strong> 会议纪要，请查阅。
     在线文档链接：<a href="{doc_url}">点击查看完整纪要</a></p>
  <p style="color:#666;font-size:13px">会议时间：{时间} | 参会：{参会人}</p>
  <hr/>

  <h2 style="color:#1a56db">一、会议内容</h2>
  <!-- 各议题 h3 + ul 列表 -->

  <hr/>
  <h2 style="color:#1a56db">二、待办事项</h2>
  <table style="border-collapse:collapse;width:100%;font-size:13px">
    <thead>
      <tr style="background:#f0f4ff">
        <th style="border:1px solid #ccc;padding:7px 10px;text-align:left;width:40px">No.</th>
        <th style="border:1px solid #ccc;padding:7px 10px;text-align:left">事项</th>
        <th style="border:1px solid #ccc;padding:7px 10px;text-align:left">责任人</th>
        <th style="border:1px solid #ccc;padding:7px 10px;text-align:left">完成时间</th>
        <th style="border:1px solid #ccc;padding:7px 10px;text-align:left">状态</th>
      </tr>
    </thead>
    <tbody>
      <!--
        每条待办一行，示例：
        <tr>
          <td style="border:1px solid #ccc;padding:6px 10px">1</td>
          <td style="border:1px solid #ccc;padding:6px 10px">完成 XX 工作</td>
          <td style="border:1px solid #ccc;padding:6px 10px">张三</td>
          <td style="border:1px solid #ccc;padding:6px 10px">下周五</td>
          <td style="border:1px solid #ccc;padding:6px 10px">待完成</td>
        </tr>
        奇偶行交替背景：偶数行 tr 加 style="background:#fafafa"
      -->
    </tbody>
  </table>

  <hr/>
  <h2 style="color:#1a56db">三、下次议题</h2>
  <ol><!-- 每条下次议题 --></ol>

  <hr/>
  <p>完整纪要链接：<a href="{doc_url}">{doc_url}</a></p>
  <p style="color:#999;font-size:12px">请各负责人关注自己的待办事项，按时完成。谢谢！</p>
</div>
```

将 HTML 内容保存到本地文件（路径必须是相对路径）：

```bash
cat > ./minutes_email.html << 'HTMLEOF'
<!-- 上述 HTML 内容 -->
HTMLEOF
```

#### 5b. ⚠️ 发送前必须确认（高风险操作）

**在执行发送前，必须向用户展示以下信息并等待确认：**

```
📧 即将发送邮件
主题：{邮件主题}
收件人（共 N 人）：张三 <zhangsan@example.com>、李四 <lisi@example.com>、...
正文预览：[会议内容摘要 / 待办事项 N 条 / 下次议题 M 条]
纪要链接：{doc_url}

确认发送？
```

使用 `ask_user` 工具询问用户确认，**用户明确同意后方可继续**。在用户确认前：

- **不要发送邮件**
- **不要把草稿转为已发送**
- **不要删除纪要文档**

#### 5b-1. 用户取消发送时

若用户选择**不发送**，立即使用 `ask_user` 追问是否需要删除刚生成的纪要文档：

```
纪要文档已生成但邮件已取消，是否删除该纪要文档？
选项：[保留文档] [删除文档]
```

- 只有在用户**明确选择删除**后，才可执行以下命令将文档移入回收站：
  ```bash
  lark-cli drive +delete \
    --file-token <doc_token> \
    --type docx \
    --as user --yes
  ```
- 用户选择**保留**：告知文档链接，流程结束。

#### 5c. 先保存草稿，再决定是否发送

先保存草稿，不要直接发送：

```bash
# 注意：必须在包含 HTML 文件的目录下执行
cd <html文件所在目录>

lark-cli mail +send --as user \
  --to "<收件人邮箱，逗号分隔>" \
  --subject "【会议纪要】{会议标题}" \
  --body-file minutes_email.html
```

若草稿创建失败：

- **不要继续执行 `drafts send`**
- 保留已生成的纪要文档
- 直接告知用户邮件草稿未生成成功

保存草稿后，再在用户已明确确认发送的前提下执行：

```bash
lark-cli mail user_mailbox.drafts send \
  --params '{"user_mailbox_id":"me","draft_id":"<draft_id>"}'
```

处理规则：

- **不要在未确认时发送**。即使草稿已生成，也只能在用户明确确认后调用 `drafts send`。
- 若发送动作需要额外高风险确认（例如 exit code 10），也必须以**用户已明确同意发送**为前提。
- **邮件发送失败时，只需要保留草稿**，把草稿信息或打开链接反馈给用户即可；**不要删除草稿、不要删除纪要文档、不要自动重试发送**。

---

## 产物规范

| 产物 | 说明 |
|------|------|
| 飞书纪要文档 | 标准三段式；按需启用 auto-seq 有序编号 |
| 邮件 | HTML 富文本，三段内容 + 纪要链接 |

---

## 关键原则

### 待办事项不遗漏
除正文明确列出的待办外，还需检查：
- 各章节中 "X 负责 / 由 X 来 / X 安排" 等隐式 action item
- 带时间节点的任务（如"下周""7月底"）

### 参会人来源优先级
1. 妙记 `vc +notes` 返回的 `participants`（最准确）
2. 文档正文中的参会人列表（如 "参会：A、B、C"）
3. 文档中 `<cite type="user">` 标签里出现的人名

### 邮件发送安全
- **必须先确认再发送**，不允许静默发送
- **不要猜测收件人邮箱**；没有明确邮箱的联系人直接忽略
- 收件人超过 5 人时，向用户列出完整名单
- **未得到用户明确确认时，不要删除纪要文档**
- 邮件发送失败时，**仅保留草稿**，等待用户后续处理
- 保留邮件 HTML 文件，方便事后核查

### 执行速度优化
- **不要在“只生成纪要”的请求里默认进入邮件流程**
- **不要在已有稳定手写章节编号时默认再跑 auto-seq**
- 联系人查询使用**一次批量查询**，不要逐人循环调用
- 草稿创建成功后，未发生实质内容变更时**不要重复生成草稿**

### 🛑 STOP / 不要这样做

- **不要在原始素材为空时继续生成纪要**
- **不要在纪要文档创建或写入失败后继续 auto-seq 或发邮件**
- **不要假装 auto-seq 已成功完成**
- **不要猜测收件人邮箱**
- **不要在草稿创建失败后继续发送**
- **不要在邮件发送失败后自动重试或删除纪要文档**

---

## 权限

| 操作 | 所需 scope |
|------|-----------|
| 读取飞书文档 | `docx:document:readonly` |
| 创建/编辑飞书文档 | `docx:document` |
| 读取妙记纪要 | `minutes:minutes:readonly`、`vc:meeting:readonly` |
| 搜索联系人 | `contact:user.base:readonly` |
| 发送邮件 | `mail:mail.send` |

---

## 任务结束报告

每次任务完成后，必须输出以下信息，并将记录追加到 `records/cost.md`：

```
📊 Token 使用情况
- 输入 Token：xxx
- 输出 Token：xxx
- 合计 Token：xxx
- 估算费用：$x.xxxx USD（Claude Sonnet 4.6：$3/MTok 输入，$15/MTok 输出）
```
