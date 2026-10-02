# A2.8.43 串串第一人稱顯示候選修復

使用者提供的真人截圖顯示：快捷欄已選中烤土豆片串，但第一人稱沒有正常的手持串串。現場 2.8.40 與 main 2.8.42 的土豆串 attachable、手持動畫、stage0 geometry 和 bite render controller 逐檔雜湊相同；升級至 2.8.42 本身不會解決此問題。

此前第一人稱換算使用 Blockbench 的展示手柄 `[-20,21,0]` 與預覽相機 `[0,19,-40]`，可在編輯器內得到可見圖像。這套座標不能直接當作玩家骨架的第一人稱綁定座標。

本版以 Mojang v1.26.50.4 的 `player_armor.json` 與 `player_firstperson.animation.json` 中公開的右臂 pivot、empty_hand 位移／旋轉、rightItem 相對偏移推導串串綁定基準。左手採鏡像基準。保留 Java 串串的旋轉／平移／比例輸入、原模型、UV、材質、所有 bite geometry、第三人稱動畫及進食動畫；沒有覆蓋玩家資源定義，也沒有修改第三方包。瓶子和串架的舊編輯器換算未納入這次串串修復。

獨立回歸從釘選的來源 fixture 重建玩家骨架，讀取實際 runtime 動畫，不呼叫姿勢生成器的校準函式。舊土豆串姿勢在此投影中沒有可見頂點；修正版檢查所有 150 個串串 geometry × 兩手，分別確認竹籤與尚未吃完的食物有可見頂點，並要求第三人稱動畫與舊版完全相同。

投影採頭部中心 `[0,24,0]`、固定視野範圍；這是座標回歸模型，**不是 Minecraft 渲染器模擬**。客戶端眼睛偏移、FOV、皮膚、走路／切換／進食時的原生骨架疊加及多包載入仍需真人確認。因此這份候選不能僅憑來源測試、Blockbench 或 BDS 宣稱已修好實際畫面。

真人驗收：在完整家族候選的獨立世界中，先拿烤土豆片串，再切換生牛肉串、不同進食階段、主副手及第三人稱；檢查站立、走動、切換、進食和結束後是否可見、是否穿過畫面／手臂。應記錄客戶端版本、FOV、皮膚、候選收據 SHA256 與截圖。只有這一份候選的實際驗收能解除其客戶端部署門檻。

來源： [Mojang 玩家骨架](https://github.com/Mojang/bedrock-samples/blob/v1.26.50.4/resource_pack/models/entity/player_armor.json)、[Mojang 第一人稱動畫](https://github.com/Mojang/bedrock-samples/blob/v1.26.50.4/resource_pack/animations/player_firstperson.animation.json)。來源 SHA256 與擷取欄位保存於 `development/gameplay_core/fixtures/native-fp-frame-1.26.50.4.json`。
