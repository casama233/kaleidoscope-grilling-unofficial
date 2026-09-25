# Guide A2.0 — Complete Player Manual

Guide A2.0 是对烟火游戏内手册的一次信息架构重做，不是在 A1.16 的 33 条静态目录上继续补句子。

## 为什么重做

A1.16 的玩家指南有三个核心问题：

1. 只有 `how_to / recipes / seasonings` 三类，后期加入的榨油、大缸、Advanced Rack、烟火气、作物加工和排错内容被挤在少数页面里。
2. 20 个固定串配方页大部分重复“穿好后刷油、翻面、调味”，既浪费页面，也没有告诉玩家每根熟串的实际效果。
3. 内容是 A1.x augmenter 硬编码输出，和当前 A2.7.x Gameplay Core 没有直接静态契约，功能演进后容易悄悄陈旧。

A2.0 改成“一个内容源 → 生成正式 payload / lang → runtime-fact checker → Dash compiled compare”的发布链。

## 玩家看到的结构

保持 Cookery 原指南里**一个**“森罗物语：烟火 / Kaleidoscope Grilling”入口，不新增物品或第二本书。

共 5 个章节、52 个主题：

| 章节 | 数量 | 内容 |
| --- | ---: | --- |
| 快速上手 | 4 | 六步烤制、烤架操作、过熟/烧焦时序、手工穿串 |
| 设备与加工 | 12 | 串盘、串谱、榨油器、大缸、厨具架、作物与原料加工 |
| 烤串配方 | 20 | 固定材料顺序 + 熟串实际效果/基础时长 |
| 调料与烟火气 | 9 | 调料制作、三种油、Hot Food、六类强化材料、容量/消耗 |
| 进阶与排错 | 7 | 烤架拒绝原因、中途拆炉、热串整理、秘制串、普通串挑战、凉拌折耳根、世界油 |

`showAll=false`，避免在 Cookery 的 ActionForm 中一次塞 52 个按钮；玩家先选章节，再选主题。

## 烧烤流程只讲一次

快速上手页现在明确给出：

**点火 → 放 1–3 根生串 → Cookery 油壶刷油 → 空手翻 4 次 → 特制调料 → 空手取出**

同时写明：

- 每次翻面约 1 秒 cooldown；
- 当前加热阶段约 40 秒不推进会过熟；
- 过熟再约 20 秒会烧成木炭；
- 潜行空手可连续取出；
- 原版铲子 / Cookery 厨房铲可熄火。

配方页不再重复这套流程。

## 配方页现在有决策价值

20 个固定/特殊串保留当前 canonical `a24_skewering_core.js` 的材料顺序。

19 个熟串页面同时显示当前 `data.js` 的固定效果与基础时长，例如：

- 牛肉串：Strength 10s
- 鸡皮串：Speed 20s
- 鱼串：Tundra Strider 30s
- 末影珍珠串：Projectile Dodge 30s
- 煎蛋串：Sulfur 60s
- 黄金烤串：Invincible 10s

“普通”烤串单独标注为致命挑战，不伪装成普通生→熟配方。

## 设备与加工

指南现在直接解释当前 Bedrock canonical runtime：

### 榨油器

- 4 个油饼一批；
- 16 点榨油进度；
- 铁砧 +4；
- 石头/圆石/深板岩/深板岩圆石/黑石 +1；
- 必须有附近大缸一次接下 4 桶菜籽油；
- 成功后 4 桶菜籽油 + 4 油渣。

### 大缸

- 8 桶容量；
- 单一流体；
- 支持水、熔岩、菜籽油、秘制辣椒油、高级辣椒油；
- 1 桶烟火油 = Cookery 油壶 8 点；
- 打掉后保留流体种类与桶数。

### Advanced Rack

- 9 格：5 调料 / 4 工具；
- 首次存入建立筛选；
- 同家族油壶 / 调料瓶状态共用过滤语义；
- 支持交换、存入、取回、清筛选、按已有筛选批量存入；
- 8 格有效操作距离；
- 打掉后保留内容与筛选。

## 调料与烟火气

指南按当前 runtime 区分两套时长规则：

### 固定熟串效果

趁热吃时：

- 新获得的固定熟串效果时长 ×2；
- 新增 saturation ×1.25。

### Special Seasoning

只有食物仍有烟火气时才触发，但**不会再被烟火气二次翻倍**。

