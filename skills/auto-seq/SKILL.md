---
name: auto-seq
version: 1.0.0
description: "飞书文档标题自动有序编号工具：将任意飞书文档（包括从本地 Markdown 上传的文档）的标题统一设为 H1/H2/H3 + seq=auto 自动有序编号，并自动去除标题内手动数字前缀，避免重复编号。当用户需要上传 Markdown 文档并整理标题格式、或将已有飞书文档标题改为有序列表时使用。"
metadata:
  requires:
    bins: ["lark-cli", "python3"]
---

# 飞书文档标题自动有序编号（AutoSeq）

> **前置条件：** 先阅读 [`../lark-shared/SKILL.md`](../lark-shared/SKILL.md)。  
> 所有 `docs` 操作必须携带 `--api-version v2`。

---

## 一、上传本地 Markdown 为飞书云文档

```bash
lark-cli docs +create --api-version v2 \
  --doc-format markdown \
  --content "$(cat /path/to/your-file.md)"
```

返回新文档 URL，如：`https://yftech2012.feishu.cn/docx/<token>`

> ⚠️ **Markdown → Feishu 标题映射规则**  
> `#` → title，`##` → H2，`###` → H3  
> 上传后标题级别会偏移，必须用第三节的 `block_replace` 修正（`##` 改为 H1，`###` 改为 H2）
>
> **默认行为**：如果用户是为了整理标题而上传本地 Markdown 到飞书云文档，上传成功后**默认继续执行后续自动编号与标题修正流程**，无需再次询问是否修改。

---

## 二、获取文档所有标题及 Block ID

**默认快路径**：一轮自动编号默认只执行 **1 次 `+fetch`** 来获取当前标题和 block ID。  
**不要**因为同一轮里要改多个不同标题，就在每改一个标题后重新 `+fetch`。

只有以下场景才需要重新执行本步骤刷新最新 ID：

1. 开始**新一轮**修改
2. 某次 `block_replace` **超时 / 失败 / 返回不确定**，无法确认该标题是否已改成功
3. 用户提供的是**旧 block ID**
4. 需要对**同一个已经改过的标题**再改一次

若 `+fetch` 失败：

1. **立即重试 1 次**
2. 若第 2 次仍失败，则**放弃本轮修改**，不要继续执行 `block_replace`

```bash
lark-cli docs +fetch --api-version v2 \
  --doc "<文档URL或token>" \
  --detail with-ids 2>&1 | python3 -c "
import json, sys, re
data = json.load(sys.stdin)
content = data['data']['document']['content']
for m in re.finditer(r'<(h[123])([^>]*)id=\"([^\"]+)\"([^>]*)>(.*?)</', content, re.S):
    attrs = (m.group(2) + m.group(4))
    text = re.sub(r'<[^>]+>', '', m.group(5)).strip()
    seq = 'seq-auto' if 'seq=\"auto\"' in attrs else 'no-seq'
    print(f'{m.group(1)}  |  {seq}  |  {m.group(3)}  |  {text}')
"
```

输出示例：
```
h2  |  no-seq    |  doxcnXXXXXX  |  2.1 硬件原型
h2  |  seq-auto  |  doxcnYYYYYY  |  算法验证
h3  |  no-seq    |  doxcnZZZZZZ  |  3.1.1 子任务
```

解析规则：

- 若本次 `+fetch` 成功，但**标题解析不到任何 H1/H2/H3 block**，则重新执行第二节命令再试 **1 次**
- 若第 2 次仍解析不到标题，则**放弃修改**
- 若 `block` 列表明显异常，或标题层级识别不完整到无法安全判断映射关系，则**可以不执行修改**，直接把现状告知用户
- 若标题已经是**目标层级**、已经带 `seq="auto"`，且标题文字里**没有手动数字前缀**，则加入 **SKIP** 列表，不进入更新队列
- 只有“层级不对 / 缺少 `seq=\"auto\"` / 标题仍带手动数字前缀”的标题，才加入 **NEED_UPDATE** 列表

## 快路径原则

正常场景优先使用以下快路径：

1. `+fetch` 1 次，解析出全部标题
2. 先把标题分成 **SKIP** 和 **NEED_UPDATE**
3. **仅对 NEED_UPDATE 执行 `block_replace`**
4. 若本轮全部成功，**直接结束**；不要为了“确认一下”再强制全量 `+fetch`

只有在**异常场景**（超时、失败、用户要求核验、准备继续第二轮修改）时，才进行额外回读

## 🔴 CHECKPOINT：标题列表有效后再继续

进入 `block_replace` 前，必须先确认：

1. `+fetch` 已成功返回
2. 已成功解析到当前文档的标题 block 列表
3. 标题层级足够完整，能够安全判断 H1 / H2 / H3 的目标映射

若任一条件不成立：

- **不要继续执行标题修改**
- 直接告知用户当前标题列表不可安全使用
- 结束本轮自动编号流程

---

## 三、将标题设为 H1/H2/H3 + 自动有序编号

上传 Markdown 后，按以下规则修正级别并加 `seq="auto"`：

| Markdown | Feishu 原始 | 目标 |
|----------|------------|------|
| `##` 一级章节 | H2 | `<h1 seq="auto" seq-level="auto">` |
| `###` 二级章节 | H3 | `<h2 seq="auto" seq-level="auto">` |
| `####` 三级章节 | H4 | `<h3 seq="auto" seq-level="auto">` |

**执行优化规则**：

- 默认只更新 **NEED_UPDATE** 列表，**不要对所有标题盲改**
- 已经是目标层级、已带 `seq="auto"`、且无手动编号前缀的标题，直接跳过
- 正常批量修改时，沿用本轮 `+fetch` 得到的这一批 block ID 即可；**不要在每成功改 1 个标题后就重新 fetch**

