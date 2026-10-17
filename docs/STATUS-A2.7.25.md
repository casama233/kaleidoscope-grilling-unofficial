# A2.7.25 — 烤串手持錨點修正

> 本批只修使用者實機截圖中「任何烤串拿出來位置不對」的共通問題，不同時改指南 UI，避免一次修改面過大。

## 根因

A2.2 之後的 39 個正式烤串 attachable 都直接把來源幾何的 `root` 綁到：

`q.item_slot_to_bone_name(context.item_slot)`

但來源幾何仍以模型自身原點為基準，缺少先前 A1.16 玩家綁定原型已使用的「手持空間錨點」位移，所以第一人稱實機會看到整根串落在手的下方／外側。

倉庫內已有一份獨立生成的 A1.16 hand-prop 基線：

- `development/player_binding/build.py`
- `projects/grilling/integration/immersion_lab/resource_pack/models/entity/hand_props.geo.json`

用同一份 raw beef 來源比對，A2.2 stage0 → A1.16 hand prop 的空間差正好是：

`[0, +7, +2]`

例如木籤 cube：

- A2.2 stage0：`[-0.25, 0.75, -8]`
- A1.16 hand prop：`[-0.25, 7.75, -6]`

因此這不是逐串模型本身壞掉，而是 39 個 attachable 共用的錨點漏掉。

## 修法

不重烘 150 份逐口 geometry，也不逐個手改模型。

新增共享 attachable 動畫：

- 第一人稱：root position `[0,7,2]`
- 第三人稱：root position `[0,7,2]`

並依官方 attachable 模式用：

- `context.is_first_person == 1.0`
- `context.is_first_person == 0.0`

切換相同的本地錨點。

這樣：

1. 39 個串共用一份修正。
2. 原本 `item_in_use_duration` 的逐口 stage 判定不動。
3. 150 份來源 geometry 不重烘，方便後續繼續對 Java 模型。
4. 主／副手仍由 `item_slot_to_bone_name` 自動綁定。

## 為什麼沒有直接照抄 Java display rotation

Java 的模型 JSON 同時帶第一／第三人稱 `display` rotation/translation/scale；Bedrock 的 item-slot binding 已先套用玩家 `rightItem/leftItem` 與視角基準。

直接把 Java display rotation 再套一次會有二次旋轉風險。因此本批先恢復已由本工程 A1.16 hand-prop 證實遺漏的本地位移，不憑空猜新的角度。

如果實機回測後仍有「角度對但需要微調」的情況，再以截圖做下一個小批，不把位置修正和角度調校混在一起。

## 驗證

CI 會確認：

- 基線是已發布 A2.7.24。
- 39/39 skewer attachable 都引用共享 hold 動畫。
- 原 `pre_animation` / `item_in_use_duration` 邏輯仍存在。
- raw beef stage0 原始 geometry 沒被改寫。
- A1.16 hand-prop 與 A2.2 raw beef 的實際座標差確為 `[0,7,2]`。
- 官方 Dash v1.2.0 編譯後逐檔與 source 一致。
- 打包新的 mcaddon / brproject。

仍保持：

- `minecraft_tested=false`
- `bds_tested=false`

本批的目標就是讓使用者下一次實機回測能直接判斷「手持串的位置是否回到手上」。
