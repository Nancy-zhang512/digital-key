---
name: gen-English-video
version: 1.0.0
description: "飞书文档转英文客户技术沟通视频。当用户需要下载飞书文档、翻译成英文技术沟通句子、按40句拆分txt，并生成字幕严格同步的 mp4 时使用。"
metadata:
  requires:
    bins: ["lark-cli", "python3", "ffmpeg", "ffprobe"]
---

# Feishu Doc -> English Tech Communication Video

> **前置条件：**
> 1. 先阅读 [`../lark-shared/SKILL.md`](../lark-shared/SKILL.md)
> 2. 再阅读 [`../lark-doc/SKILL.md`](../lark-doc/SKILL.md) 和 [`lark-doc-fetch.md`](../lark-doc/references/lark-doc-fetch.md)
> 3. 本流程默认使用在线神经语音：`edge-tts`。若本机未安装，先执行 `python3 -m pip install --user edge-tts`

## 依赖说明

### 必需命令

```text
lark-cli   用于下载飞书文档
python3    用于翻译整理、逐句 TTS、生成字幕
ffmpeg     用于读取音频时长、合并音频、渲染 mp4
ffprobe    用于精确读取 clip / m4a 的 duration
```

### Python 依赖

```bash
python3 -m pip install --user edge-tts
```

### 先检查本机依赖，再决定是否安装

执行前先检查：

```bash
command -v ffmpeg >/dev/null
command -v ffprobe >/dev/null
```

处理规则：

1. **如果本机已有 `ffmpeg` / `ffprobe`，直接调用现有命令，不要重复安装，也不要额外反复打印版本信息。**
2. **如果缺少 `ffmpeg`，先安装，再继续流程。** 在 macOS 上优先使用：

   ```bash
   brew install ffmpeg
   ```

3. 安装完成后，必须再次执行 `command -v ffmpeg` / `command -v ffprobe` 验证。
4. 若安装失败或验证仍失败，停止视频渲染流程，并明确告知用户当前环境缺少必要依赖。

## 快路径原则

Darwin 视角下，`lark-english-video` 变慢的主要来源不是“字幕规则更严格”，而是**重复依赖检查、逐句串行 TTS、以及失败后盲目重试**。默认应按以下快路径运行：

1. **文档只下载 1 次。** 如果源文档未变，不要重复 `docs +fetch`
2. **依赖只检查 1 次。** 当前进程已确认 `ffmpeg` / `ffprobe` 可用后，不要在每个分段前重复检查
3. **逐句 TTS 默认允许有限并发**（建议并发度 4-8），但最终字幕时间轴必须按原句顺序汇总
4. **duration 探测优先用 `ffprobe`，不要默认用 `ffmpeg -i`**，前者更快、更干净
5. **最终渲染默认只做 1 次**；只有出现明确失败时才进入重试分支，禁止无故重跑
6. **重试前先定位可恢复原因**；不要在输入、依赖和命令都没变化时盲目连续重试

### 渲染依赖注意事项

1. 推荐使用带 `libx264` 的 `ffmpeg`
2. 如使用 `ass` 滤镜烧录字幕，`ffmpeg` 需带 `libass`
3. 若环境里缺少 `ass` 滤镜，允许退回到 `drawtext` / 逐帧文字渲染方案，但**逐句同步逻辑不能变**
4. 默认字幕字体是 `Arial`；若当前系统没有 Arial，应选一个接近的无衬线字体并保持底部居中、白字深描边风格

## 适用场景

当用户要求你把一份飞书文档：

1. 下载到本地目录
2. 翻译并改写成适合客户技术沟通的英文句子
3. 按 **40 句一个 txt** 拆分
4. 生成英文技术沟通风格、字幕严格同步的 mp4
5. 且要求**字幕与语音严格同步**

时，使用本 Skill。

## 触发条件

当用户出现以下任一意图时，应主动使用本 Skill：

1. 提到“把飞书文档做成英文技术沟通视频 / mp4 / 带字幕视频”
2. 提到“要和现有样例视频风格一致”
3. 提到“字幕要和声音严格同步 / 不要靠估时”
4. 提到“按 40 句拆分 txt，再生成 mp4”
5. 已经给出飞书文档链接，且目标产物明确是**可独立播放的英文沟通视频**

典型关键词：

```text
飞书文档 / docx / wiki / markdown
英文技术沟通视频 / mp4 / 配音 / 字幕同步
40句一个 txt
现有样例视频风格一致
```

## 不适用场景

以下情况不应直接走本 Skill：