### 单个标题

```bash
lark-cli docs +update --api-version v2 \
  --doc "<文档URL或token>" \
  --command block_replace \
  --block-id "<block_id>" \
  --content '<h1 seq="auto" seq-level="auto">标题文字</h1>'
```

### 批量更新（Shell 循环）

```bash
# 仅放 NEED_UPDATE 项；格式："block_id:纯文字标题"（不含手动编号）
IDS=(
  "doxcnAAA:阶段零 项目启动"
  "doxcnBBB:任务一 硬件选型"
  "doxcnCCC:里程碑汇总"
)

for item in "${IDS[@]}"; do
  id="${item%%:*}"
  text="${item##*:}"
  echo -n "Updating $id ($text) ... "
  lark-cli docs +update --api-version v2 \
    --doc "<文档URL或token>" \
    --command block_replace \
    --block-id "$id" \
    --content "<h1 seq=\"auto\" seq-level=\"auto\">${text}</h1>" \
    2>&1 | python3 -c "import json,sys; d=json.load(sys.stdin); print('ok' if d.get('ok') else d)"
done
```

H2 子标题同理，将 `h1` 替换为 `h2`。

## 🔴 CHECKPOINT：批量修改前确认

在执行单个或批量 `block_replace` 前，必须先确认：

1. 当前使用的是**本轮有效的 block ID**
2. 标题文字已经去掉手动数字前缀
3. 本轮修改的目标层级（H1 / H2 / H3）已判断清楚

若任一条件不成立：

- **不要执行 `block_replace`**
- 先刷新 block ID 或修正标题文本
- 无法修正时直接放弃本轮修改

---

## 四、去除标题内手动数字前缀

当标题文字含有手动编号（如 `2.4 预研报告交付`），同时启用 `seq="auto"` 后，会显示重复编号（如 `3.4 2.4 预研报告交付`）。

**做法：在填写第三节的 `text` 时，直接去掉前缀数字，只保留纯文字。**

```bash
# ❌ 错误：保留手动前缀
--content '<h2 seq="auto" seq-level="auto">2.4 预研报告交付</h2>'

# ✅ 正确：去掉前缀，只保留文字
--content '<h2 seq="auto" seq-level="auto">预研报告交付</h2>'
```

> 一次 `block_replace` 可同时完成：修正标题级别 + 加 seq + 去除前缀，**无需分步操作**。

---

## 五、⚠️ 关键注意事项

### block_replace 每次产生新 Block ID

每次执行 `block_replace` 都会让**被修改的那个标题块**产生一个**全新的 block ID**，该标题原 ID 立即失效。

```
❌ 用旧 ID 二次修改 → 接口返回 ok:true，但实际修改的是已删除的 block，变更丢失
✅ 正确做法：如果还要继续修改同一个标题，先重新执行第二节命令，获取当前最新 ID
```

**速度关键点**：

- 正在修改 **A 标题** 时，A 的旧 ID 会失效
- **未被修改的其他标题**，其本轮拿到的 block ID 仍可继续使用
- 因此，同一轮里批量改多个**不同标题**时，默认**不需要每改一个就重新 fetch**
- 只有在**同一个标题要改第二次**，或某次返回**超时 / 不确定结果**时，才必须重新 fetch

如果用户拿**旧的 block ID**（例如上一轮操作前保存的旧 ID）继续修改，也要按同样规则处理：

1. **不要直接沿用旧 ID 继续改**
2. 先重新执行第二节，获取最新 block ID
3. 再用新的 block ID 执行 `block_replace`
4. 若拿不到新的 block ID，则放弃本轮修改

### 完整操作流程

```
1. 上传 Markdown（第一节）→ 拿到文档 token
2. +fetch --detail with-ids（第二节）→ 拿到所有标题的当前 block ID
3. 分出 SKIP / NEED_UPDATE → 只保留 NEED_UPDATE
4. 批量 block_replace（第三节 + 第四节）→ 同时修正级别、加 seq、去前缀
5. 如需二次调整同一标题 / 有异常返回 / 用户要求核验 → 重新执行第二节获取新 ID，再执行第三节
```

失败处理补充：

```
1. +fetch 失败 → 立即重试 1 次；仍失败则放弃
2. 标题解析不到 → 重新 fetch + 解析 1 次；仍失败则放弃
3. block 列表异常 / 标题层级识别不完整 → 可不执行修改
4. 用户提供旧 block ID → 必须先刷新最新 block ID，再继续修改
5. 正常批量全部成功 → 默认直接结束，不强制做第二次全量 fetch
```

### 🛑 STOP / 不要这样做

- **不要直接沿用旧 block ID 继续修改**
- **不要在 `+fetch` 失败后继续执行 `block_replace`**
- **不要在标题解析为空时强行推断标题层级**
- **不要在标题层级识别不完整时批量修改整篇文档**
- **不要保留标题里的手动数字前缀再叠加 `seq=\"auto\"`**
- **不要对已经正确的标题重复执行 `block_replace`**
- **不要在同一轮里每改一个标题就强制重新 `+fetch`**
- **不要把上传云文档后的自动修改理解为“无条件必须修改”**；只有在标题列表可安全解析时才继续

### seq="auto" 编号效果

| 层级 | 效果 |
|------|------|
| H1 seq="auto" | 1、2、3… |
| H2 seq="auto" | 1.1、1.2、2.1、2.2… |
| H3 seq="auto" | 1.1.1、1.1.2… |

---

## 权限

| 操作 | 所需 scope |
|------|-----------|
| 读取飞书文档 | `docx:document:readonly` |
| 创建飞书文档 | `docx:document` |
| 编辑飞书文档块 | `docx:document` |

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
