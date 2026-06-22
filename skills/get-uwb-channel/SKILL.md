---
name: get-uwb-channel
version: 1.0.0
description: "UWB channel 合规查询与飞书文档更新。当用户需要查询某个国家/地区的 UWB channel（CH5/CH6/CH8/CH9/CH10/CH12/CH13/CH14）要求、给出监管依据、并把结果更新到当前固定飞书文档时使用。"
metadata:
  requires:
    bins: ["lark-cli"]
---

# UWB Channel Query + Fixed Feishu Doc Update

> **前置条件：**
> 1. 先阅读 `lark-shared`：`lark-cli skills read lark-shared`
> 2. 再阅读 `lark-doc`：`lark-cli skills read lark-doc`
> 3. 所有文档读写默认使用 `--as user`

## 固定目标文档

- **Doc URL**: `https://yftech2012.feishu.cn/docx/AAu6dS6QwojKTxx3eoWckoMsnNf`
- **Doc Token**: `AAu6dS6QwojKTxx3eoWckoMsnNf`
- **更新原则**:
  1. 用户只查单个或少量国家时，优先更新首页主对比表格对应行
  2. 用户查一组国家或全量国家时，更新/重写文档中的“全球出口市场 UWB 频道合规汇总”章节
  3. 不要新建其他文档；结果统一写回这份文档

## 适用范围

适用于以下任务：

1. 查询某个国家/地区是否支持 UWB `CH5 / CH6 / CH8 / CH9 / CH10 / CH12 / CH13 / CH14`
2. 查询该国 60GHz 雷达是否允许使用
3. 给出监管依据（法规、监管机构、官方标准）
4. 将结果同步到固定飞书文档

不适用于：

1. 只做 UWB 芯片能力对比、不关心国家法规
2. 只编辑文档样式、不涉及 UWB 合规判断
3. 只做 60GHz 频段研究、不涉及 UWB channel

## 固定查询字段

### UWB channel 列

```text
CH5  = 6489.6 MHz
CH6  = 6988.8 MHz
CH8  = 7488.0 MHz
CH9  = 7987.2 MHz
CH10 = 8486.4 MHz
CH12 = 8985.6 MHz
CH13 = 9484.8 MHz
CH14 = 9984.0 MHz
```

### 状态枚举

| 状态 | 含义 | 表格颜色 |
|---|---|---|
| `authorized` | 已授权/可商用 | 蓝 |
| `restricted` | 受限/需附加条件 | 黄 |
| `forbidden` | 禁止/不可商用 | 红 |
| `unclear` | 公开资料不充分/需逐案申请 | 灰 |

### 输出列

每次查询至少输出：

| 列 | 说明 |
|---|---|
| 国家/地区 | 用户请求对象 |
| CH5 / CH6 / CH8 / CH9 / CH10 / CH12 / CH13 / CH14 | 各频道状态 |
| 60GHz | 57~66GHz / 57~71GHz / unclear |
| 监管依据 | 法规或监管机构 |
| 备注 | 例如“仅室内”“需 DAA”“需型号核准” |

## 监管判断优先级

查询时按以下优先级收集证据，**优先官方，后行业**：

1. **官方监管机构 / 官方法规**
   - 欧盟：Commission Implementing Decision、ETSI、ECC
   - 英国：Ofcom
   - 香港：OFCA / HKCA
   - 韩国：MSIT / RRA / KCC
   - 阿联酋：TDRA
   - 新加坡：IMDA
   - 澳大利亚：ACMA
   - 各国主管机构的频谱或 SRD/UWB 规范
2. **官方引用的标准体系**
   - ETSI EN 302 065
   - ECC/DEC(06)04
   - FCC Part 15 Subpart F
3. **行业合规资料（仅作补充，不作唯一依据）**
   - Qorvo APR001
   - FiRa FAQ
   - 合规实验室/认证机构解读

**禁止**仅凭芯片支持矩阵就认定某国已授权。

## 默认判断模板

