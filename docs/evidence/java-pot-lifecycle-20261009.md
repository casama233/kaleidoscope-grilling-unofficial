# G121：三道 Grilling 炒菜的 Java exact／flex 生命周期

來源基準、兩個 Java 分支的固定 revision、六條原配方與品質規格見
[cookery-flex-pot-lifecycle-20261009.md](cookery-flex-pot-lifecycle-20261009.md)。
本頁記錄 G121 的實作範圍；它不把程式檢查、配方註冊或宿主載入當成玩家／客戶端驗收。

## 固定來源與實際入口

- Grilling 1.1.1：`9a1acdab27698457bec16c9362678e574895a28c`。
- Cookery Forge 1.6.0：`2f4e386ce23f49a385ddf003c67fc6415c55417a`。
- Cookery NeoForge 1.6.0：`4d39e36cfa749939ba5f9d6d3b715ef9a984cb9c`。
- Cookery Bedrock 1.6.0 的原始 mcaddon SHA256：
  `da12fe6d39d7514aff1de3c963d69899324d771be5ca0fc3da1ccb759c7ad458`。
  本次重新取得原包並核對；原 BP 的
  `items/placeable_food/dark_cuisine.json` 確實註冊
  `kaleidoscope_cookery:dark_cuisine`，原生 max stack 16、nutrition 2、saturation modifier 0，
  食用後交還碗。沒有自行發明不存在的宿主結果 ID。

只有既有 1.6.0 宿主的 `potInteract`、`potTick` 與 `spillDirectStationContents`
函式開頭新增短掛鉤，實作在 Grilling 自有 `host_api/pot_api_core.js`、`pot_api_host.js`。
沒有覆蓋、公開完整第三方原腳本，也沒有新增輪詢器、站點副本或玩家測試入口。

宿主擴充為 family API 0.2.8，宣告實際能力 `grilling_pot_exact_flex_v1`；
它表示本頁的三菜適配，不是任意 Java datapack 的通用 flex 配方 API。
新炒鍋入口要先在宿主 `getWokRecipes()` 的實際已接受列表中看到三條 exact 配方，
逐一核對 ID、result、count、time、carrier 與 ingredient slots。
原 1.6.0 `normalizeWok` 固定輸出 `stirs:1`，並丟棄送入的 stirs；
入口也核對這個原宿主值。三次翻炒由新增的版本化 Java 階段依來源規格保存，
沒有把原宿主的單次翻炒欄位假稱為已保存三次。
沒有以複製在包內的表格跳過宿主註冊或失敗的握手。
存檔中的新備料階段在重新註冊尚不可用時保留資料、暫停；已保存的烹飪與完成結果可以排空。

## 配方與階段

| 選擇 | 材料 | 數量與時序 |
| --- | --- | --- |
| 魚腥草炒肉 exact | 魚腥草 ×3、生豬肉 ×3 | 1 份、1 碗、200 tick、3 翻 |
| 青椒魷魚 exact | 青椒 ×2、魷魚須 ×2、洋蔥 ×1 | 1 份、1 碗、200 tick、3 翻 |
| 紅燒雞翅 exact | 雞翅 ×3、糖 ×3 | 1 份、1 碗、200 tick、3 翻 |
| 三菜 flex | 分別保留 2／3／2 個原宣告 ingredient slots；材料比例可變 | 結果固定 1 份；不按重複組數乘產量 |
| 無配方的自有流程 | 迷之炒菜 | 200 tick；不要求翻炒 |

完整 exact 配方優先於 flex；宿主已有的其他完整 exact 配方也先於本模組 flex。
Matcher 把輸入補至九槽，空 ingredient 只匹配空槽，執行一對一完整配對。
Flex 先按實際 Item ID 去重，再補空槽。兩個不同 Item 即使同屬一個 tag，仍是兩個輸入種類；
沒有多餘材料容忍或依 tag 任意合併。

本版只列原包已確認的 Grilling tag 成員：
雞翅、魚腥草、魷魚須、洋蔥各自的本模組物品。
Forge 的 `forge:crops/onion` 與 NeoForge 的 `c:crops/onion` 不被虛構成通用 Bedrock tag 橋。

