# A2.7.33 — 雪克杯／調料瓶手持與放置顯示修正

本批只處理使用者補充確認的兩個顯示問題，不改配方、指南、調料邏輯或其他玩法。

## 使用者補充後的正確症狀

1. 手持時不是單純「2D 薄片」，而是雪克杯 3D 模型錯位到玩家腳／小腿附近，像是跟角色下半身嵌在一起。
2. 放置後不是普通棕色方塊，而是接近 Bedrock 自訂方塊 geometry / material 失敗時的整塊 fallback 外觀；頂部又似乎殘留少量杯頂視覺。

因此 A2.7.26 對手持問題的處理需要修正：不能把「方塊空間的一瓶 shell + 綁定 root」再用 root animation 向下移。

## 手持修正

工程裡已經有一份獨立的 immersion-lab 手持調料瓶：

- geometry.kg_imm.hand_seasoning
- root/prop 直接綁定 q.item_slot_to_bone_name(context.item_slot)
- 沒有額外 root hold animation
- 瓶身 cube 本身已經在正確的 hand-space 座標

A2.7.33 直接遵循這個模式：

- 從目前已清理的一瓶 shell 生成新的 geometry.kg_a2733.seasoning_bottle_hand。
- 將 Y=-6 烘焙進每個 shell bone/cube 的座標，而不是動畫移動已綁定到手骨的 root。
- root 只負責 item-slot bone binding。
- 三個瓶類 item 都移除 A2.7.26 hold animation / animate script 引用。
- 使用獨立、最小的 seasoning-bottle render controller，避免 item_default 引入額外假設。
- CI 將新 hand geometry 的每個 shell cube 與 immersion-lab 原型逐一核對。

這樣修的是「模型坐標系／錨點」本身，而不是繼續猜一個 root 位移。

## 放置修正

A2.7.26 已移除了 Java 空內容 placeholder 轉換出的退化 spice_empty plane。A2.7.33 再把 placed resource chain 做成一次完整 refresh：

- legacy + 1/2/3/4 瓶共 5 組 geometry 全部換成 geometry.kg_a2733.*。
- block 的 minecraft:geometry 改成目前 schema 的顯式 identifier object。
- 不存在 minecraft:geometry.full_block fallback。
- 新增 fresh terrain atlas key：
  kg_a2733_seasoning_bottle -> textures/blocks/seasoning_bottle
- 5 個 placed block 全部改用這個新 atlas key。
- 維持 blend，因為 Java spice jar 含玻璃／透明視覺；不為了繞 bug 把材質錯改成 opaque。
- 所有 placed shell cube 必須為正尺寸，且不能有 item-slot binding。

這一批同時刷新 geometry identifier 與 terrain atlas key，避免更新後仍命中舊 geometry/material 資源鏈。

## 不做的事

- 不改 pending/special seasoning 的 remaining / variant 動態填充。
- 不改調料 uses、配方、堆疊或放置邏輯。
- 不改其他烤串／料理內容。
- 不刪 A2.7.26 舊 hand animation 檔，因為歷史 slice 重建仍可能引用；正式 attachable 已不再引用它。

## 驗證

A2.7.33 CI：

- 驗證正式 A2.7.32 baseline。
- 套用本批 augmentation。
- 逐 cube 比對新 hand shell 與 immersion-lab hand-space 基準。
- 確認三個 attachable 不再引用 A2.7.26 root hold animation。
- 驗證 5 個 placed blocks 都只指向 A2.7.33 custom geometry。
- 驗證 fresh terrain atlas key 與 PNG 路徑存在。
- 驗證全部 placed cubes 為正尺寸。
- 跑全部 gameplay JS 語法檢查。
- 用 checksum-pinned Dash v1.2.0 編譯並逐檔比對。
- 打包可直接進遊戲回測的 mcaddon / brproject。

仍保持 minecraft_tested=false / bds_tested=false，直到新構件由 Minecraft 實機回測。