当国家缺少直接官方逐频道表时，可先按监管框架归类，再补充国家级证据。

### 1. EU / ETSI 框架

适用：大多数欧盟/EEA/欧洲 ETSI 对齐国家，以及部分中东/北非国家。

```text
CH5  ✅
CH6  ✅
CH8  ✅
CH9  ✅
CH10 ⚠️ restricted
CH12 ❌
CH13 ❌
CH14 ❌
60GHz = 57~66GHz
```

默认依据：

- `Commission Implementing Decision (EU) 2024/1467`
- `ETSI EN 302 065`
- `ECC/DEC(06)04`

### 2. FCC 框架

适用：美国、部分 APAC、部分 LATAM，以及显式采用 FCC/3.1~10.6GHz 低功率框架的市场。

```text
CH5  ✅
CH6  ✅
CH8  ✅
CH9  ✅
CH10 ✅
CH12 ✅
CH13 ✅
CH14 ✅
60GHz = 57~71GHz 或当地已开放范围
```

默认依据：

- `FCC Part 15 Subpart F`
- 当地 SRD/UWB 免许可规范

### 3. 韩国特殊规则

```text
CH5  ✅
CH6  ❌
CH8  ❌
CH9  ✅
CH10 ✅
CH12 ✅
CH13 ✅
CH14 ❌
60GHz = 57~66GHz
```

默认依据：

- `MSIT / RRA / KCC`

### 4. 监管不明确 / 逐案审批

若公开资料不足，或仅能确认“需型号核准/特别申请”，则统一先标记：

```text
CH5~CH14 = ❓ unclear
60GHz    = ❓ unclear
```

备注中必须写明：

- 需要本地监管机构确认
- 需要型号核准 / case-by-case approval
- 不可直接沿用 CE/FCC 结论

## 标准工作流

### Step 1: 明确查询范围

识别用户属于哪一类请求：

1. **单国查询**：如“德国的 UWB channel 要求”
2. **少量国家对比**：如“德国/法国/英国”
3. **一组国家批量查询**：如“图里这些国家都查一遍”
4. **已有文档更新**：如“把结果更新到当前飞书文档”

### Step 2: 收集法规依据

先查国家监管框架，再查该国官方或准官方依据。

建议查询思路：

```text
<country> UWB regulation channel 5 6 8 9 10 12 13 14
<country> regulator UWB 6-8.5 GHz / 3.1-10.6 GHz
<country> SRD UWB official frequency allocation
```

先判定它更接近：

1. EU / ETSI
2. FCC
3. Korea-like special
4. unclear / approval required

### Step 3: 形成结构化结果

对每个国家生成结构化记录：

```json
{
  "country": "Germany",
  "framework": "EU/ETSI",
  "ch5": "authorized",
  "ch6": "authorized",
  "ch8": "authorized",
  "ch9": "authorized",
  "ch10": "restricted",
  "ch12": "forbidden",
  "ch13": "forbidden",
  "ch14": "forbidden",
  "radar60": "57~66GHz",
  "basis": [
    "EU 2024/1467",
    "ETSI EN 302 065",
    "BNetzA"
  ],
  "notes": "CH10 only under additional conditions"
}
```

### Step 4: 先读文档，再决定写法

```bash
lark-cli docs +fetch --api-version v2 --doc "AAu6dS6QwojKTxx3eoWckoMsnNf" --detail with-ids --as user
```

根据用户意图选择更新方式：

#### A. 更新首页主对比表格

适用：单个国家或少量国家。

做法：

1. 取到主表格 block id
2. 用 `block_replace` 重写整个表格
3. 保持已有国家行不变，只更新目标国家行

示例：

```bash
lark-cli docs +update --api-version v2 \
  --doc "AAu6dS6QwojKTxx3eoWckoMsnNf" \
  --command block_replace \
  --block-id "<main_table_block_id>" \
  --content '<table>...</table>' \
  --as user
```

#### B. 更新“全球出口市场 UWB 频道合规汇总”章节

