---
name: lark-english-video
version: 1.0.0
description: "飞书文档转英文客户技术沟通视频。当用户需要下载飞书文档、翻译成英文技术沟通句子、按40句拆分txt，并生成字幕严格同步的 mp4 时使用。"
metadata:
  requires:
    bins: ["lark-cli", "python3", "ffmpeg", "ffprobe"]
---

# Feishu Doc -> English Tech Communication Video

> **前置条件：**
> 1. 先阅读 [`../lark-shared/SKILL.md`](../../../../../../.agents/skills/lark-shared/SKILL.md)
> 2. 再阅读 [`../lark-doc/SKILL.md`](../../../../../../.agents/skills/lark-doc/SKILL.md) 和 [`lark-doc-fetch.md`](../../../../../../.agents/skills/lark-doc/references/lark-doc-fetch.md)
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
默认参考男声: en-US-AndrewMultilingualNeural
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

### 3. 如果用户要求“和现有参考视频声音一致”

优先规则：

1. **不要使用本机 `say` 声音**
2. 使用在线美式男声
3. 如需匹配既有参考视频，先对候选在线男声做音色相似度对比，再选最接近的声音

本项目里已经验证过的默认参考方案：

```text
voice = en-US-AndrewMultilingualNeural
rate  = +10%
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
        voice='en-US-AndrewMultilingualNeural',
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

### Step 6: 读取每句真实时长

用 ffmpeg/ffprobe 读取每个 clip 的 duration：

```bash
ffmpeg -hide_banner -i clip.mp3
```

从 stderr 提取：

```text
Duration: 00:00:03.42
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

## 推荐产物结构

```text
target_dir/
  source_zh.md
  source_en.md
  prefix_01.txt
  prefix_02.txt
  prefix_01.mp4
  prefix_02.mp4
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
2. 继续在在线美式男声里换候选
3. 保持逐句同步流程不变

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

## 交付规则

完成后应明确告诉用户：

1. 生成了哪些 txt / mp4
2. 使用的在线声音是什么
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