1. 只需要翻译文档，不需要视频产物
2. 只需要下载或编辑飞书文档内容，应优先走 `lark-doc`
3. 只需要把本地 HTML 或静态网页发布成链接，应走 `lark-apps`
4. 只需要生成普通演示文稿，应走 `lark-slides`
5. 用户没有要求英文客户技术沟通风格，而是需要其他风格配音或完全不同的视频模板

## 固定风格与参数

### 视频

```text
分辨率: 960x540
帧率: 5 fps
背景色: 0x1F2F46
视频编码: libx264
输出容器: mp4
```

### 音频

```text
TTS: 在线神经语音（edge-tts）
默认输出声线:
  - 美式男声: en-US-AndrewMultilingualNeural
  - 英式男声: en-GB-RyanNeural
参考语速: +10%
输出编码: AAC
采样率: 24000 Hz
声道: mono
码率: 67k
响度: loudnorm=I=-22.1:TP=-4.4:LRA=7
```

### 字幕

```text
格式: ASS
字体: Arial
字号: 24
颜色: 白色
描边/阴影: 深色描边 + 半透明阴影
对齐: 底部居中
MarginV: 250
最多显示: 3 行
换行策略: 先按 48 字符宽换行，超过 3 行时改按 56 字符宽再包
```

## 核心原则

### 1. 不要再用“按词数估算整段字幕时间”

这是最重要的规则。要保证字幕同步，**必须逐句合成语音，再用每一句的真实音频长度回写字幕时间轴**。

错误做法：

```text
整段文本一次性合成 -> 按词数/WPM 估算每句时长 -> 生成字幕
```

正确做法：

```text
逐句切分 -> 每句分别 TTS -> 用 ffmpeg 读取每句真实 duration -> 累加成时间轴 -> 生成 ASS
```

### 2. 语音和字幕必须一一对应

每一个句子必须对应一条 `Dialogue`，不能混句，也不要把一句拆成多条字幕，除非用户明确要求。

### 2a. 默认输出两套男声视频

除非用户明确要求只保留其中一种声线，否则默认同时生成：

1. **美式男声视频**（`en-US-AndrewMultilingualNeural`）
2. **英式男声视频**（`en-GB-RyanNeural`）

要求：

- 两个视频的**源内容相同**
- 两个视频的**字幕文本相同**
- 但两套声音的句长可能不同，因此**各自都要独立计算 duration 和字幕时间轴**
- **不要**把美式男声的时间轴直接复用到英式男声视频上

### 3. 如果用户要求“和现有参考视频声音一致”

优先规则：

1. **不要使用本机 `say` 声音**
2. 默认同时生成在线**美式男声**和**英式男声**两个版本
3. 如需匹配既有参考视频，先对候选在线男声做音色相似度对比，再选最接近的声音

本项目里默认参考方案：

```text
US voice = en-US-AndrewMultilingualNeural
UK voice = en-GB-RyanNeural
rate     = +10%
```

## 标准流程

### Step 1: 下载飞书文档

```bash
lark-cli docs +fetch --api-version v2 --doc "<doc_url>" --doc-format markdown
```

从返回 JSON 中取：

- `data.document.content`
- `data.document.document_id`
- `data.document.revision_id`

然后保存为本地 Markdown，例如：

```text
<target_dir>/source_zh.md
```

**速度优化规则**：

- 同一轮生成里，`source_zh.md` 一旦成功落盘，默认直接复用，不要再次下载同一文档
- 只有用户更换文档、文档 revision 明确变化、或首次下载失败时，才重新 `docs +fetch`

## 🔴 CHECKPOINT：文档下载完成后再继续

在进入翻译和切分前，必须先确认：

1. `docs +fetch` 已成功返回
2. `data.document.content` 非空
3. `source_zh.md` 已成功写入本地

若任一条件不成立：

- **不要继续执行翻译、切分、TTS 或渲染**
- 直接提示当前文档下载不完整或内容为空
- 结束本次视频生成流程

### Step 2: 翻译并改写成客户技术沟通英文句子

要求：

1. 不是逐字直译，而是改写成**自然、清晰、工程师对客户沟通**的英语句子
2. 尽量一句表达一个明确点
3. 优先使用：
   - Please confirm...
   - We would like to...
   - The customer expects...
   - We suggest...
   - Please provide...
4. 输出句子要适合朗读，不要太长

推荐输出：

```text
<target_dir>/source_en.md
```

### Step 3: 按 40 句切分 txt

命名规则：

```text
<prefix>_01.txt
<prefix>_02.txt
...
```

每个 txt 内建议保留编号：

