---
name: sch-review
description: "原理图设计评审 — 以资深硬件工程师视角，基于RAG知识库执行11模块全流程评审并输出报告"
compatibility: all
metadata:
  author: Nancy
  knowledge-base: references/
  directories:
    - 1-sch
    - 2-component
    - 3-platform
    - 4-system
    - 5-guideline
    - 6-history
    - 8-output
---

# 原理图设计评审 SKILL

> **前置条件**: 已执行 `sch-data-prep`，产出 `1-sch/output/schematic_data.json` + `material_data.json`
> **评审框架**: 11 大模块，依据 `references/guideline/` 知识库执行
> **报告输出**: `8-output/`，Markdown + Word 双格式

---

## 一、角色定义

执行评审时，AI 扮演「**CMS 产品线资深硬件工程师**」角色：
- 通过 `references/platform/` 和 `references/system/` 建立对待评审产品的完整背景认知
- 通过 `references/guideline/` 和 `references/history/` 掌握公司规范与历史教训
- 评审判断以工程师经验 + 规范依据双重支撑，不只是机械对条目
- 本地数据不足时，主动从网络获取规格书/行业标准补充

---

## 二、上下文加载（自动执行）

启动评审时按顺序加载以下知识库，建立评审上下文：

| 步骤 | 数据来源 | 目的 |
|:---:|:---|:---|
| ① | `1-sch/output/schematic_data.json` | 加载元件表 + 网络表 |
| ② | `1-sch/output/material_data.json` | 加载物料参数（车规/优选级/替代料） |
| ③ | `references/platform/*.jsonl` | 了解产品平台背景 |
| ④ | `references/system/*.jsonl` | 读取 SRS / 电源树 / 参数计算 |
| ⑤ | `references/guideline/*.jsonl` | 加载评审规则知识库 |
| ⑥ | `references/component/*.jsonl` | 关键 IC 规格书（按需检索） |
| ⑦ | `references/history/*.jsonl` | 历史问题库（若有） |

---

## 三、评审执行：11 大模块

按 M1 → M11 顺序逐模块执行，每模块：
1. 从 `references/guideline/` 检索对应规则
2. 结合 `schematic_data.json` 做判断
3. 输出每项结果：✅ 通过 / ⚠️ 建议整改 / ❌ 必须整改

| 模块 | 名称 | 主要规则来源 |
|:---:|:---|:---|
| M1 | 原理图制图规范 | `WI-RD-058_原理图设计规范_B0.jsonl` |
| M2 | 电源系统评审 | `WI-RD-070_车载产品电源设计规范_A0.jsonl` |
| M3 | 核心 IC 评审 | `references/component/*.jsonl`（按 IC 检索） |
| M4 | 信号完整性 | `WI-RD-060_流媒体摄像头硬件设计规范A1.jsonl` |
| M5 | EMC 设计 | `WI-RD-060.jsonl` + ISO 16750 / CISPR 25（网络补充） |
| M6 | 降额校核 | `WI-RD-071_元器件降额设计规范_A0.jsonl` |
| M7 | 物料评审 | `material_data.json`（车规/优选级/生命周期） |
| M8 | CBB 覆盖评审 | `WI-RD-058-004CMS_CAM原理图设计评审CheckListA1.jsonl` |
| M9 | DFX 评审 | `WI-RD-058.jsonl` + DFM 规则（网络补充） |
| M10 | 电气连接检测 | `schematic_data.json` 自动分析 |
| M11 | 关键参数计算 | `system/CMS054项目_A1_关键参数计算*.jsonl` |

> **详细检查项**: 见 `references/guideline/WI-RD-058-004CMS_CAM原理图设计评审CheckListA1.jsonl`
> **降额明细**: 按 `WI-RD-071` 逐器件校核，输出降额明细表

---

## 四、网络数据补充（兜底）

当本地知识库无法覆盖某检查项时：
- 优先搜索 IC 官方 datasheet（TI / Maxim / NXP 官网）
- 参考 ISO 16750（车载环境）、CISPR 25（车载 EMC）
- 明确标注数据来源，不凭空推断

---

## 五、报告输出

按 `references/templates/report-template.md` 模板填充内容，执行 `scripts/generate_word.py` 转 Word，输出到 `8-output/`。

| 章节 | 内容 |
|:---|:---|
| 一、评审概览 | 11 模块评分汇总表 + 设计基本信息 |
| 二、🔴 高风险项 | 必须整改清单（问题描述 + 整改建议） |
| 三、🟡 中风险项 | M1~M11 逐模块详细结果 |
| 四、产品专项 | 产品定制化检查项 |
| 五、电源树 | ASCII 电源拓扑图 |
| 六、关键IC清单 | 型号/车规/优选级/替代料/价格 |
| 七、评审结论 | 综合评定 + 行动项清单（P0/P1/P2/P3） |
| 八、物料风险 | 高/中/低风险物料汇总 |

