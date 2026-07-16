# RAG 知识库索引

> **格式**: JSONL（每行一个独立 JSON chunk）
> **总量**: 7,923 chunks，17 个文件，覆盖元件/平台/系统/规范四大类
> **更新**: 2026-07-16

---

## 目录结构

```
references/
├── index.md          ← 本文件（知识库总索引）
├── component/        # IC 元件规格书 Datasheet
├── platform/         # 平台整体方案
├── system/           # 系统设计文档（SRS/框图/参数表）
└── guideline/        # 硬件设计规范与评审标准
```

## JSONL 字段说明

每行记录格式：

```json
{
  "id":       "<source>::p<page>::c<chunk_id>",
  "source":   "原始文件相对路径",
  "category": "component | platform | system | guideline",
  "page":     "页码（PDF）/ Sheet名（xlsx）/ 幻灯片编号（pptx）",
  "chunk_id": 0,
  "text":     "chunk 正文内容"
}
```

---

## 📦 component/ — 元件规格书

| JSONL 文件 | 器件说明 | 原始文件 | Chunks |
|:---|:---|:---|:---:|
| `124301750301_DC-DC_TI_LP8867CQPWPRQ1.jsonl` | LP8867 LED Driver (4CH, AEC-Q100) | PDF | 117 |
| `124302790301_DC-DC_TI_LMR33630AQRNXRQ1.jsonl` | LMR33630 降压 DC-DC (3A, AEC-Q100) | PDF | 144 |
| `128100650301_视频转换IC_串化解串__MAXIM_MAX96714FGTJVY_T.jsonl` | MAX96714 GMSL2 解串器 (ASIL-B) | PDF | 549 |
| `128101420301_视频IC_TECHPOINT_TP6805-PA.jsonl` | TP6805 LCD 控制器 | PDF | 404 |
| `S32K-RM.jsonl` | S32K MCU 参考手册（完整版） | PDF | 6,092 |

## 🏗️ platform/ — 平台方案

| JSONL 文件 | 内容说明 | 原始文件 | Chunks |
|:---|:---|:---|:---:|
| `流媒体后视镜平台方案-20260313.jsonl` | 流媒体后视镜平台整体方案 | PPTX | 33 |

## 🖥️ system/ — 系统设计文档

| JSONL 文件 | 内容说明 | 原始文件 | Chunks |
|:---|:---|:---|:---:|
| `CMS028-A1_System_Requirement_Specification.jsonl` | CMS028 系统需求规格书 (SRS) | DOCX | 312 |
| `CMS054-A1_V1系统框图及电源框图_A1.jsonl` | CMS054 系统框图 & 电源架构图 | PDF | 7 |
| `CMS054-A1项目_硬件技术规格书_V1_0_20251016.jsonl` | CMS054 硬件技术规格书 | XLSX | 16 |
| `CMS054-A1项目_硬件设计方案书_V1_00_20251026.jsonl` | CMS054 硬件设计方案书 | XLSX | 18 |
| `CMS054项目_A1_关键参数计算_V1_20251212.jsonl` | CMS054 关键参数计算表 | XLSX | 110 |
| `流媒体后视镜平台方案-20260313.jsonl` | 平台方案（系统目录副本） | PPTX | 33 |

## 📋 guideline/ — 设计规范

| JSONL 文件 | 内容说明 | 原始文件 | Chunks |
|:---|:---|:---|:---:|
| `WI-RD-058_原理图设计规范_B0.jsonl` | 原理图制图与命名规范 | PDF | 23 |
| `WI-RD-058-004CMS_CAM原理图设计评审CheckListA1.jsonl` | CMS&CAM 原理图评审 CheckList | XLSX | 11 |
| `WI-RD-060_流媒体摄像头硬件设计规范A1.jsonl` | 流媒体摄像头硬件设计规范 | PDF | 12 |
| `WI-RD-070_车载产品电源设计规范_A0.jsonl` | 车载产品电源设计规范 | PDF | 25 |
| `WI-RD-071_元器件降额设计规范_A0.jsonl` | 元器件降额设计规范 (WI-RD-071) | PDF | 17 |


## 📄 templates/ — 报告模板

| 文件 | 说明 |
|:---|:---|
| `report-template.md` | 原理图评审报告标准模板（含「说明/分析理由/依据来源」三列） |
