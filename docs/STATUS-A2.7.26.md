# A2.7.26 — 調料雪克瓶手持／放置模型熱修

> 本批只處理使用者實機截圖中的「雪克杯拿在手上變成薄片、放到世界後變成整顆方塊」；不順手改指南、配方或其他物品，保持小批可回測。

## 實機症狀

使用者在目前已發布版本回測到兩個直接可見的問題：

1. 調料瓶／待搖晃調料拿在手上時，第三人稱只看到一條很薄的 2D item icon。
2. 放置一瓶調料後，世界模型不是 Java 原作瓶身，而是把調料瓶貼圖鋪在完整 1×1×1 方塊上。

A2.2 當時只做了 Dash／結構驗證，文件已明確標記 Minecraft/BDS 未實機驗收；這次截圖把該缺口實際暴露出來。

## 手持根因與修法

目前三個瓶類 item：

- `empty_seasoning_bottle`
- `pending_seasoning`
- `special_seasoning`

都設了 `minecraft:hand_equipped=true`，但 gameplay_core 裡沒有對應 attachable。結果就是 Bedrock 只能把 2D icon 當作手持物處理，從側面看會變成截圖中的薄片。

工程內其實已有一份 A1.16 immersion-lab 的獨立手持調料瓶原型：

`projects/grilling/integration/immersion_lab/resource_pack/models/entity/hand_props.geo.json`

把同一份一瓶 shell 與該原型逐 cube 比對，四個代表性部件（瓶身、肩部、木塞、標籤）的空間差都一致為：

`[0, -6, 0]`

因此本批不猜角度，也不直接二次套 Java display rotation；做法和 A2.7.25 烤串錨點修正相同：

- 新增共用 seasoning-bottle hand geometry；
- root 綁定 `q.item_slot_to_bone_name(context.item_slot)`；
- 第一／第三人稱都套用已由工程內原型證實的本地 offset `[0,-6,0]`；
- 三個瓶類 item 共用同一份 attachable shell。

## 放置模型根因與修法

Java `seasoning_bottle.json` 的 `spice_empty` 是一個「空內容」佔位平面：

- `from=[5.5,0.5,5.5]`
- `to=[10.5,0.5,10.5]`

它本身高度為 0，但 Java 檔仍列出六個 face。舊轉換把它原樣輸出成 Bedrock `size=[5,0,5]` 且保留六個 face；其餘九個瓶身 cube 都是正常正體積。

Bedrock 本身可以有平面幾何，所以這裡不把「零厚度」一概判成非法；但這個 **空內容、六面、零高度** 的轉換結果既沒有可見內容價值，也正好是這組瓶模型相對正常 shell 的唯一退化結構。實機又已出現 geometry fallback 方塊，因此本批把它從空瓶 shell 移除，並做兩層保險：

1. legacy + 1～4瓶共 **5 組 geometry** 全部去掉 `spice_empty` 佔位 bone，留下的 cube 尺寸全部嚴格大於 0。
2. 5 組模型全部換成新的 `geometry.kg_a2726.*` identifier，避免更新包後仍命中舊資源識別。
3. block reference 同步指向新 identifier。
4. Java 原模型 `ambientocclusion=false` 對齊為 Bedrock `ambient_occlusion=0.0`，並關閉 `face_dimming`。

共移除 **11 個**空內容平面（legacy 1 + 1/2/3/4 瓶各 1/2/3/4）。

## 這批刻意沒有做的事

Java 的 `special_seasoning` 會依 remaining / variant 切換不同內容量與配色。這批先把「拿在手上是一個正確的 3D 瓶」和「放下去不再退回完整方塊」修好；pending/special 的動態填充外觀留給下一個獨立小批，避免把 hotfix 跟完整動態 renderer 混在一起。

所有調料 ingredients / uses / variant 動態資料與既有四瓶堆疊腳本都不改。

## CI 驗證

A2.7.26 workflow 會：

- 先驗證已發布 A2.7.25；
- 套用本批 augmentation；
- 驗證 5 組 placed geometry 都沒有 `spice_empty` 且所有 shell cube 為正體積；
- 驗證 block → geometry identifier 一一對應；
- 驗證三個瓶類 item 都有 attachable；
- 用 immersion-lab 原型證明手持 offset 確實是 `[0,-6,0]`；
- 檢查全部 gameplay JS 語法；
- 用固定 SHA-256 的官方 Dash v1.2.0 編譯並逐檔比對；
- 產出可直接回測的 A2.7.26 mcaddon / brproject。

仍保持：

- `minecraft_tested=false`
- `bds_tested=false`

這兩個旗標要等新的 A2.7.26 構件在遊戲裡實際回測後才改。
