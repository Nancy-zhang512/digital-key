<title>解析Euro NCAP  Driver Monitoring Framwork for 2029</title>

**从ODMS方案视角解析Euro NCAP  Driver Monitoring Framwork for 2029**

# Euro NCAP  Driver Monitoring Framwork for 2029

<cite doc-id="Pzgzb1nAYoP43yxxPUMcGthjnWc" file-type="file" title="Euro NCAP Driver Monitoring Framework for 2029.pdf" type="doc"></cite>

# 逐页解读

## 页2　2029 路线图总览

**原文关键词：** Function Robustness（Simulation, test under noise；Realistic & representative methods；Naturalistic test execution）；Performance Balance；Context；Driver State Link, Infrastructure；On-road evaluation。

![](https://feishu.cn/file/S2GybiviToykKZxzhavc9gYrnfQ)

**ODMS 关注点**

| 编号 | 原文要求 | ODMS 解读 / 需要的能力 | 详细说明 |
|-|-|-|-|
| R1 | Function Robustness：Simulation, test under noise；Naturalistic test execution | 按实路、噪声工况设计测试，而不只是赛道/实验室通过 | 测试计划要同时覆盖：①受控条件下的功能测试；②加噪声的仿真/台架（夜间、强光、遮挡、不同人群）；③自然驾驶数据回放。每类测试要有明确的通过判据和数据留存，避免出现“实验室通过、实路误报高”的落差。 |
| R1 | Driver State Link, Infrastructure | 驾驶员状态要能链接到 ADAS，ODMS 需要对外输出驾驶员状态接口 | 需要定义对外信号：状态类型（注意/分心/疲劳）、置信度、时间戳、更新频率、有效/无效标志。接口要预留与整车总线（CAN/以太网等）的映射，并与 OEM 的 ADAS 团队对齐延迟要求。 |

## 页6\~7　性能平衡与上下文

**原文：** Enabling Balanced Performance by facilitating context: a) Infrastructure (traffic rules) b) Driver awareness (attentive/distracted).

**原文示例：** “McDonald’s turn”: a simple situation, hard to predict without knowledge about driver awareness.

