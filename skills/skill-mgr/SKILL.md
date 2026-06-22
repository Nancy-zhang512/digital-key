---
name: skill-mgr
description: 'Skill 生命周期管理：在 digital-key 仓库中重命名/新增自开发 Skill、更新飞书 Skill 管理库（多维表格）、提交 GitHub。USE FOR: rename skill、move skill to category、add self-dev skill to repo、batch add token-report + records dir。DO NOT USE FOR: 创建全新 Skill 内容（用 skill-maker）、编辑飞书文档正文（用 lark-doc）。'
compatibility: 需要 git 已配置 SSH 到 GitHub；需要已安装并完成认证的 lark-cli（--as user）。
metadata:
  author: Nancy-zhang512
  knowledge-base: https://yftech2012.feishu.cn/wiki/Mj4LwwmIViOFYMkYkCucBYsUnwf
  directories:
    skill: 'Skill 定义文件（SKILL.md）'
    repo: '/Users/yf/nancy/0-repo/digital-key/skills'
---

# Skill 生命周期管理（skill-mgr）

管理 `digital-key` 自开发 Skill 的完整生命周期：重命名、目录归类、同步 GitHub、更新飞书 Skill 管理库。

---

## 常量

| 常量 | 值 |
|------|-----|
| Repo Skills 目录 | `/Users/yf/nancy/0-repo/digital-key/skills` |
| 飞书 Skill 管理库 | `https://yftech2012.feishu.cn/wiki/Mj4LwwmIViOFYMkYkCucBYsUnwf` |
| Base Token | `BFVAbXEVva3R7msfBhYcnoQOnwb` |
| Table ID | `tbla4Np3bRzFCMu6` |
| 目录选项 | `飞书skill` / `github skill` / `自开发skill` / `其他` |

---

## 场景一：重命名 Skill

### Step 1：重命名 Repo 目录

```bash
cd /Users/yf/nancy/0-repo/digital-key/skills
mv <old-name> <new-name>
```

若 Skill 来自外部（如 `.agents/skills/`），改为复制：

```bash
cp -r /Users/yf/.agents/skills/<old-name> /Users/yf/nancy/0-repo/digital-key/skills/<new-name>
```

### Step 2：更新 SKILL.md `name` 字段

编辑 `<new-name>/SKILL.md`，将 `name: <old-name>` 改为 `name: <new-name>`。

### Step 3：提交 GitHub

```bash
cd /Users/yf/nancy/0-repo/digital-key
# 重命名场景（旧目录变为已删除）
git add skills/<new-name>/ skills/<old-name>/SKILL.md
# 新增场景（无旧目录）
git add skills/<new-name>/

git commit -m "rename skill: <old-name> → <new-name>"
git push origin main
```

### Step 4：更新飞书 Skill 管理库

**4a. 查找目标记录 ID**

```bash
lark-cli base +record-list \
  --base-token BFVAbXEVva3R7msfBhYcnoQOnwb \
  --table-id tbla4Np3bRzFCMu6 \
  --as user --format json 2>&1 | python3 -c "
import json, sys
data = json.load(sys.stdin)
d = data['data']
records, fields, rids = d['data'], d['fields'], d['record_id_list']
name_idx = fields.index('Skill名称')
for rec, rid in zip(records, rids):
    if rec[name_idx] == '<old-name>':
        print(f'record_id: {rid}')
        print(f'fields: {rec}')
"
```

**4b. 更新记录（名称 + 调用 + 目录）**

```bash
lark-cli base +record-upsert \
  --base-token BFVAbXEVva3R7msfBhYcnoQOnwb \
  --table-id tbla4Np3bRzFCMu6 \
  --as user --format json \
  --record-id <record_id> \
  --json '{"Skill名称":"<new-name>","调用":"skill: \"<new-name>\"","目录":"<目录>"}'
```

> ⚠️ `--json` 的值必须是 **flat Map**，不要包裹 `{"fields": ...}`。

