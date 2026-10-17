# A2.7.64 — Skewer Held Geometry Corrective

本批按「先小樣、再全量」處理使用者回報的烤串手持錯位。問題類型與 Tavern 雪克杯一致：不要再依賴 bound root animation 修正整個模型位置，而改成 hand-space geometry。

## 第一階段：3 個代表樣本

只切換：

- raw_beef_skewer
- grilled_beef_skewer
- ordinary_skewer

共 14 個 bite-stage geometry（5 + 5 + 4）。

來源仍是 A2.2 的 `models/entity/a22_bites`，輸出到：

`models/entity/a2764_skewer_hand/`

## 轉換規則

A2.7.25 已證明 A1.16 的獨立 hand prototype 相對 raw beef A22 geometry 是精確的：

`[0, +7, +2]`

A2.7.64 將這個平移烘入 root 以下的 geometry：

- root pivot 維持 [0,0,0]
- root binding 維持 q.item_slot_to_bone_name(context.item_slot)
- 非 root bone pivot + [0,7,2]
- cube origin + [0,7,2]
- 有 rotation pivot 的 cube pivot 同樣 + [0,7,2]
- UV / size / rotation / hierarchy 不變

生成器：

`development/gameplay_core/a2764_rebake_skewer_hand_geometry.py`

CI 會用 --check 要求 14 個輸出可逐字重建。

## attachable 變更

三個樣本：

- geometry alias 改指 geometry.kg_a2764.*
- 移除 hold_first_person / hold_third_person animations
- 移除 scripts.animate 的 root hold animation
- 保留原 bite-stage pre_animation
- 保留 controller.render.kg_a22.bite
- 保留原 stage texture

其餘 36 個串暫時仍使用 A2725 路線，直到樣本完成 Minecraft 第一/第三人稱實機驗收。

## 為什麼不立即全量 39 個

CI 可以證明幾何平移可重現、引用鏈完整、Dash 可編譯，但不能證明實際 FOV/手部位置美觀。

所以此版本故意是 sample validation：

- sample = 3
- baked stage geometry = 14
- remaining A2725 attachables = 36

實機確認三個樣本不再掉到腳邊/嵌進身體後，再用同一生成器批量轉剩餘 136 個 stage geometry。

## 驗證邊界

- minecraft_tested=false
- bds_tested=false
- client_visuals_tested=false

本批不修改配方、營養、進食時序、粒子、聲音、烤爐或穿串 gameplay。
