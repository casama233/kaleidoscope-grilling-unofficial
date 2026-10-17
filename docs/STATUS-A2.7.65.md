# A2.7.65 — Full Skewer Hand Geometry

A2.7.64 先以 raw beef / grilled beef / ordinary 三個代表樣本驗證 baked hand-space geometry 路線；A2.7.65 將同一規則擴到全部 39 個烤串 attachable 與 150 個 bite-stage geometry。

## 完整轉換

來源：
`resource_pack/models/entity/a22_bites/`

輸出：
`resource_pack/models/entity/a2764_skewer_hand/`

固定轉換：
`[0,+7,+2]`

此值不是新的目測調參，而是 A2.7.25 已用 A1.16 `geometry.kg_imm.hand_skewer` 與 raw beef stage0 證明的精確空間差。

每個 geometry：

- root pivot 維持 [0,0,0]
- root binding 維持 q.item_slot_to_bone_name(context.item_slot)
- 非 root bone pivot + [0,7,2]
- cube origin + [0,7,2]
- cube rotation pivot + [0,7,2]
- UV / size / rotation / hierarchy 不變

## Runtime 切換

39/39 skewer attachable 現在：

- geometry 全部使用 `geometry.kg_a2764.*`
- 保留原 `pre_animation` bite-stage 時序
- 保留原 stage textures
- 保留 `controller.render.kg_a22.bite`
- 不再有 `scripts.animate` hold entry
- 不再有 `animations.hold_first_person`
- 不再有 `animations.hold_third_person`

`a2725_skewer_hold.animation.json` 僅作歷史重建保留，正式 runtime 引用數必須為 0。

## Fail-closed 驗證

`verify_a2765.py` 要求：

- A22 source geometry = 150
- A2764 baked geometry = 150
- 檔名集合完全一致
- 生成器 `--check` 能逐檔結構重建
- skewer attachable = 39
- A2764 geometry runtime references = 150
- A2725 hold animation runtime references = 0

## 驗證邊界

這批修的是已知與 Tavern 雪克杯相同類型的 attachable/root-transform 架構問題；CI 可以證明 geometry 轉換與引用鏈一致，但不能代替 Minecraft 實機的 FOV、第三人稱、左右手與動畫畫面驗收。

- minecraft_tested=false
- bds_tested=false
- client_visuals_tested=false

本批沒有修改配方、營養、烤製、穿串、進食時序、粒子或聲音。
