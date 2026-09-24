# A2.7.63 — Held Display Parity Batch 1

本批延續 A2.7.62 的 Big Vat corrective，開始處理全量 Render Audit 揭露的手持 display parity 債務。只改 Resource Pack 的 held rendering；不改玩法、配方、容量、交互、BlockEntity、持久化 key 或 UUID。

## 來源

A2.7.62 Render Audit 對 canonical Gameplay Core 掃描：

- 238 個 geometry
- 29 個 animation
- 4 個 render controller
- 23 個正式 block
- 43 個 attachable

當時結果：

- error 0
- high 119
- medium 0
- info 2

High 幾乎全部集中在 held rendering：39 個 fixed skewer 的 bound-root animation / Java display 未套、3 個 seasoning item 的 Java display 未套，以及 Advanced Rack 沒有 held attachable。

## 調料瓶

A2.7.33 已經把調料瓶從「動畫直接移動 bound root」修成安全的 hand-space shell，因此 A2.7.63 不重做 shell，也不把舊 root animation 接回去。

新結構：

```
root  (binding = q.item_slot_to_bone_name(context.item_slot))
└─ display
   └─ seasoning shell bones...
```

- `root` 只負責跟手；
- A2.7.33 已 bake 的 -6 hand-space shell 座標保留；
- Java first/third-person rotation / translation / scale 全放在 `display`。

Java `seasoning_bottles_1` display：

- first-person right/left
  - rotation `[-180, 60.25, -180]`
  - translation `[0, 5, 0]`
  - scale `[0.72, 0.72, 0.72]`
- third-person right/left
  - rotation `[29.5, 45, 0]`
  - translation `[0, 3, 2.75]`
  - scale `[0.5, 0.5, 0.5]`

套用到：

- `empty_seasoning_bottle`
- `pending_seasoning`
- `special_seasoning`

三個 attachable 共用 `geometry.kg_a2733.seasoning_bottle_hand` 與新的 A2.7.63 display animations。

## Advanced Rack

舊狀態：

- Java `advanced_rack_0..4` 有明確 display transform；
- canonical BP 的 `advanced_rack` item 有 block placer；
- canonical RP 沒有 `kaleidoscope_grilling:advanced_rack` attachable；
- 手持只能走 Bedrock 預設 item/block rendering。

A2.7.63 新增：

- `resource_pack/attachables/advanced_rack.attachable.json`
- `resource_pack/models/entity/a2763_advanced_rack_hand.geo.json`
- `resource_pack/animations/a2763_advanced_rack_hand.animation.json`
- `resource_pack/render_controllers/a2763_advanced_rack_hand.render_controllers.json`

hand geometry 從空架 `advanced_rack_0` 派生：

- x/z 保留已轉換為以 block center 為原點的座標；
- y 整體 -8 model units，使 0..16 Java block-space 置中到 hand-space；
- bound `root` 不做 transform；
- shell 在 child `display` 下。

Java 明確存在的 transform：

- third-person right/left
  - rotation `[75,45,0]`
  - translation `[0,2.5,0]`
  - scale `[0.375,0.375,0.375]`
- first-person right
  - rotation `[0,57,0]`
  - scale `[0.4,0.4,0.4]`

原 Java model **沒有** `firstperson_lefthand`。因此本批不自行鏡像／複製一套左手數值，也不宣稱左手 Java parity；左手第一人稱保留 Bedrock attachable 的未加 transform fallback，待實機確認。

## 防回歸

`tools/audit_grilling_render.py` 現在把兩組 corrective 升成 error-level contract：

- seasoning hand root 必須保持 item-slot binding；
- `display` 必須是 unbound child；
- shell bones 必須在 `display` 下；
- seasoning 四組 FP/TP transform 必須逐值等於 Java report；
- 三個 seasoning attachable 必須全部公開這四組 animation；
- Advanced Rack hand geometry / binding / display hierarchy 必須存在；
- Rack FP-right / TP-right / TP-left 必須逐值等於 Java report；
- pinned Java source 若未來新增 FP-left，audit 會報錯要求重新移植；
- 在 Java 尚未定義 FP-left 時，canonical attachable 不允許悄悄加入一個自稱 parity 的 `fp_left`。

## 尚未處理

A2.7.62 audit 的最大剩餘項仍是 fixed skewer：

- 39 個 skewer attachable 的 FP/TP animation 直接 transform bound root；
- 其中 37 個能直接對應到 Java display report，但仍使用 A2.7.25 通用 offset。

這一批不把 150 個 bite geometry 與 39 個 attachable 一次性大改。下一批應先把 skewer held hierarchy 收斂為 `bound root -> display -> bite geometry`，再接 Java display transform。

## 驗證邊界

Static Render Audit / JSON / Dash / compiled-output compare 可以證明：

- 引用存在；
- bone hierarchy 與 binding 正確；
- transform 數值與 pinned Java report 一致；
- canonical source 與 compiled pack 一致。

它們不能證明實際 Minecraft 第一人稱 FOV、左撇子、皮膚、GPU、Android、動畫 blending 或最終觀感。A2.7.63 仍需要實機截圖確認。