```text
1. ...
2. ...
...
40. ...
```

## 逐句 TTS + 严格字幕同步方法

### Step 4: 清洗句子

读 txt 时去掉序号，只保留实际句子内容：

```python
line = re.sub(r'^\s*\d+\.\s*', '', line).strip()
```

### Step 5: 逐句在线合成

示例 Python：

```python
import asyncio, edge_tts

async def synth_sentence(text: str, out_path: str):
    communicate = edge_tts.Communicate(
        text,
        voice=VOICE,
        rate='+10%',
    )
    await communicate.save(out_path)
```

每一句输出一个 `mp3`，如：

```text
clips_01/01.mp3
clips_01/02.mp3
...
```

**速度优化规则**：

- 默认允许对不同句子做**有限并发 TTS**（建议并发度 4-8），不要强制全串行逐句等待
- 发生 429 / 限流 / 网络抖动时，再降为更低并发或串行
- 无论是否并发，最终 `durations` 与字幕 `Dialogue` 的顺序都必须与原句顺序一致
- **先完成一套英文句子的清洗与切分，再分别生成 US / UK 两套音频和视频**；不要重复翻译同一份文档

### Step 6: 读取每句真实时长

**优先使用 `ffprobe`** 读取每个 clip 的 duration（比 `ffmpeg -i` 更快）：

```bash
ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 clip.mp3
```

输出示例：

```text
3.42
```

### Step 7: 合并音频

用 concat 合并所有逐句音频：

```bash
ffmpeg -y -hide_banner \
  -f concat -safe 0 -i concat.txt \
  -c:a aac -ar 24000 -ac 1 -b:a 67k output.m4a
```

### Step 8: 用真实句长生成 ASS

关键逻辑：

1. 先累加逐句 duration
2. 再用最终音频容器实际总时长做一次比例修正

示例：

```python
actual_total = probe_duration(audio_m4a)
clip_total = sum(durations)
scale = actual_total / clip_total if clip_total > 0 else 1.0

t = 0.0
for sentence, dur in zip(sentences, durations):
    seg = dur * scale
    start = t
    end = t + seg
    # 写入 ASS Dialogue
    t = end
```

这一步是**本 Skill 最关键的同步方法**。

## ASS 模板

```ini
[Script Info]
ScriptType: v4.00+
PlayResX: 960
PlayResY: 540
ScaledBorderAndShadow: yes
WrapStyle: 2
YCbCr Matrix: TV.601

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,24,&H00FFFFFF,&H00FFFFFF,&H00202020,&H64000000,0,0,0,0,100,100,0,0,1,2,1,2,80,80,250,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
```

## 🔴 CHECKPOINT：开始批量渲染前确认

在执行任意一段 mp4 渲染前，必须先确认以下条件全部成立：

1. `edge-tts` 可用，且逐句音频已生成
2. `ffmpeg` / `ffprobe` 已检查通过
3. `output.m4a` 与 `output.ass` 都存在且非空
4. 输出目录存在且可写
5. 本轮仍沿用逐句同步方案，而不是词数估时方案

若任一条件不成立：

- **不要进入批量渲染**
- 先修复依赖、输入文件或路径问题
- 修复失败则停止本轮视频生成

## 最终渲染命令

```bash
ffmpeg -y -hide_banner \
  -f lavfi -i "color=c=0x1F2F46:s=960x540:r=5:d=${DURATION}" \
  -i output.m4a \
  -vf "ass=output.ass" \
  -af "loudnorm=I=-22.1:TP=-4.4:LRA=7" \
  -map 0:v -map 1:a \
  -c:v libx264 -preset medium -crf 23 \
  -c:a aac -ar 24000 -ac 1 -b:a 67k \
  -shortest output.mp4
```

## 双声线输出规则

同一份 `source_en.md` / `prefix_*.txt` 默认生成两套最终产物：

1. **US 版**
   - voice: `en-US-AndrewMultilingualNeural`
   - 建议文件名：`<prefix>_us.mp4`
2. **UK 版**
   - voice: `en-GB-RyanNeural`
   - 建议文件名：`<prefix>_uk.mp4`

执行顺序：

1. 中文原文只下载 1 次
2. 英文改写只生成 1 份
3. 每个 `txt` 只切分 1 次
4. 然后分别对 **US / UK**：
   - 逐句 TTS
   - 读取真实 duration
   - 生成对应的 `output.ass`
   - 渲染对应的 `output.mp4`

注意：

- 两个版本的**字幕文本内容必须一致**
- 两个版本的**字幕时间轴允许不同**，并且通常会不同
- 不要因为已经生成了 US 版，就跳过 UK 版的 duration / ASS 计算

