# A2.8.1 — 大缸手持與調料瓶圖示修正

針對 A2.8.0 玩家截圖：大缸第一人稱遮屏、第三人稱位於腳前；空調料瓶圖示顯示整張 UV 材質。這些是真實客戶端缺陷回報，不把先前 CI 通過視作畫面驗收。

## 大缸：回到原生方塊物品渲染

停用 `kaleidoscope_grilling:big_vat` 的自訂 attachable，原檔逐位元組保存到 `history/a281-retired/`。原配置使用與玩家骨骼名稱相關的手別條件，並把 Java item display 直接接在 entity 子骨骼上；該路徑在回報環境顯示錯誤。沒有 Content Log 和客戶端除錯器，不能斷言是其中哪個 Molang 條件或皮膚骨架導致，但不再保留這條多餘的渲染路徑。

大缸 `minecraft:item_visual` 現在引用既有、無玩家骨骼綁定的空缸 geometry，由引擎負責手持／GUI／掉落顯示。固定 Java 大缸的七種 display 場景與官方列出的 Bedrock 預設值一致：第一人稱比例 0.4、第三人稱 0.375、GUI 0.625、掉落 0.25、展示框 0.5；GUI 的 -135° 與 225° 為同一旋轉。沒有新增魔法位移、額外骨骼縮放、實驗性 `item_display_transforms` 或玩家 JSON 覆寫。

官方參照：
- https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/blockcomponents/minecraftblock_item_visual
- https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/itemdisplaytransforms

物品只畫空缸，不繼承某一個液位的 fluid material。**世界放置模型、缸體碰撞、狀態、容量、交互、儲存鍵和配方完全不變。** 其他物品的手持模型不在這一批更改，不能將大缸修復推論為全部皮膚／attachable 已通過。

## 調料瓶：模型材質不再當 UI sprite

A2.8.0 的 `empty_seasoning_bottle`、`pending_seasoning`、`special_seasoning` 三個 UI PNG 與 `textures/blocks/seasoning_bottle.png` 位元組相同，都是 32×32 的材質圖。這正是截圖所見的彩色拼圖來源。

本版沿用已保存的 Java 瓶身、面 UV、GUI 朝向及原材質，輸出 64×64 透明背景的瓶身 sprite；光柵化按每像素深度混合，保留玻璃透明度。沒有重畫原材質、替換玩家物品 ID 或改動 64 種手持調料狀態。

空瓶與待調配瓶使用 Java 零配料預設外形；完成調料的靜態圖示以滿瓶 variant 0 表示。**這批不宣稱背包圖示會即時反映每份配料、uses 或所有 variant。** 原有實際手持／放置狀態顯示仍由既有系統負責。

指南的調料圖示副本與來源 SHA 同步更新；指南仍在煙火本體、Cookery 同一本指南內。取色生成器對這三類模型物品使用原瓶身材質，避免 UI sprite 改動意外改變已固定的放置配料色盤。

衍生圖示沿用 LICENSE-ASSETS（CC BY-NC-SA 4.0）及原 Grilling 美術歸屬。來源檔與圖示像素指紋列於 `reports/a281-vat-icons.json`。

## 驗證與邊界

新增十項來源／圖像回歸：七種 Java/Bedrock 預設顯示對比、旋轉等價與錯誤比例排除、原生 item_visual 入口、圖示輪廓與透明邊界、滿空瓶區分、指南副本、原材質保存，以及精確 BP/RP 變更集合。

保留 A2.8.0 全部資料／資源回歸、54 個核心規則原指紋、共享分類六種排列、76 條指南／77 配方變體、39 烤串／150 模型、64 手持調料狀態、放置顯示、PBR、固定 Java 契約、Dash 及來源／編譯成品精確比較。1383 個其餘 runtime 檔案須保持與固定 A2.8.0 基線一致。

新圖示離線重建比較 RGBA 像素；不要求不同系統的 PNG 壓縮位元組一樣。真正打包的檔案仍逐位元組核對來源並提供 SHA256。

`minecraft_tested=false`、`bds_tested=false`、`client_visuals_tested=false`。這是針對已回報缺陷的程式／資源修正版，尚需玩家重新驗收第一／第三人稱畫面。建議在備份世界更新同一組煙火 BP/RP；Cookery 1.0.6 依賴不變，不新增相容包。
