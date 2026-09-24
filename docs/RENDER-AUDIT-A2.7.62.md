# Canonical Render Audit — A2.7.62

本報告針對使用者實機回報「多個模型多少都有渲染問題」做正式 Gameplay Core 全鏈靜態排查。

## 掃描範圍

Canonical CI 的 `tools/audit_grilling_render.py` 會掃描：

- 238 個 geometry identifier
- 29 個 animation
- 4 個 render controller
- 23 個正式 block
- 43 個 attachable
- block geometry/material/terrain atlas 引用
- attachable geometry/texture/animation/render-controller 引用
- bone parent / binding / cube size
- attachable animation 是否直接 transform 已綁 item slot 的 bone
- 已保存的 Java display transform 與目前 Bedrock held chain 的已知 parity gap

A2.7.62 audit run 的結果：

- error: **0**
- high: **119**
- medium: **0**
- info: **2**

兩個 info 是 `textures/blocks/water_still_grey` 與 `textures/blocks/lava_still`。它們是 Mojang Bedrock vanilla resource sample 內存在的基礎資源路徑，因此不是 canonical RP 缺檔。

## High findings 分組

### 1. 39 個固定烤串：動畫直接移動 bound root — 78 項

所有 39 個正式 skewer attachable 的 bite geometry 都把 `root` 綁到：

`q.item_slot_to_bone_name(context.item_slot)`

但正式 `a2725_skewer_hold.animation.json` 的 first-person / third-person 動畫又直接對 `root` 做：

`position: [0, 7, 2]`

因此每個 attachable 有兩項 high finding，合計 78。

這不是純理論風險。專案自己的 immersion-lab `geometry.kg_imm.hand_skewer` 已經採用相反、較穩定的結構：

- bound `prop` 本身不動；
- `[0,7,2]` 已 bake 到 child bite geometry 座標。

這與 A2.7.33 調料瓶 corrective 的經驗一致：不要用 animation 移動已綁手的 root。

### 2. 37 個固定烤串：Java display transform 尚未真正移植 — 37 項

Java fixed skewer 模型有完整 first/third-person rotation / translation / scale。以 beef 為例：

- third-person: rotation `[-98.57,1.45,-174.51]`, translation `[0.75,6.25,5.5]`, scale `0.8`
- first-person right: rotation `[-95,-7,-163]`, translation `[-1,7.75,7.25]`, scale `0.8`
- first-person left: rotation `[-94,0,-165]`, translation `[-1.5,7.25,7]`, scale `0.8`

目前正式 Bedrock attachable 沒有使用這些 transform，只使用通用 A2.7.25 root position。因此「能拿在手上顯示」不代表 Java 手持姿勢已移植。

37 而不是 39，是因為 auditor 只把能直接對應到現有 Java display report 的項目計入這一類；39 個仍全部受 bound-root 問題影響。

### 3. 調料瓶 — 3 項

`empty_seasoning_bottle`、`pending_seasoning`、`special_seasoning` 在 A2.7.33 已修掉「bound root 動畫把瓶子拉到玩家腳附近」的主要錯位，現在的 hand shell anchor 是安全的。

但 Java `seasoning_bottle` display 仍有：

- third-person rotation `[29.5,45,0]`, translation `[0,3,2.75]`, scale `0.5`
- first-person rotation `[-180,60.25,-180]`, translation `[0,5,0]`, scale `0.72`

這些尚未套到目前 attachable，所以仍可能存在「位置大致正常、角度/大小總覺得不對」的實機差異。

### 4. Advanced Rack — 1 項

Java `advanced_rack_0..4` 都有同一組明確 display transform：

- third-person right/left: rotation `[75,45,0]`, translation `[0,2.5,0]`, scale `0.375`
- first-person right: rotation `[0,57,0]`, scale `0.4`

但正式 RP 沒有 `kaleidoscope_grilling:advanced_rack` attachable，手持只能走預設 item/block 顯示路徑。

原 Java model 本身只定義 first-person right，沒有 first-person left；因此 corrective 不應自行臆造左手 transform，需按 Java 缺省/Bedrock fallback 做單獨設計與實機驗證。

## 世界模型結論

目前 audit 沒有找到以下硬錯：

- 缺 geometry identifier
- attachable 缺 geometry
- 缺 animation
- 缺 render controller
- 方塊 geometry 混入 item-slot binding
- 負 cube size
- 兩軸以上為 0 的 line/point degenerate cube
- geometry 使用未定義 material_instance slot

269 個單平面 cube 被統計，但這一類大量來自 Java 模型有意製作的 inward face、薄片、植物與液面，不能機械判錯。

烤架 `legged=true` 主 block 仍引用 flat shell 也不是直接 BUG：正式 runtime 會在下方生成獨立 `kaleidoscope_grilling:grill_legs` helper block，避免把腿和主方塊 collision 混在同一格。

## 修復優先序

建議維持小批次：

1. **Seasoning held transform parity**：只有 3 個 attachable，已有 A2.7.33 安全 hand-space 基線，風險最低。
2. **Advanced Rack held path**：新增專用 attachable，但 Java 沒提供 first-person left，需要明確保留 fallback，不自行偽造 parity。
3. **Skewer held architecture**：先把 39 個 attachable 從「動畫搬 bound root」改成 child/display transform；再把 Java display transform 接進 first/third-person。
4. 最後再用實機截圖調整 FOV/左手/第三人稱，不拿靜態 CI 代替客戶端像素驗收。

## 驗證邊界

Render Audit 是靜態鏈檢查。它能證明引用、bone ownership、geometry/material contract 與已知 Java transform drift；不能證明特定 Minecraft 客戶端/GPU 最終像素、FOV、皮膚交互、Android 透明排序或動畫實際觀感。


## A2.7.64 follow-up

A2.7.63 已消除 seasoning 3 项与 Advanced Rack 1 项 high finding。

A2.7.64 随后迁移全部 39 个 fixed-skewer attachable 与 150 个 bite geometry；迁移脚本核对 264 份 fixed-skewer Java display report。迁移后的实际 Render Audit：

- error: **0**
- high: **0**
- medium: **0**
- info: **2**

因此 A2.7.62 初始的 119 个 high finding 已全部从 canonical render chain 中消除。两项 info 仍是合法的 vanilla water/lava base-resource reference。