适用：批量国家、整组国家、重新梳理全球矩阵。

做法：

1. 先定位该标题 block
2. 若章节已存在，优先整体 `block_replace` 或删除旧章节后重插
3. 若不存在，则用 `append` 追加

示例：

```bash
lark-cli docs +update --api-version v2 \
  --doc "AAu6dS6QwojKTxx3eoWckoMsnNf" \
  --command append \
  --content '<h1>全球出口市场 UWB 频道合规汇总</h1><table>...</table>' \
  --as user
```

## 文档排版规则

### 1. 主展示形态

优先使用 `<table>`，列固定为：

```text
国家/地区 | CH5 | CH6 | CH8 | CH9 | CH10 | CH12 | CH13 | CH14 | 60GHz | 监管依据 | 备注
```

### 2. 颜色规则

```text
authorized -> light-blue
restricted -> light-yellow
forbidden  -> red
unclear    -> medium-gray
```

### 3. 说明区块

大批量更新后，至少增加一个 callout 说明：

1. 本次覆盖的国家范围
2. 数据依据优先级
3. “芯片支持 != 国家许可”

示例：

```xml
<callout emoji="❗" background-color="light-red" border-color="red">
  <p><b>注意</b>：芯片支持矩阵不等于国家监管许可。若国家未发布明确 UWB 频谱规则，则需按型号核准或特别申请处理。</p>
</callout>
```

## 结果输出要求

对用户回复时，至少包含：

1. **结论**：哪些频道支持 / 受限 / 禁止
2. **依据**：至少 1 条官方或准官方依据
3. **更新动作**：是否已写回固定飞书文档
4. **不确定性**：如果资料不足，要明确说“不明确/需申请”，不要伪造确定性

## 高风险和边界情况

### 1. 找不到国家直接规定

允许按监管框架给出“高置信默认结论”，但必须显式说明：

```text
该国未找到逐频道官方公开表，以下结论基于其采用的 EU/ETSI（或 FCC）框架推导，并以当地主管机构最终批复为准。
```

### 2. 同一国家不同应用场景规则不同

若发现：

1. 车载 UWB 与消费电子不同
2. 室内与室外不同
3. 定位与通信不同

则在备注中写清场景，不能混写成一个无条件结论。

### 3. 文档已有历史结论冲突

处理顺序：

1. 先 fetch 当前内容
2. 保留表格结构
3. 以新证据覆盖旧状态
4. 在备注或说明区标注“本次按最新监管依据修订”

## 最小可复用模板

### 单国结论模板

```text
<国家> UWB channel 结论：
- 支持：CH...
- 受限：CH...
- 不支持：CH...
- 60GHz：...
- 依据：...
```

### 表格行模板

```xml
<tr>
  <td>国家</td>
  <td background-color="light-blue">CH5</td>
  <td background-color="light-blue">CH6</td>
  <td background-color="red">CH8</td>
  <td background-color="light-blue">CH9</td>
  <td background-color="light-yellow">CH10</td>
  <td background-color="red">CH12</td>
  <td background-color="red">CH13</td>
  <td background-color="red">CH14</td>
  <td background-color="light-blue">57~66GHz</td>
  <td>ETSI / regulator</td>
  <td>备注</td>
</tr>
```

## 当前已验证的高置信规则

1. **德国 / 法国**：EU/ETSI 规则
2. **英国**：Ofcom 基本沿用 ETSI 逻辑
3. **香港**：OFCA 对 6~8.5GHz 许可，CH12~CH14 不建议商用
4. **韩国**：特殊频道组合，不可按 EU/FCC 直接套用
5. **阿联酋**：TDRA 对齐国际框架，可按高频 UWB 许可处理
6. **俄罗斯 / 独联体部分国家**：默认走 `unclear / approval required`

## 执行时的默认策略

如果用户没有额外说明：

1. 优先查官方/监管依据
2. 再按监管框架映射到频道状态
3. 回答用户
4. 同步更新固定飞书文档

这四步缺一不可。
