# A2.7.8 — 基礎切配 I：胡蘿蔔粒 + 馬鈴薯片

> Java 基線：Kaleidoscope Grilling 1.1.1 @ `9a1acdab27698457bec16c9362678e574895a28c`。  
> Cookery Bedrock：1.0.6，公開包 SHA-256 `c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351`。  
> 本批只做兩條**不存在 Cookery built-in 衝突**的 Chopping Board 配方。

## 已完成

新增普通 64 堆疊物品：

- `kaleidoscope_grilling:carrot_dice`
- `kaleidoscope_grilling:potato_slice`

兩張貼圖直接取自鎖定 Java commit，Git blob SHA-1 分別為：

- carrot_dice: `c5359f186611411d51f1fe55077357d2c16efa61`
- potato_slice: `9562676753ad5e32ea0e1345236e314ad4767b85`

Java item 註冊均為普通 `new Item(new Item.Properties())`，沒有食物、效果或特殊 callback，因此 Bedrock 不添加額外 gameplay component。

## Java 配方逐條對齊

### Carrot Dice

Java：

- input: `minecraft:carrot`
- cuts: **4**
- result: `kaleidoscope_grilling:carrot_dice ×3`
- model_id: `kaleidoscope_grilling:carrot_dice`

Bedrock 透過 Cookery Extension Recipe API v1 註冊完全相同的 input / cuts / result / count。

### Potato Slice

Java：

- input: `minecraft:potato`
- cuts: **4**
- result: `kaleidoscope_grilling:potato_slice ×3`
- model_id: `kaleidoscope_grilling:potato_slice`

Bedrock 同樣透過公開 API 註冊。

只有 Cookery `api_ready` 明確宣告 `chopping_board` capability 時才註冊。

## 為什麼 Beef Chunks 沒混進這一批

Java Grilling 的：

`data/kaleidoscope_cookery/recipe/chopping_board/raw_cow_offal.json`

實際把 Cookery 原來的牛肉砧板配方改成：

`minecraft:beef -> kaleidoscope_grilling:beef_chunks ×2, 4 cuts`

本輪重新檢查**精確 Cookery Bedrock 1.0.6 公開包**後確認：

`BOARD_RECIPES["minecraft:beef"] = { result:"kaleidoscope_cookery:raw_cow_offal", count:2, cuts:4 }`

而 directStation 查找順序是：

`BOARD_RECIPES[id] || getExtensionBoardRecipe(id)`

因此普通 Extension API 註冊無法覆蓋 beef built-in。若現在把 beef recipe 一起送進 API，註冊本身會成功，但實際遊戲永遠先命中 Cookery built-in，屬於「假完成」。

所以：

- `beef_chunks` item/recipe **本批沒有冒充完成**
- 單獨留給 A2.7.9 做 built-in override adapter

## 顯示差異

Java 兩條配方都有自己的 `model_id`。Cookery Bedrock 公開 recipe API 對未提供額外 board display/native-model 資產的 extension input 使用 generic item-display fallback。

因此 A2.7.8：

- 配方結果／刀數／產量：已對齊
- 物品欄貼圖：Java 原圖
- 砧板加工中的 staged 3D model：**尚未宣稱與 Java 1:1**

考慮到之前使用者已實機抓到 renderer 問題，這項差異明確留在報告中，不用 generic fallback 冒充 Java model parity。

## 下一步

A2.7.9 優先單獨處理：

- `beef_chunks`
- Cookery built-in beef board override
- 同時選擇不修改 Cookery 私有腳本的最小可維護方案

之後再切：

- chicken_skin
- raw_mantou_slice
- squid_tentacle
- 其餘加工物

仍保持：

- `minecraft_tested=false`
- `bds_tested=false`
