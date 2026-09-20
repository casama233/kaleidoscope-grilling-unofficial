# 煙火 A1.16 Cookery 依賴沉浸動效驗收

這是**依賴 Kaleidoscope Cookery 1.0.6** 的動畫驗收包，不包含 Cookery 本體。請先安裝並在測試世界啟用 Cookery 1.0.6 的 BP/RP，再啟用本包。

A1.16 新增六種原作進食規則（ONE / TWO / THREE / THREE_ALT / THREE_RANDOM / FOUR）、主手／副手、第一／第三人稱玩家骨骼動畫、刷油與撒料的手持 attachable，以及拿起／收回過渡。THREE_RANDOM 每次開始只選一次 THREE 或 THREE_ALT，該結果同時控制動作和分口時間。

在創造測試世界召喚 `/summon kg_imm:rehearsal`。流程仍為點火→上串→刷油→翻面四次→撒料→取串→進食。刷油請拿 `kg_imm:oil_brush`，撒料拿 `kg_imm:seasoning_bottle`；進食請拿六個 `kg_imm:eat_*` 驗收串之一，可放主手或副手。

刷油核心仍為原作1秒、撒料核心0.5秒；各自在前後新增0.15秒拿起／收回，這兩段是基岩移植新增銜接。六種進食規則本身不加時。ONE和THREE會驅動第二隻手；只有副手／主手對側為空時才暫放驗收碎塊，絕不覆蓋玩家已有物品。

本包不扣食材、不恢復飢餓、不註冊正式配方。第一人稱右手基準來自固定版本的 Mojang Bedrock samples；左手為鏡像校準。Minecraft客戶端中的皮膚、左撇子設定、真正接觸位置與相機觀感仍需要實機驗收。
