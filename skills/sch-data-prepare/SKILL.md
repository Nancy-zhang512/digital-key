---
name: sch-data-prepare
description: "原理图评审数据准备 — 网表提取/BOM匹配/物料系统批量查询，输出结构化JSON供评审使用"
compatibility: all
metadata:
  author: Nancy
  directories:
    - 1-sch
    - 1-sch/output
    - 2-component
    - 4-system
    - scripts
---

# 原理图数据准备 SKILL

> **职责**: 评审前数据就绪，产出 `schematic_data.json` + `material_data.json`
> **下游**: 产出物直接供 `sch-review` skill 使用

---

## 一、数据清单检查

启动时逐项确认以下文件是否存在，缺失则提示用户补充后再继续。

| # | 数据项 | 路径 | 必需 |
|:-:|:---|:---|:---:|
| 1 | 网表文件 | `1-sch/*.net / *.asc / *.edn` | 🔴 |
| 2 | BOM xlsx | `1-sch/*.xlsx` | 🔴 |
| 3 | 原理图 PDF | `1-sch/*.pdf` | 🔴 |
| 4 | 关键IC规格书 | `2-component/*.pdf` | 🟡 |
| 5 | 系统框图/电源树 | `4-system/*` | 🟡 |

> **网表导出方法**: OrCAD → Tools → Create Netlist → EDIF 2.0 → 导出 `.net` 到 `1-sch/`

---

## 二、网表提取 → JSON

运行提取脚本，将网表 + BOM 合并为结构化 JSON：

```
scripts/extract_from_files.py
→ 1-sch/output/schematic_data.json
  ├── parts[]:  位号 / 类型 / 封装 / 型号 / 料号
  ├── nets[]:   网络名 / 类型 / 连接引脚列表
  └── meta:     项目名 / 页数 / 提取时间
```

**验收标准**:
- BOM 匹配率 = 100%（位号全部命中）
- parts 数量与原理图元件数一致
- 若匹配率 < 100%，列出未匹配位号，提示用户修正 BOM 后重跑

---

## 三、IT 物料系统 MCP 批量查询 → RAG 切片

调用 IT 物料系统 MCP: `http://192.168.29.113:8099/mcp`
接口: `mt_smart_substitute_import_query(materialCodes=[...], full=true)`

**分批规则**: 每次最多 20 个料号，循环直到全部查完。

查询完成后，将结果生成 **JSONL 格式 RAG 知识库切片**，写入 `1-sch/output/material_data.jsonl`，每行一条物料记录：

```json
{
  "id": "material::<料号>",
  "source": "IT物料系统MCP",
  "category": "material",
  "materialCode": "料号",
  "model": "MPN型号",
  "preferGrade": "A/B/C",
  "materialLevel": "Q100/Q101/Q200",
  "substitutes": ["替代料号1", "替代料号2"],
  "hasRisk": true/false,
  "originCountry": "国家",
  "price": 0.00,
  "leadTime": "周数",
  "text": "料号 <xxx> | 型号 <MPN> | 车规 <Q100> | 优选级 <A> | 替代料 <N个> | 原产地 <CN> | 价格 <¥x.xx>"
}
```

> `text` 字段为自然语言摘要，供 sch-review 评审时 RAG 检索使用。
> 若 MCP 无法连接，跳过此步并在评审报告中标注「物料数据待补充」。

---

## 四、输出确认

完成后输出数据摘要：

```
✅ 数据准备完成
- 元件数:    xxx 个
- 网络数:    xxx 条
- BOM匹配率: 100%
- 物料查询:  xxx / xxx 料号（x 批次）
- 输出文件:  1-sch/output/schematic_data.json
             1-sch/output/material_data.jsonl  (RAG切片，每行一条物料)
→ 可执行 sch-review 开始评审
```