---

## 场景二：批量为自开发 Skill 添加标准结构

为自开发 Skill 统一补充任务结束报告指令 + `records/` 目录（CHANGELOG + cost）：

```python
import os

SKILLS_DIR = "/Users/yf/nancy/0-repo/digital-key/skills"
TARGET_SKILLS = ["<skill-1>", "<skill-2>"]  # 替换为目标 skill 列表

TOKEN_SECTION = """
---

## 任务结束报告

每次任务完成后，必须输出以下信息，并将记录追加到 `records/cost.md`：

\```
📊 Token 使用情况
- 输入 Token：xxx
- 输出 Token：xxx
- 合计 Token：xxx
- 估算费用：$x.xxxx USD（Claude Sonnet 4.6：$3/MTok 输入，$15/MTok 输出）
\```
"""

CHANGELOG_INIT = """# Changelog

所有重要变更记录于此，格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)。

---

## [1.0.0] - {date}

### Added
- 初始版本发布
- 增加任务结束 token 使用 & 费用报告
"""

COST_INIT = """# Token 使用记录

| 日期 | 任务描述 | 输入 Token | 输出 Token | 合计 | 估算费用(USD) |
|------|----------|-----------|-----------|------|-------------|
"""

from datetime import date
today = date.today().isoformat()

for skill in TARGET_SKILLS:
    skill_dir = os.path.join(SKILLS_DIR, skill)
    records_dir = os.path.join(skill_dir, "records")
    skill_md = os.path.join(skill_dir, "SKILL.md")

    # 追加到 SKILL.md（幂等：检查是否已存在）
    with open(skill_md, "r") as f:
        if "任务结束报告" not in f.read():
            with open(skill_md, "a") as fw:
                fw.write(TOKEN_SECTION)

    # 创建 records/ 目录和文件（幂等）
    os.makedirs(records_dir, exist_ok=True)
    changelog = os.path.join(records_dir, "CHANGELOG.md")
    if not os.path.exists(changelog):
        with open(changelog, "w") as f:
            f.write(CHANGELOG_INIT.format(date=today))
    cost = os.path.join(records_dir, "cost.md")
    if not os.path.exists(cost):
        with open(cost, "w") as f:
            f.write(COST_INIT)

    print(f"[OK] {skill}")
```

提交变更：

```bash
cd /Users/yf/nancy/0-repo/digital-key
git add skills/
git commit -m "feat(self-dev): add token-report + records/ to skills"
git push origin main
```

---

## 飞书 Skill 管理库字段说明

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| Skill名称 | 文本 | Skill 唯一标识符 | `mm` |
| 入参 | 文本 | 调用时需提供的上下文提示 | `{"skill":"mm"}；随后提供会议文档...` |
| 调用 | 文本 | 触发 Skill 的标准格式 | `skill: "mm"` |
| 目录 | 单选 | 分类 | `自开发skill` |
| 用途 | 文本 | 功能一句话说明 | `会议纪要自动化工作流` |
| 负责人 | 文本 | 维护者 | `待分配` |

---

## 目录结构规范

每个自开发 Skill 的标准目录结构：

```
skills/<skill-name>/
  SKILL.md            # Skill 主文件，末尾含「任务结束报告」章节
  records/
    CHANGELOG.md      # 版本历史（不体现在 SKILL.md 内）
    cost.md           # Token 使用 & 费用记录
  references/         # 可选：API 参考、命令示例
```

---

## 失败处理

| 场景 | 处理方式 |
|------|---------|
| `git push` 失败 | 检查 SSH key 或 remote；`git pull --rebase` 后重推 |
| bitable 更新报 `800010701` | 检查 `--json` 不要包裹 `{"fields":...}`，使用 flat Map |
| `record_id` 找不到 | 用 `+record-list` 全量扫描，按 `Skill名称` 字段匹配 |
| 重命名后旧 record_id 失效 | 记录永远不变；只更新字段值，不需要重建记录 |

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
