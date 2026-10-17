# A2.8.4：進食錯位修正

## 問題與證據

使用者影片顯示第三人稱進食時，手臂脫離肩膀，串物懸空。
舊 `development/player_binding/build.py` 把 Java 第一人稱專用曲線轉成
`rightarm/leftarm` 位移，再寫入 `rightitem/leftitem` 的額外位移／旋轉。
例如 `eat_one.main` 第一幀的第三人稱手臂 Y 位移為 -10.597391。
這會移走肩關節，並在既有 attachable 手持變換上再施加物品變換。

Java 上游 `ItemInHandSkewerEatingMixin` 攔截的是第一人稱
`ItemInHandRenderer.renderArmWithItem`，並自行建立相機空間的 PoseStack。
它並非第三人稱全身姿勢，不能直接套到基岩版玩家骨架。
參考版本為 Java 1.1.1、commit `9a1acdab27698457bec16c9362678e574895a28c`。

## 本次修正

- 停止從腳本播放 `animation.kg_imm.player.eat_*`；42 種串類食品由既有
  `minecraft:use_animation = eat` 接管手臂。歷史曲線仍保留供後續重製研究，正式食品流程不再呼叫。
- 移除中途停止與 THREE_ALT 提前結算後的全身零姿勢重設，避免干擾原生姿勢及下一個手持物品。
- 玩家離線時清理進食狀態表。
- 39 組分口模型、分口時間、進食音效、營養及效果结算邏輯保留。
- 延續 A2.8.3 的提示、物品圖示與模型修正；本次未增加常駐文字提示。

原生 use animation 的語義參考
[Microsoft 官方文件](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/itemreference/examples/itemcomponents/minecraft_use_animation?view=minecraft-bedrock-stable)。

## 驗證及界線

`python development/gameplay_core/verify_current.py`：42 種食物原生進食元件、39 組分口
attachable、腳本不存在舊進食動畫呼叫、停止／提前結算不覆寫骨架，以及前版資源和核心玩法回歸。

這是解除錯誤骨架覆寫的修正，**尚非 Java 特殊進食動作的完整還原**。
原生連續咀嚼動作不會逐幀吻合 Java 分口聲音與特殊取食手勢。
Java helper-hand 取下一塊食物的動作仍待正式重製。
靜態檢查及 BDS 載入無法證明客戶端手持位置正確。

## 客戶端驗收

更新資源包後，以影片中的馬鈴薯片串、雞皮串和牛肉串驗證：

1. 第一人稱及第三人稱：站立、行走、蹲下、視角抬低；手臂不得離肩，食物須跟隨手部。
2. 持續食用、提早鬆開、切換物品、連續吃下一串；不得殘留姿勢或影響下一件物品。
3. 分口減少、聲音、完成／中止結算；另以另一名玩家觀察同步。
4. 普通及纖細手臂皮膚、主副手；自訂骨架皮膚需另行確認。

使用者提供的兩份改善手冊採納了「區分視角座標」、「避免多層變換疊加」、
「以實際載入版本和玩家畫面验收」原則；其中將煙火理解為 fireworks 的部分不適用本模組。
