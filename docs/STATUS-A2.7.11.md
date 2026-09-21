# A2.7.11 — 生饅頭片 / Mantou Chopping

> Java 基線：Kaleidoscope Grilling 1.1.1 @ `9a1acdab27698457bec16c9362678e574895a28c`。  
> Cookery Bedrock：1.0.6，公開包 SHA-256 `c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351`。  
> 基線已包含 A2.7.10 Chicken Acquisition；本批只補 `raw_mantou_slice` 與它的砧板入口。

## Java 1.1.1 真實語義

鎖定 Java commit 的配方：

`kaleidoscope_grilling:chopping_board/raw_mantou_slice`

- input: `kaleidoscope_cookery:mantou`
- cut_count: **4**
- model_id: `kaleidoscope_grilling:raw_mantou_slice`
- result: `kaleidoscope_grilling:raw_mantou_slice ×3`

`RAW_MANTOU_SLICE` 由 Java 的普通 `ingredient("raw_mantou_slice")` 註冊：

- stack 64
- 非食物
- 無特殊 callback / effect

物品貼圖直接鎖定 Java 1.1.1 原圖，Git blob SHA-1：

`c89c916e0611d7de9d821e122b2d88c099809cbf`

## Bedrock 實作

A2.7.11 使用 Cookery Extension Recipe API v1。只有：

- `api=1`
- `capabilities` 包含 `chopping_board`

時才註冊：

`kaleidoscope_cookery:mantou -> raw_mantou_slice ×3 / 4 cuts`

CI 下載精確 SHA-256 的 Cookery 1.0.6 公開包，驗證 direct station 仍採：

`BOARD_RECIPES[id] || getExtensionBoardRecipe(id)`

並確認 station recipe data 沒有 `kaleidoscope_cookery:mantou` built-in key。未來若 Cookery 新增同 input 的 built-in recipe，contract gate 直接失敗，不把被遮蔽的 extension recipe 冒充成完成。

## 不重複 API ping

A2.7.8 已在所有 ES module imports 完成後用 `system.run` 發送一次 `api_ping`。

A2.7.11 只新增 `api_ready` listener，不自行再 ping，因此：

- listener 在既有 ping 發送前已完成註冊；
- 不會因兩次 ping 造成兩輪 extension recipe registration。

## A2.7.10 並行成果保留

主線在本批開發途中已先發布 A2.7.10 Chicken Acquisition。

因此 A2.7.11 明確：

- 以 manifest `[2,7,10]` 為唯一可接受輸入基線；
- 在 A2.7.10 chicken runtime import 後追加 mantou runtime；
- CI 回歸執行 A2.7.10 chicken core/runtime tests；
- A2.7.10 Cookery chicken-board/knife contract 與 A2.7.11 mantou contract 都必須各自通過。

不覆寫、不降級雞皮/雞翅取得鏈。

## 下游鏈恢復

A2.4 fixed-skewer table 已存在：

`raw_mantou_slice + raw_mantou_slice + raw_mantou_slice -> raw_bun_slice_skewer`

此前固定串配方存在，但 Grilling 沒有正常取得 `raw_mantou_slice` 的加工入口。A2.7.11 後，當 Cookery 的 mantou 可取得時：

**mantou → 砧板切片 → 三片生饅頭片 → 生饅頭片串**

正式可達。

## 仍未冒充完成的視覺差異

Java 指定 `kaleidoscope_grilling:raw_mantou_slice` 作為 chopping-board model。

Cookery Bedrock 公開 extension recipe 對外部 ingredient 仍走 generic foreign-item board display fallback；本批沒有把它宣稱為 Java staged model 1:1。

所以：

- input / output / count / cuts：已做結構 parity
- item icon：Java 原圖
- staged chopping-board model：**未 1:1**
- Minecraft 客戶端實際渲染：**未驗收**

## 後續差異

下一批較適合繼續拆：

- `squid_tentacle`：Java 菜刀擊殺 squid，50% 掉 2–3 + Looting bonus；
- `houttuynia -> minced_houttuynia`：4 刀 ×1，但上游魚腥草取得仍需一起規劃；
- 之後進入 canola / onion / sweet potato / houttuynia 四種作物與 pepper tree 世界生成。

較大的剩餘系統仍有：

- Advanced Rack（BlockEntity / 分格 / shortcut / GUI / 工具與調料分類）
- 21 個 Java advancements / guide 動態進度
- skewer plate 逐串顯示
- extension chopping recipes 的 Java staged board model
- Minecraft / BDS / 多人 / reload 實機驗收

仍保持：

- `minecraft_tested=false`
- `bds_tested=false`
- `exact_java_staged_board_visual=false`