基础规则：

- 每瓶最多 8 份材料；
- 世界中最多堆 4 瓶；
- 青/绿辣椒粉 + 花椒 + 洋葱粉是完成调料的三种基础料；
- 完成瓶 16 次使用；
- 对烤架一次消耗“架上串数”这么多次。

强化：

- 红石：Speed I；4+ → II
- 火药：Strength I；4+ → II
- 折耳根粉：时长 ×2；4+ → ×4
- 花椒 4+：Numb，基础 45s
- 不死图腾粉：Heavy Metal；致命伤保到 1HP，触发后 Heavy Metal Poisoning 约 10min
- 龙蛋粉：Dragon Blood

三种油的烟火气窗口：

- 菜籽油：约 60s
- 秘制辣椒油：约 10min
- 高级辣椒油：约 20min

## 原料链与特殊取得

A2.0 也补上了旧指南基本没讲的玩家路径：

- Canola Seeds → Millstone → Canola Powder → Oil Cake → Oil Press
- Sweet Potato → Millstone → Sweet Potato Powder → Raw Sweet Potato Sheet
- Sweet Potato Powder 也可持续使用约 1.5s 直接揉成生苕皮
- Carrot / Potato / Mantou 的 4-cut Chopping Board 加工
- 完成 Chopping Board 生鸡肉切割时取得 Chicken Skin
- 用 Cookery kitchen knife 杀鸡取得 Chicken Wing（Looting 可影响数量）
- Sichuan Pepper Tree 的生长、结果、空手采收与刺伤
- Cold Houttuynia：工作台旁潜行，主手 3 折耳根 + 副手 Premium Chili Oil Pot，消耗 2 点油，成品约 60s Fire Resistance

## 进阶排错

新增一页专门回答：

- 为什么不能放串？
- 为什么油壶没刷上？
- 为什么空手不翻？
- 为什么不能撒料？
- 为什么不能取出？

不再要求玩家从内部 phase 数字猜状态。

同时说明中途拆炉的 raw / cooked / Dark Grilling / Mysterious Skewer 掉落结果，以及热串在 Chest / Trapped Chest / Barrel 中的 5 分钟热度差整理规则。

## Canonical authoring

唯一当前内容源：

`projects/grilling/guide/content.a2.json`

生成：

`python tools/build_grilling_guide.py`

验证：

`python tools/build_grilling_guide.py --check`
`python tools/check_grilling_guide.py`

A1.x `content.json` 与 `development/guide/augment_a*.py` 降为历史重放/取证，不再覆盖正式 A2.0 guide。

## Cookery 1.0.6 host

仍使用已验证的 **KC Guidebook Extension API v1**：

- entry id 保持 `kg_a1:grilling`；
- 不创建独立 guidebook item；
- publisher 不读取玩家 inventory/world；
- host 自己保存每玩家语言 `kc:guidebook_language`。

原始 Cookery 1.0.6 的 `mechanicsByLocale` locale validator 有已确认兼容问题。Canonical Guide CI 会继续从 checksum-pinned 原包生成窄范围 locale-compat 候选，只修改这个 validator；不修改 Cookery gameplay、UUID、配方或 UI 流程。

Guide API v1 仍是静态目录，因此本批不伪造搜索、收藏或自定义配方持久化功能。

## 验证边界

新的 checker 会把指南中的关键数字与当前 Gameplay Core 静态绑定，包括：

- grill 800/400 ticks、4 flips、20 tick cooldown；
- Oil Press 4 cakes / 16 progress / 4 output；
- Big Vat 8 buckets；
- 三种油 heatTicks；
- seasoning 8 ingredients / 4 bottles / 16 uses；
- Advanced Rack 9 slots / 8 range；
- 20 fixed recipe rows；
- 19 cooked-effect durations。

Canonical CI 还会：

- 确认 52 条 × 3 locale；
- 确认本地图标存在；
- 确认旧复制粘贴配方句子没有回来；
- 确认 API v1 chunk 容量；
- 用官方 checksum-pinned Dash 编译；
- 逐档比较 source 与 compiled output；
- 生成 deterministic Guide A2 mcaddon；
- 生成 Cookery locale-compat review artifact。

这些检查不能证明 Minecraft 触控/控制器 UI、字体换行、真实客户端颜色/图标观感或 BDS 多人环境；仍需实机验收。
