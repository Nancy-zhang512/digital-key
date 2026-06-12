---
name: lark-autoseq
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

---

## 二、获取文档所有标题及 Block ID

**每次修改前都必须重新执行本步骤获取最新 ID。**

```bash
lark-cli docs +fetch --api-version v2 \
  --doc "<文档URL或token>" \
  --detail with-ids 2>&1 | python3 -c "
import json, sys, re
data = json.load(sys.stdin)
content = data['data']['document']['content']
for m in re.finditer(r'<(h[123])[^>]*id=\"([^\"]+)\"[^>]*>([^<]+)</', content):
    print(f'{m.group(1)}  |  {m.group(2)}  |  {m.group(3)}')
"
```

输出示例：
```
h2  |  doxcnXXXXXX  |  2.1 硬件原型
h2  |  doxcnYYYYYY  |  2.2 算法验证
h3  |  doxcnZZZZZZ  |  3.1.1 子任务
```

---

## 三、将标题设为 H1/H2/H3 + 自动有序编号

上传 Markdown 后，按以下规则修正级别并加 `seq="auto"`：

| Markdown | Feishu 原始 | 目标 |
|----------|------------|------|
| `##` 一级章节 | H2 | `<h1 seq="auto" seq-level="auto">` |
| `###` 二级章节 | H3 | `<h2 seq="auto" seq-level="auto">` |
| `####` 三级章节 | H4 | `<h3 seq="auto" seq-level="auto">` |

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
# 格式："block_id:纯文字标题"（不含手动编号）
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

每次执行 `block_replace` 都会产生一个**全新的 block ID**，原 ID 立即失效。

```
❌ 用旧 ID 二次修改 → 接口返回 ok:true，但实际修改的是已删除的 block，变更丢失
✅ 正确做法：每轮操作前重新执行第二节命令，获取当前最新 ID
```

### 完整操作流程

```
1. 上传 Markdown（第一节）→ 拿到文档 token
2. +fetch --detail with-ids（第二节）→ 拿到所有标题的当前 block ID
3. 批量 block_replace（第三节 + 第四节）→ 同时修正级别、加 seq、去前缀
4. 如需二次调整 → 重新执行第二节获取新 ID，再执行第三节
```

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
