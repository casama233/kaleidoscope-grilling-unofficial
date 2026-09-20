# A1.16.0 — Cookery 依賴、六種進食規則與玩家骨骼／相機綁定

A1.16 將 A1.15 的獨立動效驗收台改為**明確依賴 Kaleidoscope Cookery 1.0.6** 的測試包，並把原作六種進食規則、主／副手、第一／第三人稱玩家骨骼、手持 attachable、拿起／收回和中途恢復接到同一條沉浸流程。

這仍是動畫／互動驗收層，不是完整生存玩法；不扣食材、不回復飢餓、不註冊正式燒烤配方，也沒有把 Cookery 原包提交進本倉庫。

## Cookery 依賴

保留本包既有 UUID，只把版本升到 [0,1,16]。正式驗收包現在要求：

- Cookery BP：10f37ae2-9ccf-435f-b34b-0eec8191cd94，版本 [1,0,6]
- Cookery RP：c89dc8df-c3fc-4bc8-8bd0-527abba76681，版本 [1,0,6]

A1.15 的「可獨立執行」只保留為歷史測試結構；A1.16 的 BP/RP manifest 缺少上述任一依賴時，CI 會直接失敗。

## 六種進食規則

| Profile | 總長 | 原作咬點 |
|---|---:|---|
| ONE | 90 ticks | 1.16667s、3.08333s |
| TWO | 90 ticks | 0.95833s、4.00000s |
| THREE | 100 ticks | 0.95833s、2.33333s、3.54167s |
| THREE_ALT | 90 ticks | 0.95833s、2.16667s、3.50000s |
| THREE_RANDOM | 開始時選一次 THREE 或 THREE_ALT | 選中的分支同時控制總長、骨骼動畫、分口及音效 |
| FOUR | 90 ticks | 0.95833s、2.33333s、3.45833s、4.08333s |

THREE_RANDOM 不會每一口重新抽取，也不會出現「動作走 THREE、食物卻按 THREE_ALT 分口」。伺服器開始操作時只決定一次，之後整個動作使用同一 resolved profile。

## 玩家綁定

本輪生成 **16 條玩家動畫**：

- 五個 resolved 進食 profile × 主／副手：10
- 刷油 × 主／副手：2
- 撒料 × 主／副手：2
- 拿起／收回 reach × 主／副手：2

沒有覆寫 minecraft:player 的 client entity 或玩家模型。手持物件使用 attachable，根骨綁定：

q.item_slot_to_bone_name(context.item_slot)

因此主手沿 rightItem，副手沿 leftItem。第一人稱右手基準固定引用 Mojang Bedrock Samples 提交 46ba6ea985fb5a92d79a9419198f10dda14c199d 的原生 first-person empty-hand 姿態；左手目前以鏡像校準生成，真實「左撇子」客戶端設定仍要實機驗收。

ONE 與 THREE 使用原作雙手規則。對側手為空時，驗收程式才暫時放入來源衍生的咬塊；對側已有玩家物品時不覆蓋。中途取消或重新進世界時，以恢復令牌檢查原槽仍是不是 kg_imm:visual_*，只有仍是驗收 visual 才還原 selector，避免蓋掉玩家後來換進去的物品。

## 刷油、撒料與接觸

原作核心時間不壓縮：

- 刷油核心：1.00s，一次完整往返
- 撒料核心：0.50s，兩次抖動與倒瓶
- 基岩移植新增：前 0.15s 拿起＋後 0.15s 收回

所以可見總長分別為約 1.30s 和 0.80s。新增的 0.15s 銜接明確標為移植補間，不冒充原作時間。

為了讓原作 camera-space 軌跡落入爐面工作區，本驗收台要求操作時：

- 水平距離 0.72–1.32 格
- 朝向爐心的水平視線 dot > 0.90
- 垂直差 < 0.75 格

拿起後第 3 tick 才觸發刷油／撒料接觸聲。蹲下取消優先於 3 tick 防連點，因此剛開始動作也能立即收手。

**這些是座標與流程校準，不是已通過 Minecraft 像素級碰撞驗收。** 真實 FOV、玩家皮膚、手臂寬度、左撇子設定及第三人稱相機距離仍可能需要微調。

## 實際驗證

成功工作流程：
https://github.com/casama233/kaleidoscope-grilling-unofficial/actions/runs/35484643707

- 六種規則／流程：21 項通過
- 實際 A1.16 adapter 在模擬事件宿主中：15 項通過
- Cookery 1.0.6 依賴結構：通過
- 玩家動畫：16
- attachable 幾何：4
- profile selector 物品：6
- 官方 bridge. Dash v1.2.0：Windows 實際編譯成功，記錄 77 個檔案
- 真實 Dash 輸出逐檔比對：RP 48、BP 28，全部與生成來源一致
- .mcaddon 與 .brproject 均通過 ZIP 完整性檢查

輸出 SHA-256：

- Grilling_Immersion_Lab_A1.16.mcaddon：854af63a4b6de669592d1f23ba9d1b32e30b03372726904e2e7bcaf3f92dcb19
- Grilling_Immersion_Lab_A1.16.brproject：e28719233274f7fd1043eacf405778e7c4b8df9145cee8ac8520dcc0fdf9451a

## 怎樣測

1. 使用複製的創造測試世界。
2. 先安裝並啟用 **Kaleidoscope Cookery 1.0.6 BP/RP**。
3. 再匯入 A1.16 .mcaddon 並啟用其 BP/RP。
4. /summon kg_imm:rehearsal
5. 點火、上串後：
   - 刷油：主手或副手拿 kg_imm:oil_brush
   - 撒料：主手或副手拿 kg_imm:seasoning_bottle
   - 進食：拿 kg_imm:eat_one、eat_two、eat_three、eat_three_alt、eat_three_random 或 eat_four
6. 需要刷油／撒料時靠近並面向爐心。
7. 蹲下互動可立即取消。

## 尚未宣稱完成

- Minecraft 客戶端／BDS 真實運行
- 左撇子玩家設定
- 不同 FOV／皮膚手臂粗細下的最終接觸精度
- 正式背包交易、油量、調味料消耗、營養／效果結算
- 正式 Cookery 世界中的完整烤爐加工流程
- 玩家原生使用鍵直接進食，而不是驗收台觸發
- 完整自由組合串、餐盤、流體及剩餘粒子

A1.16 的核心成果是：六種原作規則和玩家動作不再只存在來源資料表，而是已生成到實際 Bedrock 玩家骨骼／item bone 動畫並通過構建和模擬事件驗收；Minecraft 實機仍是下一層。