| 保存階段 | 進入／轉移 |
| --- | --- |
| preparing | 新倒油開始 1200 個有熱源 tick；已有材料仍倒數，增減材料不重設 |
| cooking | 第一鏟開始 200 tick，同一次扣除第 1 次翻炒；普通材料鎖定；後兩鏟各再扣 1 |
| cooking 自動開始 | 備料耗盡且非空時開始 200 tick，還欠 3 翻；空鍋則清空 |
| finished | 200 tick 到期；少任何一翻改成迷之炒菜，保留 800 tick 取出窗口 |
| burnt | 完成窗口耗盡後再保留 400 tick；此時用碗取出黑暗料理 |
| charcoal | 400 tick 耗盡，1–3 炭的本次結果先寫入並讀回，再經既有單次收據掉落與清空 |

計時只按實際載入且有熱源的 block tick 前進，不推算卸載時間。
辣椒油的 12000／24000 tick 是食物煙火气期限；它不再延長新鍋的 1200 tick 備料時間。
新狀態整段保留油的邏輯所有權；完成／燒焦隱藏油面，清空時才清除邏輯油。

普通材料鎖不攔截既有特殊調味瓶的 before-event 路徑。
有熱源時空手取回材料造成原規則的 1 點火傷害。
成品缺少碗且沒有持鏟時同樣嘗試 1 點火傷害；持鏟則保留翻炒動作與耐久判斷。
普通鍋鏟先作 25% 的耐久支出判斷，再使用原生 `getDamageChance(unbreaking)`；
實際 clone 的耐久與手部讀回屬明列的 Bedrock 適配，沒有宣稱等同 Java 的所有原生附魔／工具事件。

## 保存、成本與單次交付

宿主原 `kc_station:<dimension>:<position>` JSON 保留 `items` 與
`grillingOutputEpoch`，並增加版本化 `grillingPot`：
`version`、`epoch`、`revision`、`phase`、`ticksRemaining`、
`stirsRemaining`，烹飪後另保存 `recipeKind`、原 Java `recipeId`、固定 `output` 及可選 `quality`。
新 schema、越界數字、品質缺失、不同 epoch、成品前後像衝突不被當成空鍋。

輸入與普通油消耗先記錄站點操作 journal
`senluo:java_pot_operation:<dimension>:<position>`，
綁定實際站點前像、後像、來源 owner、手部前後像。
journal 必須寫入並讀回，才進行扣除；接著驗證手部與完整站點保存。
非 terminal journal 會擋住新流程、舊宿主交接與拆除。

補償必須先確定站點已恢復前像，才可以退還成本。
站點仍可能持有已投入的材料／油時保留已扣成本並隔離。
手部必須確實進入本次寫入，且仍是本次擁有的後像，才能補償；
失敗的前置所有權檢查不會把恰好等於預期後像的他人物品當成自己的扣除。
站點也記錄真正進入 writer 的邊界；未嘗試保存時不會撤回恰好相同的其他新狀態。
原 `commitSharedStationOil` 同步修正此順序，並要求宿主提供不吞錯的原始 JSON 讀回。
共享油交易以此次 debit 自己保留的原生 before／after clone 核對成本，
不把稍後重新讀到的物品提升成此次交易擁有的後像；這些 clone 不寫入公開收據。
油退款另需原生 stackability 證明所有權；不可堆疊或不可讀的原生身分保留成本並隔離。

新備料只接受能以原生 `isStackableWith` 證明等於同 ID 普通 prototype 的可堆疊材料。
具名稱、lore 或其他不在此保存模型中的自訂資料不先吞掉再重建；
它們仍在原手中。這是有限適配，沒有聲稱任意 ItemStack／NBT 的無損持久化。
帶油鍋鏟變換 ID 時保存已暴露的 metadata、耐久及附魔並讀回；不可見原生資料仍不列入保真證據。

取回普通材料與拆鍋使用同一 `input:<epoch>:<revision>:<slot>` 所有權鍵，
且保存 journal 先於掉落。未知或部分交付保留原站點資料／journal，不再由宿主無條件清空。
這些普通材料走 `pot_input` 收據，保留普通物品，不套食物熱度或調味。
已具備新能力的宿主由 v2 收據識別真正料理，Grilling 不再把單純背包增加猜成成品，
避免取回原料時加上熱度、調味並錯清鍋內調味。

