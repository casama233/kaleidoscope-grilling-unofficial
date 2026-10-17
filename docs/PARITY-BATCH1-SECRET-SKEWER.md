# Grilling parity batch 1 — 秘製串煙燻與食材行為相容層

基準：

- Bedrock：`main@7ef78bb360ac6a34664a15deef2c2aff5cc3d719`
- Java 1.1.1：`breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c`

## 這批修什麼

Java `SkeweringHandler.ensureCookedIngredientStacks` 會對秘製串中的每個食材查
`RecipeType.SMOKING`；`SecretSkewerItem.finishFoodAndEffect` 則會真正執行每個食材的
`finishUsingItem`，因此第三方煙燻配方、食物效果和容器返還天然可參與。

Bedrock stable Script API 沒有跨 Behavior Pack 的 RecipeManager/recipe enumeration，
所以不能誠實地聲稱能在 runtime 自動讀出任意第三方配方。這批把原先散落在
`main.js` 的白名單改成公開、可擴展的相容契約：

1. `secret_compat_core.js`
   - 內建原版 Minecraft 的 9 個 smoker 轉換。
   - 內建 Grilling 1.1.1 自己的 chicken wing / sweet potato smoker 轉換。
   - 同時支援 item ID 與 item tag 規則。
   - 食材完成使用行為可宣告 native/persistent effects、機率、容器返還、
     honey-style 解毒、chorus-style teleport 與 ordinary-skewer 行為。
2. `secret_compat_runtime.js`
   - `kaleidoscope_grilling:register_secret_smoking`
   - `kaleidoscope_grilling:register_secret_food_behavior`
   - `kaleidoscope_grilling:register_secret_compat`
   - 每個秘製串食材結算後發出
     `kaleidoscope_grilling:secret_ingredient_consumed`，讓第三方腳本執行無法用
     宣告資料表達的自訂副作用。
3. `main.js`
   - 移除 `VANILLA_SMOKED` 硬編碼。
   - 穿串快照保留 item tags，供 tag-based smoking/behavior 規則使用。
   - 容器返還可攜帶 count/name/lore/primitive dynamic properties。

## 第三方 Add-on 接法

另一個 Script API Add-on 可在世界啟動時呼叫：

```js
system.sendScriptEvent(
  'kaleidoscope_grilling:register_secret_smoking',
  JSON.stringify({input:'example:raw_food',output:'example:smoked_food'})
);

system.sendScriptEvent(
  'kaleidoscope_grilling:register_secret_food_behavior',
  JSON.stringify({
    input:'example:smoked_food',
    behavior:{
      effects:[{effect:'speed',ticks:200,amplifier:0}],
      remainder:{id:'minecraft:bowl'}
    }
  })
);
```

也可用 `tag` 取代 `input`。需要任意自訂腳本行為時，第三方監聽
`kaleidoscope_grilling:secret_ingredient_consumed`，payload 包含
`playerId`、`playerName`、`itemId`。

註冊是 runtime contract；第三方 pack 應在每次 script runtime 啟動時重新送出。
不把這個限制偽裝成 Java RecipeManager 自動發現。

## 驗證邊界

新增純 Node regression：

- Java 1.1.1 內建 smoking mapping。
- item/tag 規則優先順序與第三方註冊。
- merge/replace 食材行為。
- remainder、機率效果和 bundle 註冊。
- reset 後不污染既有 vanilla 行為。

`verify_a287.py` 另外檢查 canonical `main.js` 已不再包含 `VANILLA_SMOKED`，
且 runtime 確實註冊三個輸入事件和一個消耗事件。

這批**沒有**宣稱 Bedrock 能自動枚舉其他 Behavior Pack 的配方；未知第三方仍需透過
上述公開 contract 註冊。下一批才處理通用熱食合併與 Cookery 非玩家/自動化產出。
