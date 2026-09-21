# A2.7.10 — 生饅頭片 / Mantou Chopping

> Java 基線：Kaleidoscope Grilling 1.1.1 @ `9a1acdab27698457bec16c9362678e574895a28c`。  
> Cookery Bedrock：1.0.6，公開包 SHA-256 `c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351`。  
> 本批只補 `raw_mantou_slice` 與它的砧板入口，不混入作物、雞皮或魷魚鬚取得方式。

## Java 1.1.1 真實語義

鎖定 Java commit 的配方：

`kaleidoscope_grilling:chopping_board/raw_mantou_slice`

內容為：

- input: `kaleidoscope_cookery:mantou`
- cut_count: **4**
- model_id: `kaleidoscope_grilling:raw_mantou_slice`
- result: `kaleidoscope_grilling:raw_mantou_slice ×3`

`RAW_MANTOU_SLICE` 在 Java 註冊為普通 `ingredient("raw_mantou_slice")`：

- stack 64
- 非食物
- 無特殊 callback / effect

物品欄貼圖直接鎖定 Java 1.1.1 原圖，Git blob SHA-1：

`c89c916e0611d7de9d821e122b2d88c099809cbf`

## Bedrock 實作

這條輸入不需要像 A2.7.9 牛肉那樣覆寫 Cookery built-in。

A2.7.10 使用 Cookery Extension Recipe API v1：

- 只在 `api=1`
- 且 `capabilities` 包含 `chopping_board`

時註冊：

`kaleidoscope_cookery:mantou -> raw_mantou_slice ×3 / 4 cuts`

CI 會下載精確 SHA-256 的 Cookery 1.0.6 公開包，確認：

1. direct station 仍採 `BOARD_RECIPES[id] || getExtensionBoardRecipe(id)`；
2. station recipe data 沒有 `kaleidoscope_cookery:mantou` built-in key。

如果未來 Cookery 新增內建 mantou 砧板 recipe，本批 contract gate 會失敗，而不是繼續宣稱公開 API parity。

## 不重複 API ping

A2.7.8 已在模組載入完成後透過 `system.run` 發送一次 `api_ping`。

A2.7.10 只新增 `api_ready` listener，不再自行 ping。由於 ES module imports 會先完成，而 A2.7.8 的 ping 要到排程 callback 才發送，因此 A2.7.10 listener 會及時收到同一個 ready event，同時避免兩次 ping 觸發重複 recipe registration。

## 下游鏈恢復

A2.4 已經存在固定串配方：

`raw_mantou_slice + raw_mantou_slice + raw_mantou_slice -> raw_bun_slice_skewer`

此前固定串本身存在，但 Grilling 沒有正常取得 `raw_mantou_slice` 的加工入口。

A2.7.10 補完後，當 Cookery 的 mantou 可取得時：

**mantou → 砧板切片 → 三片生饅頭片 → 生饅頭片串**

這條既有固定串鏈正式變成可達。

## 仍未冒充完成的視覺差異

Java 為這條配方提供 `kaleidoscope_grilling:raw_mantou_slice` 的分階段 chopping-board model。

Cookery Bedrock 公開 extension recipe 對外部 ingredient 目前走 generic foreign-item board display fallback；本批沒有把這個 fallback 標成 Java 1:1 模型。

因此：

- input / output / count / cut count：結構 parity
- item icon：Java 原圖
- Java staged chopping-board model：**未完成 1:1**
- Minecraft 客戶端實際渲染：**未驗收**

## 下一批候選

完成這一小批後，仍可沿同樣節奏拆：

- `chicken_skin` / `chicken_wing` 的刀具擊殺掉落；
- `squid_tentacle` 的刀具擊殺掉落；
- `houttuynia -> minced_houttuynia` 砧板鏈；
- 再進入 canola / onion / sweet potato / houttuynia 作物與 pepper tree 世界生成。

全局較大的剩餘項仍包括 Advanced Rack、指南動態頁／進度、餐盤逐串顯示、作物與世界生成，以及 Minecraft/BDS/多人實機驗收。

仍保持：

- `minecraft_tested=false`
- `bds_tested=false`
- `exact_java_staged_board_visual=false`