## 渲染失败重试规则

## 🛑 STOP：渲染超时

如果视频渲染 **10 分钟** 仍未生成完成：

1. 视为**渲染超时**
2. 立即提示用户当前任务已超时
3. **直接退出渲染流程**
4. 保留当前中间产物，方便后续排查

如果最终渲染失败：

1. 先检查错误日志，优先确认：
   - `ffmpeg` 是否可执行
   - `ass` 滤镜是否可用
   - 输入音频 / ASS 文件是否存在且非空
   - 输出路径是否可写
2. 修正可恢复问题后，**重新渲染最多 2 次**
3. 若第 2 次重试后仍失败，**放弃渲染**，不要无限重试

约束：

- **总尝试次数最多 3 次**：首次渲染 + 2 次重试
- **10 分钟超时后不能静默继续等待**，必须明确提示用户超时并退出
- 重试时必须沿用同一套逐句同步逻辑，不要退化为按词数估时
- 若确认是 `ass` 滤镜问题，可改用 `drawtext` / 逐帧文字渲染后再重试
- 2 次重试仍失败时，保留中间产物用于排查，并向用户明确说明已放弃渲染
- **不要在原因未变化时盲目连试 3 次**；每次重试前必须先判断本轮是否真的做了可恢复修正

## 推荐产物结构

```text
target_dir/
  source_zh.md
  source_en.md
  prefix_01.txt
  prefix_02.txt
  prefix_01_us.mp4
  prefix_01_uk.mp4
  prefix_02_us.mp4
  prefix_02_uk.mp4
```

中间文件（**视频生成完成后必须删除**）：

```text
clips_01/
clips_02/
*.ass
*.m4a
*.mp3
concat.txt
```

> ⚠️ **强制清理**：每个 mp4 验证可正常播放后，立即执行以下命令删除所有中间临时文件：
>
> ```bash
> rm -rf clips_*/
> rm -f *.ass *.m4a *.mp3 concat.txt
> ```
>
> 清理后仅保留最终产物：`source_zh.md`、`source_en.md`、`prefix_*.txt`、`prefix_*.mp4`。

## 失败回退策略

### 1. 声音不对

如果用户说声音不像：

1. 不要退回本机 `say`
2. 先判断用户反馈针对的是 **US 版** 还是 **UK 版**
3. 在对应口音的在线男声候选里继续调整
4. 保持逐句同步流程不变

### 2. 字幕不同步

优先检查：

1. 是否误用了“整段一次性 TTS + 词数估时”
2. 是否逐句生成了音频
3. 是否按 `actual_total / clip_total` 做了时间缩放修正

### 3. 字幕位置不对

统一改 `MarginV`：

```text
170 -> 较低
250 -> 当前项目标准
```

### 4. 渲染失败

按以下顺序处理：

1. 检查本机是否已有 `ffmpeg` / `ffprobe`；没有则先安装
2. 若是 `ass` 滤镜不可用，切到 `drawtext` / 逐帧渲染方案
3. 重新渲染，最多再试 2 次
4. 若仍失败，则放弃渲染，并把失败原因和已保留的中间文件告知用户

### 执行速度优化

- **不要重复下载同一份文档**
- **不要在每段渲染前重复检查 `ffmpeg` / `ffprobe`**
- 优先使用 `ffprobe` 探测时长，而不是 `ffmpeg -i`
- 逐句 TTS 默认使用**有限并发**
- 渲染失败时先定位原因，再决定是否值得重试

## 交付规则

完成后应明确告诉用户：

1. 生成了哪些 txt / mp4
2. US / UK 两个版本分别使用的在线声音是什么
3. 是否采用了逐句同步方案
4. 中间临时文件已**强制删除**（clips_*/ *.ass *.m4a *.mp3 concat.txt）
5. 本次使用的关键依赖或降级方案（例如：`ass` 烧录还是 `drawtext` / 逐帧渲染）

## 交付前检查

交付前至少确认：

1. 每个 mp4 都能正常播放，且包含视频流和音频流
2. 最终时长与合成音频一致，没有明显提前结束或尾部黑屏过长
3. 字幕是逐句对应，不存在两句合并或一句拆成多段的意外情况
4. 输出目录和文件命名符合 `<prefix>_01.txt`、`<prefix>_01.mp4` 这类规则
5. 所有中间临时文件（`clips_*/`、`*.ass`、`*.m4a`、`*.mp3`、`concat.txt`）已清理，目录下仅剩最终产物

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
