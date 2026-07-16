---
name: sch-data-prep
description: "原理图评审数据准备 — 网表提取/BOM匹配/物料系统批量查询，输出结构化JSON供评审使用"
compatibility: all
metadata:
  author: Nancy
  directories:
    - 1-sch
    - 2-component
    - 4-system
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

## 三、IT 物料系统 MCP 批量查询

调用 IT 物料系统 MCP: `http://192.168.29.113:8099/mcp`
接口: `mt_smart_substitute_import_query(materialCodes=[...], full=true)`

**分批规则**: 每次最多 20 个料号，循环直到全部查完。

| 返回字段 | 用途 |
|:---|:---|
| `model` (MPN) | 型号确认 |
| `preferGrade` (A/B) | 优选等级 |
| `materialLevel` (Q100/Q200) | 车规等级 |
| `substitutes[]` | 替代料 |
| `hasRisk` / `originCountry` | 供应风险 |
| `price` / `leadTime` | 成本与交期 |

查询结果写入: `1-sch/output/material_data.json`

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
             1-sch/output/material_data.json
→ 可执行 sch-review 开始评审
```