成品取出／拆鍋／黑暗料理／最終炭沿用 G120 的 epoch、prepared 交付讀回、carrier 成本、
拆除 fence、未知結果保留與撤回確認。
成品不能以不同階段更換 epoch 重新領取；完成轉燒焦、燒焦轉炭前先檢查是否已有交付。
炭數量在交付前保存，交付後清空失敗只能重試相同收據，不能重新抽數量。
補存 burn origin 的回收路徑，以 helper 已確認且回寫至同一資料物件的完整後像清空，
不使用較舊前像，也不盲目接納站點上其他較新狀態。
只有已完整 `rolled_back`、settlement version 1 的零交付原菜收據，
才能在同站點、同 epoch、同數量與已保存的原菜／原品質相符時重綁成黑暗料理。
prepared、committed、quarantined 不可利用換菜名繞過收據；拆除 fence 仍封閉整個 epoch。

## 品質與結果身分

Exact 成功不加 flex 品質。Flex 以原 `flex_pot/<菜名>` ID、
已讀的 `World.seed` 字串、宣告順序的 alternatives 與固定九槽輸入調用品質核心。
未知 seed／演算失敗保留材料與階段，不用 0、時鐘或 `Math.random()` 補品質。

保存的 `quality` 是 0–3；料理、JSON 往返與成品交付都保留它。
料理 API 的 `requestedItemId` 綁定配方的基本 ID，
實際 inventory／entity 的 output fingerprint 與 target ID 則是品質代理實物。
舊收據沒有新欄位時仍按原 output ID 辨識，不重寫舊收據、不重新消耗碗。
取出、拆除補發與衝突檢查使用相同基本／實物映射。
沒有品質欄位的其他原宿主料理保留原 ID。送入 API 的 requested ID 必須是基本 ID；
品質別名、其原始公開 lore、收據 metadata 及保存中的 immutable quality 必須一致。
拆除 intent 的品質不得覆蓋保存中的另一個品質，外部 nativeStack 的不一致 payload 也不自動修補。
品質的公開 payload、原生食物數值、保存與食用入口由同版品質修復承接；
它不隨「新熱度與調味」配置停用而消失。

Java 的燒焦取出新建黑暗料理；takeout mixin 更新的是原料理。
因此新燒焦階段的黑暗料理不繼承品質、熱度或調味，最終木炭也沒有食物 metadata。

## 明列保留與未驗收範圍

1. 舊 active／finished／burnt 宿主資料原樣排空，不猜測其已消耗的備料時間，
   不补 1200、不丟原材料、不改舊完成數量。
2. 未註冊的 Grilling 配方、原作者／外部油容器保留原宿主路徑。
   已註冊且新開始的普通倒油會先採共同的 Java 備料窗口；
   非三菜材料在扣除前交還宿主，選中其他作者配方則保存
   `grillingLegacyPot` 的原因、epoch、剩餘備料時間，再由原宿主決定數量與後續料理。
   因此不能把本次修復稱作所有 Cookery 配方均已改成 Java 生命周期。
3. 現有跨包調味 bridge 的舊 station metadata 會在下次新油／明確調味操作時重設，
   並非本次新增了可跨包原子清空所有 metadata 的交易。鍋的實際版本化內容立即按確認結果清空。
4. 所有權／schema 不明時採保留與隔離；未提供把未知 native 物品自動重建或人工核准為成功的後門。
5. 原宿主顯示、音效與鍋鏟動畫仍是有限適配。新 phase 與成品數值的 source check，
   不能證明 Java 粒子／動畫／模型／品質提示已在客戶端一比一呈現。
6. 本次本地執行純配方／保存狀態回歸及程式語法、原包八個掛鉤 hash 邊界檢查。
   主控於整合後另外各執行一次既有純儲存 harness 中的零交付原菜→黑暗料理及站點回復失敗保留油成本案例，兩者通過。
   未執行新的或既有的本地模擬玩家交互測試、BDS 玩家流程或 LIVE 佈署。
   實際滿包、重啟、不同玩家、拆除取消、手部變更、烹調時序與渲染仍需同候選原生驗收；
   `client=false`、`production_ready=false` 維持。