![这是Euro NCAP 2025年发布的第7页主题为“Performance Balance”的示意图，核心展示通过支撑两类上下文实现性能平衡的内容。图中分为左右两个区块：左侧区块对应a)基础设施（交通规则），以路口示意图说明橙色车辆按规则必须左转，可判定其不会直行，标注有“Not a Turn Across Path”；右侧区块对应b)驾驶员意识（专注/分心），以路网、车辆和麦当劳门店的示意图举例“麦当劳转弯”场景，说明这类简单场景若没有驾驶员的注意状态相关信息，系统很难做出准确预判，直观呼应了文档中ODMS需为ADAS提供驾驶员注意状态输入的相关要求。](https://feishu.cn/file/P5SobfQogohPdZxomSncM6rlnXc)

**ODMS 关注点**

| 编号 | 原文要求 | ODMS 解读 / 需要的能力 | 详细说明 |
|-|-|-|-|
| R2 | Driver awareness (attentive/distracted) 作为 ADAS 平衡性能的上下文 | ODMS 的价值从报警扩展为给 ADAS 提供驾驶员注意状态 | 产品定位上，ODMS 不仅是“报警器”，还是 ADAS 的输入源， 需要给ADAS输入更多的信息，如视线/等 |
| R2 | McDonald’s turn：没有驾驶员注意信息难以预测 | 注意状态需要稳定、低延迟，否则影响 ADAS 判断（页6 为 OEM 的 Trigger happiness 示意图，无展开文字） | ADAS 会依赖注意状态做决策，状态抖动会放大误触发。建议对状态做滞回/平滑，并在方案里给出端到端延迟预算（相机曝光→算法→信号输出）。具体延迟指标需与 OEM 协商，原文未给出数值。 |

## 页8　Driver Engagement 2029 路线图任务表

**原文关键描述（节选）：**

- 1b Synthetic data：assessment process including performance predictions in ranges …
- 1c Impairment verification：objective verification for sleep onset (replace subjective KSS-only assessment); include fatigue ramp-up and micro-sleep detection windows.
- 1d Sensing quality：Sudden sickness (e.g., loss of consciousness) detection.
- 2a False Positive validation on-road：flag driver acceptance issues (e.g., nuisance alerts).
- 2b Warnings & interventions：positive alternatives to encourage engagement instead of penalising disengagement (attention management).
- 2c Redefine attentiveness beyond gaze metrics：object monitoring (driver must be aware of path objects instead of just eyes on-road) tied to ADAS interventions / warnings.
- 3a\~3d：voice and multimodal controls；GVC & DM coupling；on-road time-critical tasks；personalisation。

![这张图是Euro NCAP发布的2029年驾驶员参与度路线图任务表，核心内容以表格形式呈现，包含任务组/模块、任务编号、任务名称与描述，还标注了对应责任方、任务开始与结束年份。表中突出的任务项包含1a的标准DSM驱动程序、1b的合成数据评估流程、1c的损伤验证方法、1d的感知质量检测，以及2a至2c、3a至3d等相关任务，明确了各任务的实施方向与时间安排，用于呈现2029年驾驶员监控框架相关的具体任务规划。](https://feishu.cn/file/MG0fb6BvUoiGw1xvH9sccFqgn6g)

**ODMS 关注点**

| 编号 | 原文要求 | ODMS 解读 / 需要的能力 | 详细说明 |
|-|-|-|-|
| R3 | 1b/1c：客观入睡验证，含 fatigue ramp-up 和 micro-sleep detection windows；performance predictions in ranges | 可客观验证的入睡检测，覆盖疲劳加重过程和微睡眠窗口；支持按范围预测性能 | 疲劳检测要输出分级（如逐步加重）和微睡眠事件，而不是单一阈值报警。需要建立“范围参数”（光照、头姿、遮挡、人群特征等）与检测性能的对应关系，便于做性能预测。验证数据要有客观标签（如 PVT/生理指标），不能只靠主观评分。 |
| R4 | 1d：Sudden sickness (e.g., loss of consciousness) detection | 新增突发疾病、意识丧失检测方向，当前 ODMS 视觉方案是否覆盖需评估 | 先评估纯视觉能做什么：长时间闭眼、头部无力下垂、无响应等可观测特征；原文提到的 DADSS 式触摸/呼气传感属于其他传感器，ODMS 是否纳入需产品决策。建议先做可行性评估 |
| R5 | 2a/2b：实路 nuisance alerts 被标注；鼓励参与而非惩罚（attention management） | 设定误报率目标；告警策略从惩罚走神转向分级、正向 | 告警要分级（提示→警告→干预），并支持延迟/抑制策略。需要内部误报指标：实路每百公里误报次数、用户可感知的骚扰告警占比；具体目标值需结合 OEM 要求，原文未给数值。HMI 形式（声音/视觉/触觉）由 OEM 决定，ODMS 提供可配置的触发条件。 |
| R6 | 2c：driver must be aware of path objects instead of just eyes on-road，与 ADAS 干预/告警挂钩 | 最关键：视线与前向感知目标关联 | 需要把视线方向换算到车辆坐标系，并与前向感知给出的目标方位对比，判断驾驶员是否看向了威胁。依赖：相机与车辆坐标系的标定、视线估计精度（尤其大角度）、前向感知的目标方位与时延。这条是后续 FTL/LFTS 的基础，也是接口设计的重点。 |
| R7 | 3a\~3d：语音与多模态控制；GVC & DM coupling；on-road time-critical tasks；personalisation | 接收车辆控制操作状态；考虑驾驶员个人配置 | 需要整车提供“当前是否在操作车辆控制”的信号，ODMS 据此抑制/延迟告警（见页16\~17）。个性化方面，可预留驾驶员 ID 对应的参数配置（如灵敏度），但是否做、做到什么程度由 OEM 决定；涉及个人数据时要考虑隐私合规。 |
| — | 表中 Start/End（如 1c：2025 H2\~2026 H2；2c：2026 H1\~2026 H2） | 是 Euro NCAP 各任务的研究/制定周期，不是量产要求时间，生效以后续正式协议为准 | 跟踪 Euro NCAP 后续正式协议文件 |

## 页9　2029 框架：目标与信息链路

**原文：** Move from generic distraction warnings to risk-based support: Functional adaptations: Maximizing ADAS effectiveness while keeping low FP/nuisance；Attention management: Ensuring that DMS supports and does not annoy。

**原文链路：** Driver State + External events → DMS → ADAS。

![](https://feishu.cn/file/EID1biweaoNqrixizLbcjo8RnQg)

**ODMS 关注点**

| 编号 | 原文要求 | ODMS 解读 / 需要的能力 | 详细说明 |
|-|-|-|-|
| R8 | Driver State + External events → DMS → ADAS；Functional adaptations + Attention management | 明确 DMS 输入/输出边界：输出给 ADAS 做功能适配，给驾驶员做注意力管理 | 系统架构图里要画清两条输出：①给 ADAS 的状态/事件（功能适配）；②给驾驶员的告警（注意力管理）。输入侧要列出所有外部事件及其来源，并标明这些输入是进入 DMS 判定，还是只在策略层使用，这个区分与专利规避有关。 |
| R8 | External events 进入 DMS 链路 | 与 Magna 55/56（阈值随运行状态变化；车速+前方交通）主题接近；美国版建议把外部风险引入点放在 ADAS/OEM 侧 | 原文链路里外部事件会影响 DMS 输出，这与 Magna 55/56 的主题接近。是否构成侵权要逐个权利要求要素比对，本文不下结论。设计上建议：DMS 层只输出驾驶员状态，外部风险的引入放在策略层，并保留设计证据，由美国律师评估。 |

## 页10　注意力告警时序（最关键）

**原文表（节选）：**

- Short glance off road (≤1 s)：2023 Higher FCW & LDW sensitivity；2026 ≥200 ms difference in FCW for longitudinal conflicts, LSS adaptations；2029\~2032 Last point to brake or last point to steer + (distracted) driver’s reaction time for all scenarios, LSS adaptations
- Long Glance Away (LGA)：3 s → 3–4 s → External Risk-based
- VATS：All tasks → Non-driving related tasks, Phone Use → Phone Use（注：e.g., 10 s accumulated within 30 s window）
- Fail to Look (FTL)：2029 Threat in collision path and with high angle relative to driver’s gaze
- Looked but Failed to See (LFTS)：2032 Threat in collision path and within driver’s gaze

![](https://feishu.cn/file/AiTkbK2IRoAUrgxJdG7cgzuOn8d)

**ODMS 关注点**

| 编号 | 原文要求 | ODMS 解读 / 需要的能力 | 详细说明 |
|-|-|-|-|
| R9 | Short glance ≤1 s：FCW/LDW 灵敏度适配 | 低时延、高时间分辨率的视线/头姿输出 | 需要明确帧率、算法延迟和输出频率，使 ≤1s 的短暂扫视能被可靠检测。要验证快速扫视时的视线估计稳定性（眨眼、头动、遮挡下的表现）。 |
| R9 | LGA：3 s → 3–4 s → External Risk-based | 阈值可配置，并可被外部风险动态调整 | 把 LGA 时间阈值做成可配置参数，并预留由策略层下发的接口。“外部风险驱动”由谁计算、谁下发要在接口文档里写清；美国版配置要与专利风险评估联动。 |
| R9 | VATS：e.g., 10 s accumulated within 30 s window；2029 收窄到 Phone Use | 滑动窗口累计；稳定的手机使用检测 | 实现 30s 滑动窗口内的累计离路时长，并输出累计值。手机使用检测要区分拿手机、看手机、通话等行为，验证不同手持姿态和遮挡情况。窗口和阈值要可配置，原文用的是示例值（e.g.）。 |
| R10 | FTL（2029）：threat in collision path and with high angle relative to driver’s gaze；LFTS（2032）：threat within driver’s gaze | 视线方向与碰撞路径威胁方位关联；判断没看见与看了但没看见，是与前向感知融合的核心接口。 | FTL：威胁在碰撞路径上，且与视线夹角大 → 判断为没看。LFTS：威胁在视线内但未反应 → 看了但没看见。需要：视线方向与威胁方位的时间同步、坐标统一、夹角阈值、视线有效性判断。LFTS 到 2032 才出现，可分阶段实现。页11 的 FTL 细节在另一场演讲，需补充获取。 |

## 页11\~12 合成数据验证

**原文（页12）：** Spot Checks (\~20 cases)；Validation dataset (\~1000 cases)；Benchmark dataset (\~20 cases)；Ground Truth：Head pose (X/Y, Yaw, Pitch, Roll)、Eye gaze vector、Eyelid aperture、Driver characteristics、Occlusion(s) presence、Illumination；Injection → DMS ECU → Output (TP, FP)；Domain gap metrics (at model level)；Calibration；TPR/FPR across ranges。

（页11 的 Fail To Look 细节在另一场演讲中，本文档没有展开。）

![](https://feishu.cn/file/By7HbfdKFogJedxSriMc639XnZg)

**ODMS 关注点**

| 编号 | 原文要求 | ODMS 解读 / 需要的能力 | 详细说明 |
|-|-|-|-|
| R11 | Injection → DMS ECU → Output (TP, FP)；TPR/FPR across ranges | DMS ECU 需有注入合成数据的测试入口，并输出可统计 TP/FP 的结果 | 需要一个能把合成图像/特征注入 ECU 的测试模式（如视频输入或测试接口），并保证输出的状态结果带时间戳，便于与真值对比，统计各范围下的 TPR/FPR。该入口要与量产软件隔离或受控，避免安全风险。 |
| R11 | Sensor specs；Ground Truth：Head pose, Eye gaze vector, Eyelid aperture, Occlusion, Illumination | 准备传感器规格；输出量与真值一一对应 | 向合成数据提供方交付传感器规格（分辨率、视场、波段、曝光等）。算法侧要能输出与真值对应的量：头姿（X/Y、yaw/pitch/roll）、视线向量、眼睑开度、遮挡与光照条件给到ADAS系统来决策。这些输出量也可用于内部调试。 |
| R11 | Domain gap metrics (at model level)；Calibration | 合成数据与真实物理测试的差距要可度量、可校准 | 需要做同一场景下的合成结果与物理测试结果对比，度量差距并校准，才能证明合成数据可用于性能预测。要预先设计一组物理测试（基准集）与合成数据对应。原文的数据集规模（约 20/1000/20 例）以官方后续规定为准。 |

## 页13　实路评估

**原文：** >2000 km naturalistic driving on public roads；Driver acceptance issues (FP)；Perception and actuation performance (TP, FN)；Event annotation possible under noise factors — Driver Monitoring: nighttime, direct sun glare。

![](https://feishu.cn/file/KE9IbT0yToioaExAx1gcYA6Gnb0)

**ODMS 关注点**

| 编号 | 原文要求 | ODMS 解读 / 需要的能力 | 详细说明 |
|-|-|-|-|
| R12 | Driver Monitoring noise factors: nighttime, direct sun glare | 重点优化 NIR 照明、曝光控制、抗太阳光干扰的图像效果，并在这两类场景留存实路数据 | 夜间：NIR 照明强度、均匀性、曝光控制。强光直射：滤光、HDR/曝光策略、对太阳光干扰的抗性。需要为这两类场景建立专项测试集和内部指标，并持续收集实路数据。 |
| R12 | Driver acceptance issues (FP)；Perception and actuation performance (TP, FN) | 需具备事件记录能力（时间戳、状态输出、图像或特征），用于事后分析 | 需要实路采集系统：记录状态输出、时间戳、关键中间量，必要时记录图像或特征。图像记录涉及隐私与合规，要与 OEM 确认可记录范围。记录要能与人工标注（FP/FN）对齐，便于复盘。 |

## 页14\~15　疲劳验证（PVT）

**原文（页14）：** Scenario-based, naturalistic assessment of drowsiness detection robustness. Objective reference: Psychomotor Vigilance Task (PVT) … Assessment: Annotating FN and FP during on-road evaluation, with 10-min PVT as a reference.

**原文（页15）：** T0 pre-departure baseline PVT；Mid-route PVT + KSS；End-of-route PVT + KSS；Event-contingent tests：Vehicle drowsiness alert or Driver feels extremely drowsy → Safe stop → 10-min PVT + KSS。

![](https://feishu.cn/file/EdAXbPI2AorFp4xGu14czzzxnJd)

![](https://feishu.cn/file/IJvhbd83roHc8nxIQQrclVk4nyc)

**ODMS 关注点**

| 编号 | 原文要求 | ODMS 解读 / 需要的能力 | 详细说明 |
|-|-|-|-|
| R3 | 10-min PVT 作为 objective reference；Annotating FN and FP | PVT 变差而 DMS 报警为 TP，报警但 PVT 正常为 FP，未报警但 PVT 很差为 FN | 内部验证要有同样的对照方法：采集 PVT 数据与 DMS 输出，按上述规则统计 TP/FP/FN。需要设计采集协议（受试者、时段、疲劳诱导方式），并考虑伦理与安全要求。 |
| R3 | Event-contingent tests：drowsiness alert → Safe stop → 10-min PVT + KSS | 疲劳算法需能与 PVT 对照，不能只靠 PERCLOS 等经验阈值；告警时间点和状态要有可追溯记录 | DMS 疲劳告警会触发一次停车后的 PVT 测试，因此每次告警的时间点、状态等级、触发依据都要被记录，便于与 PVT 结果对应。算法要给出可解释的中间量，而不只是最终告警。 |

## 页16\~17　通用车辆控制与 DM 的关系

**原文（页16）：** Driver wants to change temperature… poor UX forces driver’s gaze off-road for a few seconds… Driver Monitoring System issues an LGA distraction alert… **Poor UX design should not lead to reaching Driver Monitoring warning thresholds.**

**原文（页17）：** 2026 Interaction modality requirements for controls across most common tasks；2029 Focus on interaction quality — Introducing backstop for distraction warnings during normal controls interaction。

![](https://feishu.cn/file/Gkp0bhyK3o9AoVxAKkHcJQignAh)

![这是Euro NCAP文档的第17页，主题为通用车辆控制。页面左侧明确标注了两个时间节点的相关要求：2026年需覆盖多数常规车辆控制任务的交互模态要求；2029年将聚焦交互质量，引入常规控制交互过程中分心告警的兜底规则。页面右侧搭配了影视《黄金三镖客》的对应主题配图，以THE GOOD、THE BAD、THE UGLY的意象呼应不同的交互表现。该页对应解读2029版Euro NCAP中通用车辆控制与驾驶员监控的关联要求，和文档中ODMS针对操作中控、空调等场景的告警抑制策略的解读内容相呼应。](https://feishu.cn/file/HgygbxDg5oRUV8x79hKcWG2an9p)

**ODMS 关注点**

| 编号 | 原文要求 | ODMS 解读 / 需要的能力 | 详细说明 |
|-|-|-|-|
| R7 | Poor UX design should not lead to reaching Driver Monitoring warning thresholds；2029 backstop for distraction warnings during normal controls interaction | 操作空调、中控等所需的视线离路不应触发 DMS 告警 | 需要一套“控制操作期间”的告警策略：整车提供当前操作的任务类型，ODMS 在该期间延迟或抑制 LGA 告警，但仍保留“兜底（backstop）”上限，防止长时间离路。兜底的具体数值原文未给出，待正式协议。 |
| R7 | Interaction modality requirements for controls（2026）；Focus on interaction quality（2029） | 需从整车获取当前是否在操作车辆控制及任务类型，据此抑制或延迟 LGA；与 R9 的外部风险输入分开定义 | 接口文档里要把两类输入分开：①“车辆控制操作状态”→ 用来抑制告警；②“外部风险”→ 用来调整灵敏度。两者方向相反，混在一起会造成逻辑冲突，也会影响专利风险评估。 |

# 解读汇总：原文条目 → ODMS 技术解读

## 汇总

| 编号 | 原文位置 | 原文要求（摘要） | ODMS 技术解读 / 需要的能力 | 详细说明 |
|-|-|-|-|-|
| R1 | 页2 | 噪声下验证、自然驾驶评估、Driver State Link | 噪声工况测试体系；对外输出驾驶员状态接口 | ① 测试计划要同时覆盖：①受控条件下的功能测试；②加噪声的仿真/台架（夜间、强光、遮挡、不同人群）；③自然驾驶数据回放。每类测试要有明确的通过判据和数据留存，避免出现“实验室通过、实路误报高”的落差。  <br/>② 需要定义对外信号：状态类型（注意/分心/疲劳）、置信度、时间戳、更新频率、有效/无效标志。接口要预留与整车总线（CAN/以太网等）的映射，并与 OEM 的 ADAS 团队对齐延迟要求。 |
| R2 | 页6\~7 | 驾驶员注意状态作为 ADAS 平衡性能的上下文 | 注意/分心状态稳定、低延迟输出 | ① 产品定位上，ODMS 不仅是“报警器”，还是 ADAS 的输入源， 需要给ADAS输入更多的信息，如视线/等  <br/>② ADAS 会依赖注意状态做决策，状态抖动会放大误触发。建议对状态做滞回/平滑，并在方案里给出端到端延迟预算（相机曝光→算法→信号输出）。具体延迟指标需与 OEM 协商，原文未给出数值。 |
| R3 | 页8（1b/1c）、页14\~15 | 客观入睡验证，含疲劳加重与微睡眠窗口；10 分钟 PVT 为基准 | 可客观验证的疲劳/微睡眠检测；与 PVT 对照的采集与测试流程；报警事件可追溯 | ① 疲劳检测要输出分级（如逐步加重）和微睡眠事件，而不是单一阈值报警。需要建立“范围参数”（光照、头姿、遮挡、人群特征等）与检测性能的对应关系，便于做性能预测。验证数据要有客观标签（如 PVT/生理指标），不能只靠主观评分。  <br/>② 内部验证要有同样的对照方法：采集 PVT 数据与 DMS 输出，按上述规则统计 TP/FP/FN。需要设计采集协议（受试者、时段、疲劳诱导方式），并考虑伦理与安全要求。  <br/>③ DMS 疲劳告警会触发一次停车后的 PVT 测试，因此每次告警的时间点、状态等级、触发依据都要被记录，便于与 PVT 结果对应。算法要给出可解释的中间量，而不只是最终告警。 |
| R4 | 页8（1d） | 突发疾病、意识丧失检测 | 评估视觉方案覆盖程度，必要时规划多传感器 | 先评估纯视觉能做什么：长时间闭眼、头部无力下垂、无响应等可观测特征；原文提到的 DADSS 式触摸/呼气传感属于其他传感器，ODMS 是否纳入需产品决策。建议先做可行性评估 |
| R5 | 页8（2a/2b） | 实路误报被标注为接受度问题；鼓励参与而非惩罚 | 误报率目标；分级/正向的告警策略 | 告警要分级（提示→警告→干预），并支持延迟/抑制策略。需要内部误报指标：实路每百公里误报次数、用户可感知的骚扰告警占比；具体目标值需结合 OEM 要求，原文未给数值。HMI 形式（声音/视觉/触觉）由 OEM 决定，ODMS 提供可配置的触发条件。 |
| R6 | 页8（2c） | 注意力＝意识到路径上的物体，与 ADAS 干预挂钩 | 视线与前向感知目标关联 | 需要把视线方向换算到车辆坐标系，并与前向感知给出的目标方位对比，判断驾驶员是否看向了威胁。依赖：相机与车辆坐标系的标定、视线估计精度（尤其大角度）、前向感知的目标方位与时延。这条是后续 FTL/LFTS 的基础，也是接口设计的重点。 |
| R7 | 页8（3a\~3d）、页16\~17 | 语音与多模态控制、GVC 与 DM 耦合、个性化；控制操作期间分心告警兜底 | 接收车辆控制操作状态；操作期间抑制/延迟 LGA；驾驶员个人配置 | ① 需要整车提供“当前是否在操作车辆控制”的信号，ODMS 据此抑制/延迟告警（见页16\~17）。个性化方面，可预留驾驶员 ID 对应的参数配置（如灵敏度），但是否做、做到什么程度由 OEM 决定；涉及个人数据时要考虑隐私合规。  <br/>② 需要一套“控制操作期间”的告警策略：整车提供当前操作的任务类型，ODMS 在该期间延迟或抑制 LGA 告警，但仍保留“兜底（backstop）”上限，防止长时间离路。兜底的具体数值原文未给出，待正式协议。  <br/>③ 接口文档里要把两类输入分开：①“车辆控制操作状态”→ 用来抑制告警；②“外部风险”→ 用来调整灵敏度。两者方向相反，混在一起会造成逻辑冲突，也会影响专利风险评估。 |
| R8 | 页9 | Driver State + External events → DMS → ADAS；功能适配与注意力管理 | 明确 DMS 输入/输出边界；专利规避的分层设计 | ① 系统架构图里要画清两条输出：①给 ADAS 的状态/事件（功能适配）；②给驾驶员的告警（注意力管理）。输入侧要列出所有外部事件及其来源，并标明这些输入是进入 DMS 判定，还是只在策略层使用，这个区分与专利规避有关。  <br/>② 原文链路里外部事件会影响 DMS 输出，这与 Magna 55/56 的主题接近。是否构成侵权要逐个权利要求要素比对，本文不下结论。设计上建议：DMS 层只输出驾驶员状态，外部风险的引入放在策略层，并保留设计证据，由美国律师评估。 |
| R9 | 页10 | 短暂扫视≤1s；LGA 3\~4s→外部风险驱动；VATS 30s 窗口累计 | 高时间分辨率视线输出；阈值可配置、可动态调整；滑动窗口累计；手机使用检测 | ① 需要明确帧率、算法延迟和输出频率，使 ≤1s 的短暂扫视能被可靠检测。要验证快速扫视时的视线估计稳定性（眨眼、头动、遮挡下的表现）。  <br/>② 把 LGA 时间阈值做成可配置参数，并预留由策略层下发的接口。“外部风险驱动”由谁计算、谁下发要在接口文档里写清；美国版配置要与专利风险评估联动。  <br/>③ 实现 30s 滑动窗口内的累计离路时长，并输出累计值。手机使用检测要区分拿手机、看手机、通话等行为，验证不同手持姿态和遮挡情况。窗口和阈值要可配置，原文用的是示例值（e.g.）。 |
| R10 | 页10 | FTL（2029）、LFTS（2032） | 视线方向与碰撞路径威胁方位关联接口 | FTL：威胁在碰撞路径上，且与视线夹角大 → 判断为没看。LFTS：威胁在视线内但未反应 → 看了但没看见。需要：视线方向与威胁方位的时间同步、坐标统一、夹角阈值、视线有效性判断。LFTS 到 2032 才出现，可分阶段实现。页11 的 FTL 细节在另一场演讲，需补充获取。 |
| R11 | 页12 | 合成数据注入、传感器规格、真值、域差距校准 | 注入测试入口；传感器规格文档；TP/FP、TPR/FPR 统计；域差距评估 | ① 需要一个能把合成图像/特征注入 ECU 的测试模式（如视频输入或测试接口），并保证输出的状态结果带时间戳，便于与真值对比，统计各范围下的 TPR/FPR。该入口要与量产软件隔离或受控，避免安全风险。  <br/>② 向合成数据提供方交付传感器规格（分辨率、视场、波段、曝光等）。算法侧要能输出与真值对应的量：头姿（X/Y、yaw/pitch/roll）、视线向量、眼睑开度、遮挡与光照条件给到ADAS系统来决策。这些输出量也可用于内部调试。  <br/>③ 需要做同一场景下的合成结果与物理测试结果对比，度量差距并校准，才能证明合成数据可用于性能预测。要预先设计一组物理测试（基准集）与合成数据对应。原文的数据集规模（约 20/1000/20 例）以官方后续规定为准。 |
| R12 | 页13 | >2000 km 实路；夜间与强光为 DMS 噪声因素 | NIR/曝光/抗强光优化；事件记录与标注能力 | ① 夜间：NIR 照明强度、均匀性、曝光控制。强光直射：滤光、HDR/曝光策略、对太阳光干扰的抗性，DMS重点优化这些场景的图像效果。需要为这两类场景建立专项测试用例，并持续收集实路数据。  <br/>② 需要实路采集系统：记录状态输出、时间戳、关键中间量，必要时记录图像或特征。 |

## 提炼：对架构/算法的要求

1. **架构层（最重要）**：DMS 只输出驾驶员状态（视线、离路时长、VATS 累计、疲劳等级），预留外部目标/车辆控制状态输入，把"外部风险引入阈值"的策略放在策略层，欧美可分别配置。（R2、R6、R8、R9、R10）

<whiteboard token="KM81wBNjbh23ZybphDrcvxLsn3f"></whiteboard>

图：ODMS 分层架构（DMS 判定层只输出驾驶员状态，外部风险在ADAS策略层引入）



1. **算法层**：低时延视线/头姿、手机使用、疲劳与微睡眠的客观可验证检测、夜间与强光鲁棒性。（R3、R9、R12）
2. **验证层**：合成数据注入、域差距评估、实路事件记录、PVT 对照流程。（R1、R3、R11、R12）
3. **体验层**：误报控制、控制操作期间告警兜底、告警策略从惩罚转向鼓励。（R5、R7）
4. **待评估项**：突发疾病/意识丧失检测（R4）。



## **专利挖掘相关**

专利挖掘（基于 Euro NCAP 2029 新方向，初步，仅为专利方向构思，以及与美国9项高风险专利对比说明）

| 编号 | 关联 R | 挖掘点（发明构思） | 可写入权利要求的关键技术特征 | 风险与说明 | 可申请性 | 优先级 |
|-|-|-|-|-|-|-|
| P1 | R6 / R10 | 视线与威胁方位关联判定（FTL/LFTS） | 把视线射线换算到车辆坐标系；与前向感知威胁方位做时间同步；按视线置信度和有效性加权计算夹角；区分“没看”（夹角大）与“看了但没看见”（在视线内且无响应）；可结合威胁出现后的扫视时间窗。 | 与 Magna 55/56/193 主题邻近，需先做 FTO 和新颖性检索。本点必然引入外部输入，应落在融合/策略层，不要写成 DMS 判定层本身，以与规避设计保持一致。 | 高：构思明确、可落在融合/策略层，需检索确认新颖性 | 高优先级（先检索再决定权利要求范围） |
| P2 | R7 | 车辆控制操作期间的分心告警抑制，并设置兜底上限 | 整车提供当前操作的任务类型；ODMS 在该期间延迟/抑制 LGA 告警；兜底上限随任务类型和近期累计离路时长动态调整，超过上限仍告警。 | 此输入（控制操作状态）与外部风险输入方向相反，可与 P2 一同描述；是否落入 Magna 权利要求需比对，该输入不是车速/交通类。 | 高：输入与控制逻辑具体，与 Magna 外部风险类权利要求方向不同 | 高优先级（优先挖掘） |
| P3 | R3 | 以停车后 PVT 结果回灌、校准个人化疲劳阈值 | 疲劳告警或驾驶员自觉很困触发安全停车后做 PVT；将 PVT 结果与告警前后的 DMS 特征对齐；据此更新该驾驶员的疲劳判定参数或置信度。 | 涉及与外部测试结果的闭环，需确认实际产品能否实现（是否有 PVT 采集手段），可能更适合研发验证阶段的方法专利。 | 中：需确认产品能否实现 PVT 闭环 | 中优先级（视产品可实现性） |
| P4 | R4 | 无响应/意识丧失的视觉联合判定 | 长时间闭眼、头部姿态无力下垂、对告警无响应等特征的联合判定，并触发分级干预请求。 | 疲劳/无响应检测现有技术较多，需聚焦“告警无响应”这一联合特征；是否纳入产品范围待决策。 | 中：需聚焦“告警无响应”联合特征，现有技术较多 | 中优先级（先评估产品范围） |
| P5 | R11 | DMS ECU 的合成数据注入测试模式与域差距校准 | 测试模式下接受合成图像/特征输入；输出带时间戳的状态；对同一场景的合成与物理测试结果计算域差距并校准输出阈值或置信度。 | 偏测试方法，需检索是否已有相近“域差距校准”方案；价值取决于是否成为行业通用做法。 | 中：视检索是否已有域差距校准方案 | 中优先级（视检索结果） |
| P6 | R8 / R9 | 驾驶员状态与外部风险分层的系统架构 | DMS 层仅输出驾驶员状态（视线、离路时长、VATS 累计、疲劳等级）；策略层再接入外部风险/车速等并下发灵敏度；两层之间接口信号及更新方式。 | 架构本身偏防御性，侵权发现难；但能把“规避设计”固化为公开文献，防止被他人占位。 | 低：偏防御性公开，侵权发现难 | 低优先级（可做防御性公开或方法+系统组合） |
| P7 | R9 | 滑动窗口累计离路时长，并按任务类型（手机/非驾驶任务）区分累计 | 在滑动窗口（如 30s）内累计离路时间；对手机使用与其他任务分别累计；窗口和阈值可配置；累计值作为状态输出。 | 累计视线时间类的现有技术较多，新颖性风险高，需检索确认；建议与 P1/P4 的特征组合后再评估。 | 低：现有技术较多，宜作从属特征 | 低优先级（作为从属特征） |
| P8 | R12 | 实路事件的低隐私风险记录与 FP/FN 对齐 | 触发事件时记录特征而非原始图像；记录时间戳、状态输出和关键中间量；与人工标注或后续 PVT 结果对齐，自动生成误报/漏报标签。 | 偏数据采集与验证方法，侵权发现难，但对内部验证效率有价值；需看是否有创新性。 | 低：偏数据采集与验证方法 | 低优先级 |
| P9 | R12 | 夜间/强光场景下的 NIR 照明与曝光自适应 | 检测太阳光干扰或夜间低照度；自适应调整 NIR 强度、曝光和滤光；保持视线/眼睑估计稳定。 | 该方向现有技术很多，建议结合我们具体光学/结构方案的差异点再评估。 | 低：现有技术很多，需结合硬件差异点 | 低优先级（需结合硬件差异点） |

## 待确认

1. ODMS 当前形态与对外接口范围。
2. 前向感知信号是否可由整车提供，及其时延。
3. 页11 FTL 深度内容在另一场演讲中，需补充获取。