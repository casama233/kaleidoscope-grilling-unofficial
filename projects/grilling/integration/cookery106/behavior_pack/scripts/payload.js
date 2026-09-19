// Generated from pinned source references; no gameplay registration.
export const GUIDE_PAYLOAD = {
  "api": 1,
  "id": "kg_a1:grilling",
  "version": "0.1.12",
  "order": 300,
  "icon": "textures/ui/kg_grilling/grill_legged_lit",
  "titleKey": "title",
  "introKey": "intro",
  "allKey": "all",
  "selectKey": "select",
  "backKey": "back",
  "languageNoteKey": "language_note",
  "showAll": false,
  "showIds": false,
  "showKinds": false,
  "showCategoryOnEntry": false,
  "categories": [
    {
      "id": "start",
      "labelKey": "start",
      "fallback": "Start / scope",
      "icon": "textures/ui/kg_grilling/grill_legged_lit"
    },
    {
      "id": "equipment",
      "labelKey": "equipment",
      "fallback": "Equipment",
      "icon": "textures/ui/kg_grilling/grill_legged_lit"
    },
    {
      "id": "crops",
      "labelKey": "crops",
      "fallback": "Crops",
      "icon": "textures/ui/kg_grilling/grill_legged_lit"
    },
    {
      "id": "recipes",
      "labelKey": "recipes",
      "fallback": "Skewer recipes (source reference)",
      "icon": "textures/ui/kg_grilling/grill_legged_lit"
    },
    {
      "id": "seasonings",
      "labelKey": "seasonings",
      "fallback": "Seasoning references",
      "icon": "textures/ui/kg_grilling/grill_legged_lit"
    },
    {
      "id": "saved",
      "labelKey": "saved",
      "fallback": "My recipes (planned)",
      "icon": "textures/ui/kg_grilling/grill_legged_lit"
    }
  ],
  "entries": [
    {
      "id": "kg_a1:guide_start",
      "category": "start",
      "icon": "textures/ui/kg_grilling/grill_legged_lit",
      "kinds": [],
      "mechanics": [
        "這是素材與指南接入測試，不是完整可玩移植。 / Assets and guide integration preview; not a playable port.",
        "沿用森羅物語原指南，只加入一個煙火入口；沒有額外指南書。 / One extension in the existing Cookery guide; no extra book.",
        "所有配方保留Java來源順序；實際基岩版合成與效果尚未接入。 / Recipes are ordered Java-source references, not registered Bedrock recipes.",
        "書中的返回與取消行為由Cookery管理。 / Back and cancel behaviour belongs to Cookery."
      ]
    },
    {
      "id": "kg_a1:guide_grill",
      "category": "equipment",
      "icon": "textures/ui/kg_grilling/grill_legged_lit",
      "kinds": [],
      "mechanics": [
        "四種爐體已有靜態素材。刷油、翻面與調味仍待玩法階段接入；圖中的紅炭不是自發光驗收。",
        "Static model reference only. Placement, interaction, lighting and processing are not yet implemented."
      ]
    },
    {
      "id": "kg_a1:guide_rack",
      "category": "equipment",
      "icon": "textures/ui/kg_grilling/advanced_rack_4",
      "kinds": [],
      "mechanics": [
        "本批補上調料檔位 0–4。工具掛載、碰撞、操作及粒子仍未接入。",
        "Static model reference only. Placement, interaction, lighting and processing are not yet implemented."
      ]
    },
    {
      "id": "kg_a1:guide_press",
      "category": "equipment",
      "icon": "textures/ui/kg_grilling/oil_press",
      "kinds": [],
      "mechanics": [
        "框架、五個壓槌位置及油餅狀態已備妥。這不是已完成的壓榨動畫或出油流程。",
        "Static model reference only. Placement, interaction, lighting and processing are not yet implemented."
      ]
    },
    {
      "id": "kg_a1:guide_vat",
      "category": "equipment",
      "icon": "textures/ui/kg_grilling/big_vat",
      "kinds": [],
      "mechanics": [
        "缸體與內壁已轉換；油量、液面與裝卸尚待接入。",
        "Static model reference only. Placement, interaction, lighting and processing are not yet implemented."
      ]
    },
    {
      "id": "kg_a1:guide_canola",
      "category": "crops",
      "icon": "textures/ui/kg_grilling/canola_stage_7",
      "kinds": [],
      "mechanics": [
        "已轉換age 0–7的四面交叉作物模型；保留原始16×28透明貼圖。 / Four crossed double-sided planes, eight ages and original 16×28 textures.",
        "階段3/4及5/6共用相同原圖，不是漏做。 / Ages 3/4 and 5/6 deliberately have identical source textures.",
        "本包未加入種植、生長、收穫或掉落。 / No planting, growth, harvesting or drops are installed."
      ]
    },
    {
      "id": "kg_a1:guide_recipe_beef",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/beef_cooked",
      "kinds": [],
      "mechanics": [
        "來源配方，未註冊基岩版合成。 / Java-source reference; not an installed Bedrock recipe.",
        "穿串順序（每格的「或」表示擇一）：1. 牛肉塊（來源標籤） → 2. 紅辣椒 → 3. 牛肉塊（來源標籤）",
        "Ordered slots (OR means choose one): 1. ingredients/beef_chunks; 2. red_chili; 3. ingredients/beef_chunks",
        "來源結果 / Source result: kaleidoscope_grilling:raw_beef_skewer",
        "烤熟對應 / Cooked reference: kaleidoscope_grilling:grilled_beef_skewer"
      ]
    },
    {
      "id": "kg_a1:guide_recipe_pork_belly",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/pork_belly_cooked",
      "kinds": [],
      "mechanics": [
        "來源配方，未註冊基岩版合成。 / Java-source reference; not an installed Bedrock recipe.",
        "穿串順序（每格的「或」表示擇一）：1. 生五花肉 → 2. 青辣椒 → 3. 生五花肉",
        "Ordered slots (OR means choose one): 1. raw_pork_belly; 2. green_chili; 3. raw_pork_belly",
        "來源結果 / Source result: kaleidoscope_grilling:raw_pork_belly_skewer",
        "烤熟對應 / Cooked reference: kaleidoscope_grilling:grilled_pork_belly_skewer"
      ]
    },
    {
      "id": "kg_a1:guide_recipe_chicken_skin",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/chicken_skin_cooked",
      "kinds": [],
      "mechanics": [
        "來源配方，未註冊基岩版合成。 / Java-source reference; not an installed Bedrock recipe.",
        "穿串順序（每格的「或」表示擇一）：1. 雞皮（來源標籤） → 2. 雞皮（來源標籤）",
        "Ordered slots (OR means choose one): 1. ingredients/chicken_skin; 2. ingredients/chicken_skin",
        "來源結果 / Source result: kaleidoscope_grilling:raw_chicken_skin_skewer",
        "烤熟對應 / Cooked reference: kaleidoscope_grilling:grilled_chicken_skin_skewer"
      ]
    },
    {
      "id": "kg_a1:guide_recipe_mid_wing",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/mid_wing_cooked",
      "kinds": [],
      "mechanics": [
        "來源配方，未註冊基岩版合成。 / Java-source reference; not an installed Bedrock recipe.",
        "穿串順序（每格的「或」表示擇一）：1. 雞翅（來源標籤） → 2. 紅辣椒 → 3. 雞翅（來源標籤）",
        "Ordered slots (OR means choose one): 1. ingredients/chicken_wings; 2. red_chili; 3. ingredients/chicken_wings",
        "來源結果 / Source result: kaleidoscope_grilling:raw_mid_wing_skewer",
        "烤熟對應 / Cooked reference: kaleidoscope_grilling:grilled_mid_wing_skewer"
      ]
    },
    {
      "id": "kg_a1:guide_recipe_squid_tentacle",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/squid_tentacle_cooked",
      "kinds": [],
      "mechanics": [
        "來源配方，未註冊基岩版合成。 / Java-source reference; not an installed Bedrock recipe.",
        "穿串順序（每格的「或」表示擇一）：1. 魷魚鬚（來源標籤） → 2. 魷魚鬚（來源標籤） → 3. 魷魚鬚（來源標籤）",
        "Ordered slots (OR means choose one): 1. ingredients/squid_tentacles; 2. ingredients/squid_tentacles; 3. ingredients/squid_tentacles",
        "來源結果 / Source result: kaleidoscope_grilling:raw_squid_tentacle_skewer",
        "烤熟對應 / Cooked reference: kaleidoscope_grilling:grilled_squid_tentacle_skewer"
      ]
    },
    {
      "id": "kg_a1:guide_recipe_fish",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/fish_cooked",
      "kinds": [],
      "mechanics": [
        "來源配方，未註冊基岩版合成。 / Java-source reference; not an installed Bedrock recipe.",
        "穿串順序（每格的「或」表示擇一）：1. 鱈魚 或 鮭魚 或 熱帶魚 或 河豚",
        "Ordered slots (OR means choose one): 1. cod OR salmon OR tropical_fish OR pufferfish",
        "來源結果 / Source result: kaleidoscope_grilling:raw_fish_skewer",
        "烤熟對應 / Cooked reference: kaleidoscope_grilling:grilled_fish_skewer"
      ]
    },
    {
      "id": "kg_a1:guide_recipe_sweet_potato_sheet",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/sweet_potato_sheet_cooked",
      "kinds": [],
      "mechanics": [
        "來源配方，未註冊基岩版合成。 / Java-source reference; not an installed Bedrock recipe.",
        "穿串順序（每格的「或」表示擇一）：1. 生苕皮（來源標籤） → 2. 碎魚腥草（來源標籤） → 3. 碎魚腥草（來源標籤）",
        "Ordered slots (OR means choose one): 1. ingredients/raw_sweet_potato_sheets; 2. ingredients/minced_houttuynia; 3. ingredients/minced_houttuynia",
        "來源結果 / Source result: kaleidoscope_grilling:raw_sweet_potato_sheet_skewer",
        "烤熟對應 / Cooked reference: kaleidoscope_grilling:grilled_sweet_potato_sheet_skewer"
      ]
    },
    {
      "id": "kg_a1:guide_recipe_potato_slice",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/potato_slice_cooked",
      "kinds": [],
      "mechanics": [
        "來源配方，未註冊基岩版合成。 / Java-source reference; not an installed Bedrock recipe.",
        "穿串順序（每格的「或」表示擇一）：1. 土豆片（來源標籤） → 2. 土豆片（來源標籤） → 3. 土豆片（來源標籤）",
        "Ordered slots (OR means choose one): 1. ingredients/potato_slices; 2. ingredients/potato_slices; 3. ingredients/potato_slices",
        "來源結果 / Source result: kaleidoscope_grilling:raw_potato_slice_skewer",
        "烤熟對應 / Cooked reference: kaleidoscope_grilling:grilled_potato_slice_skewer"
      ]
    },
    {
      "id": "kg_a1:guide_recipe_caterpillar",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/caterpillar_cooked",
      "kinds": [],
      "mechanics": [
        "來源配方，未註冊基岩版合成。 / Java-source reference; not an installed Bedrock recipe.",
        "穿串順序（每格的「或」表示擇一）：1. 毛毛蟲",
        "Ordered slots (OR means choose one): 1. caterpillar",
        "來源結果 / Source result: kaleidoscope_grilling:raw_caterpillar_skewer",
        "烤熟對應 / Cooked reference: kaleidoscope_grilling:grilled_caterpillar_skewer"
      ]
    },
    {
      "id": "kg_a1:guide_recipe_mushroom",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/mushroom_cooked",
      "kinds": [],
      "mechanics": [
        "來源配方，未註冊基岩版合成。 / Java-source reference; not an installed Bedrock recipe.",
        "穿串順序（每格的「或」表示擇一）：1. 棕色蘑菇 或 紅色蘑菇 → 2. 胡蘿蔔丁（來源標籤） → 3. 棕色蘑菇 或 紅色蘑菇",
        "Ordered slots (OR means choose one): 1. brown_mushroom OR red_mushroom; 2. ingredients/carrot_dice; 3. brown_mushroom OR red_mushroom",
        "來源結果 / Source result: kaleidoscope_grilling:raw_mushroom_skewer",
        "烤熟對應 / Cooked reference: kaleidoscope_grilling:grilled_mushroom_skewer"
      ]
    },
    {
      "id": "kg_a1:guide_recipe_bun_slice",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/bun_slice_cooked",
      "kinds": [],
      "mechanics": [
        "來源配方，未註冊基岩版合成。 / Java-source reference; not an installed Bedrock recipe.",
        "穿串順序（每格的「或」表示擇一）：1. 生饅頭片（來源標籤） → 2. 生饅頭片（來源標籤） → 3. 生饅頭片（來源標籤）",
        "Ordered slots (OR means choose one): 1. ingredients/raw_mantou_slices; 2. ingredients/raw_mantou_slices; 3. ingredients/raw_mantou_slices",
        "來源結果 / Source result: kaleidoscope_grilling:raw_bun_slice_skewer",
        "烤熟對應 / Cooked reference: kaleidoscope_grilling:grilled_bun_slice_skewer"
      ]
    },
    {
      "id": "kg_a1:guide_recipe_ender_pearl",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/ender_pearl_cooked",
      "kinds": [],
      "mechanics": [
        "來源配方，未註冊基岩版合成。 / Java-source reference; not an installed Bedrock recipe.",
        "穿串順序（每格的「或」表示擇一）：1. 末影珍珠 → 2. 甜菜根 → 3. 末影珍珠",
        "Ordered slots (OR means choose one): 1. ender_pearl; 2. beetroot; 3. ender_pearl",
        "來源結果 / Source result: kaleidoscope_grilling:raw_ender_pearl_skewer",
        "烤熟對應 / Cooked reference: kaleidoscope_grilling:grilled_ender_pearl_skewer"
      ]
    },
    {
      "id": "kg_a1:guide_recipe_meatball",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/meatball_cooked",
      "kinds": [],
      "mechanics": [
        "來源配方，未註冊基岩版合成。 / Java-source reference; not an installed Bedrock recipe.",
        "穿串順序（每格的「或」表示擇一）：1. 生肉丸 → 2. 生肉丸 → 3. 生肉丸",
        "Ordered slots (OR means choose one): 1. raw_meatball; 2. raw_meatball; 3. raw_meatball",
        "來源結果 / Source result: kaleidoscope_grilling:raw_meatball_skewer",
        "烤熟對應 / Cooked reference: kaleidoscope_grilling:grilled_meatball_skewer"
      ]
    },
    {
      "id": "kg_a1:guide_recipe_slime",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/slime_frame_2",
      "kinds": [],
      "mechanics": [
        "來源配方，未註冊基岩版合成。 / Java-source reference; not an installed Bedrock recipe.",
        "穿串順序（每格的「或」表示擇一）：1. 黏液球 → 2. 魚腥草（來源標籤） → 3. 黏液球",
        "Ordered slots (OR means choose one): 1. slime_ball; 2. ingredients/houttuynia; 3. slime_ball",
        "來源結果 / Source result: kaleidoscope_grilling:raw_slime_skewer",
        "烤熟對應 / Cooked reference: kaleidoscope_grilling:grilled_slime_skewer"
      ]
    },
    {
      "id": "kg_a1:guide_recipe_meat_and_bone",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/meat_and_bone_cooked",
      "kinds": [],
      "mechanics": [
        "來源配方，未註冊基岩版合成。 / Java-source reference; not an installed Bedrock recipe.",
        "穿串順序（每格的「或」表示擇一）：1. 生小肉塊 → 2. 骨頭 → 3. 生小肉塊",
        "Ordered slots (OR means choose one): 1. raw_cut_small_meats; 2. bone; 3. raw_cut_small_meats",
        "來源結果 / Source result: kaleidoscope_grilling:raw_meat_and_bone_skewer",
        "烤熟對應 / Cooked reference: kaleidoscope_grilling:grilled_meat_and_bone_skewer"
      ]
    },
    {
      "id": "kg_a1:guide_recipe_fried_egg",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/fried_egg_cooked",
      "kinds": [],
      "mechanics": [
        "來源配方，未註冊基岩版合成。 / Java-source reference; not an installed Bedrock recipe.",
        "穿串順序（每格的「或」表示擇一）：1. 煎蛋 → 2. 煎蛋",
        "Ordered slots (OR means choose one): 1. fried_egg; 2. fried_egg",
        "來源結果 / Source result: kaleidoscope_grilling:raw_fried_egg_skewer",
        "烤熟對應 / Cooked reference: kaleidoscope_grilling:grilled_fried_egg_skewer"
      ]
    },
    {
      "id": "kg_a1:guide_recipe_gluten",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/gluten_cooked",
      "kinds": [],
      "mechanics": [
        "來源配方，未註冊基岩版合成。 / Java-source reference; not an installed Bedrock recipe.",
        "穿串順序（每格的「或」表示擇一）：1. 生麵團 → 2. 生麵團",
        "Ordered slots (OR means choose one): 1. raw_dough; 2. raw_dough",
        "來源結果 / Source result: kaleidoscope_grilling:raw_gluten_skewer",
        "烤熟對應 / Cooked reference: kaleidoscope_grilling:grilled_gluten_skewer"
      ]
    },
    {
      "id": "kg_a1:guide_recipe_lamb",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/lamb_cooked",
      "kinds": [],
      "mechanics": [
        "來源配方，未註冊基岩版合成。 / Java-source reference; not an installed Bedrock recipe.",
        "穿串順序（每格的「或」表示擇一）：1. 生羊排 → 2. 油 → 3. 生羊排",
        "Ordered slots (OR means choose one): 1. raw_lamb_chops; 2. oil; 3. raw_lamb_chops",
        "來源結果 / Source result: kaleidoscope_grilling:raw_lamb_skewer",
        "烤熟對應 / Cooked reference: kaleidoscope_grilling:grilled_lamb_skewer"
      ]
    },
    {
      "id": "kg_a1:guide_recipe_golden",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/golden_cooked",
      "kinds": [],
      "mechanics": [
        "來源配方，未註冊基岩版合成。 / Java-source reference; not an installed Bedrock recipe.",
        "穿串順序（每格的「或」表示擇一）：1. 金蘋果 → 2. 不死圖騰 → 3. 金胡蘿蔔",
        "Ordered slots (OR means choose one): 1. golden_apple; 2. totem_of_undying; 3. golden_carrot",
        "來源結果 / Source result: kaleidoscope_grilling:raw_golden_skewer",
        "烤熟對應 / Cooked reference: kaleidoscope_grilling:grilled_golden_skewer"
      ]
    },
    {
      "id": "kg_a1:guide_recipe_ordinary",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/ordinary_full",
      "kinds": [],
      "mechanics": [
        "來源配方，未註冊基岩版合成。 / Java-source reference; not an installed Bedrock recipe.",
        "穿串順序（每格的「或」表示擇一）：1. 毒馬鈴薯 → 2. 蜘蛛眼 → 3. 河豚",
        "Ordered slots (OR means choose one): 1. poisonous_potato; 2. spider_eye; 3. pufferfish",
        "來源結果 / Source result: kaleidoscope_grilling:ordinary_skewer",
        "來源沒有另外的生／熟轉換，不補造結果。 / No separate raw-to-cooked result is authored."
      ]
    },
    {
      "id": "kg_a1:guide_seasoning_0",
      "category": "seasonings",
      "icon": "textures/ui/kg_grilling/grill_legged_lit",
      "kinds": [],
      "mechanics": [
        "來源調料關聯，尚未接入基岩版效果。 / Source seasoning association; no Bedrock effect installed.",
        "來源材料 / Source ingredient: minecraft:redstone",
        "來源種類 / Source kind: speed"
      ]
    },
    {
      "id": "kg_a1:guide_seasoning_1",
      "category": "seasonings",
      "icon": "textures/ui/kg_grilling/grill_legged_lit",
      "kinds": [],
      "mechanics": [
        "來源調料關聯，尚未接入基岩版效果。 / Source seasoning association; no Bedrock effect installed.",
        "來源材料 / Source ingredient: minecraft:gunpowder",
        "來源種類 / Source kind: strength"
      ]
    },
    {
      "id": "kg_a1:guide_seasoning_2",
      "category": "seasonings",
      "icon": "textures/ui/kg_grilling/grill_legged_lit",
      "kinds": [],
      "mechanics": [
        "來源調料關聯，尚未接入基岩版效果。 / Source seasoning association; no Bedrock effect installed.",
        "來源材料 / Source ingredient: kaleidoscope_grilling:houttuynia_powder",
        "來源種類 / Source kind: duration"
      ]
    },
    {
      "id": "kg_a1:guide_seasoning_3",
      "category": "seasonings",
      "icon": "textures/ui/kg_grilling/grill_legged_lit",
      "kinds": [],
      "mechanics": [
        "來源調料關聯，尚未接入基岩版效果。 / Source seasoning association; no Bedrock effect installed.",
        "來源材料 / Source ingredient: kaleidoscope_grilling:totem_powder",
        "來源種類 / Source kind: totem"
      ]
    },
    {
      "id": "kg_a1:guide_seasoning_4",
      "category": "seasonings",
      "icon": "textures/ui/kg_grilling/grill_legged_lit",
      "kinds": [],
      "mechanics": [
        "來源調料關聯，尚未接入基岩版效果。 / Source seasoning association; no Bedrock effect installed.",
        "來源材料 / Source ingredient: kaleidoscope_grilling:dragon_egg_powder",
        "來源種類 / Source kind: vitality"
      ]
    },
    {
      "id": "kg_a1:guide_seasoning_5",
      "category": "seasonings",
      "icon": "textures/ui/kg_grilling/grill_legged_lit",
      "kinds": [],
      "mechanics": [
        "來源調料關聯，尚未接入基岩版效果。 / Source seasoning association; no Bedrock effect installed.",
        "來源材料 / Source ingredient: kaleidoscope_grilling:sichuan_pepper",
        "來源種類 / Source kind: numbness"
      ]
    },
    {
      "id": "kg_a1:guide_saved",
      "category": "saved",
      "icon": "textures/ui/kg_grilling/grill_legged_lit",
      "kinds": [],
      "mechanics": [
        "原型頁的收藏不是遊戲存檔；本章沒有假保存按鈕。 / Prototype favourites are not game saves; this chapter has no fake save button.",
        "記錄、命名、重開與多人儲存仍屬後續功能，沒有因共用指南而刪除。 / Recording, naming, reopening and multiplayer persistence remain required work."
      ]
    }
  ],
  "names": {
    "zh_TW": {
      "kg_a1:guide_start": "閱讀前先看",
      "kg_a1:guide_grill": "烤爐",
      "kg_a1:guide_rack": "進階工具架",
      "kg_a1:guide_press": "榨油機",
      "kg_a1:guide_vat": "大缸",
      "kg_a1:guide_canola": "油菜・八段生長素材",
      "kg_a1:guide_recipe_beef": "牛肉串",
      "kg_a1:guide_recipe_pork_belly": "五花肉串",
      "kg_a1:guide_recipe_chicken_skin": "雞皮串",
      "kg_a1:guide_recipe_mid_wing": "雞翅中串",
      "kg_a1:guide_recipe_squid_tentacle": "魷魚鬚串",
      "kg_a1:guide_recipe_fish": "魚串",
      "kg_a1:guide_recipe_sweet_potato_sheet": "苕皮串",
      "kg_a1:guide_recipe_potato_slice": "土豆片串",
      "kg_a1:guide_recipe_caterpillar": "毛毛蟲串",
      "kg_a1:guide_recipe_mushroom": "蘑菇串",
      "kg_a1:guide_recipe_bun_slice": "饅頭片串",
      "kg_a1:guide_recipe_ender_pearl": "末影珍珠串",
      "kg_a1:guide_recipe_meatball": "丸子串",
      "kg_a1:guide_recipe_slime": "黏液串",
      "kg_a1:guide_recipe_meat_and_bone": "骨肉相連串",
      "kg_a1:guide_recipe_fried_egg": "煎蛋串",
      "kg_a1:guide_recipe_gluten": "麵筋串",
      "kg_a1:guide_recipe_lamb": "羊肉串",
      "kg_a1:guide_recipe_golden": "黃金串",
      "kg_a1:guide_recipe_ordinary": "特殊串",
      "kg_a1:guide_seasoning_0": "紅石",
      "kg_a1:guide_seasoning_1": "火藥",
      "kg_a1:guide_seasoning_2": "魚腥草粉",
      "kg_a1:guide_seasoning_3": "圖騰粉",
      "kg_a1:guide_seasoning_4": "龍蛋粉",
      "kg_a1:guide_seasoning_5": "花椒",
      "kg_a1:guide_saved": "自訂配方記錄待接入"
    },
    "zh_CN": {
      "kg_a1:guide_start": "閱讀前先看",
      "kg_a1:guide_grill": "烤爐",
      "kg_a1:guide_rack": "進階工具架",
      "kg_a1:guide_press": "榨油機",
      "kg_a1:guide_vat": "大缸",
      "kg_a1:guide_canola": "油菜・八段生長素材",
      "kg_a1:guide_recipe_beef": "牛肉串",
      "kg_a1:guide_recipe_pork_belly": "五花肉串",
      "kg_a1:guide_recipe_chicken_skin": "雞皮串",
      "kg_a1:guide_recipe_mid_wing": "雞翅中串",
      "kg_a1:guide_recipe_squid_tentacle": "魷魚鬚串",
      "kg_a1:guide_recipe_fish": "魚串",
      "kg_a1:guide_recipe_sweet_potato_sheet": "苕皮串",
      "kg_a1:guide_recipe_potato_slice": "土豆片串",
      "kg_a1:guide_recipe_caterpillar": "毛毛蟲串",
      "kg_a1:guide_recipe_mushroom": "蘑菇串",
      "kg_a1:guide_recipe_bun_slice": "饅頭片串",
      "kg_a1:guide_recipe_ender_pearl": "末影珍珠串",
      "kg_a1:guide_recipe_meatball": "丸子串",
      "kg_a1:guide_recipe_slime": "黏液串",
      "kg_a1:guide_recipe_meat_and_bone": "骨肉相連串",
      "kg_a1:guide_recipe_fried_egg": "煎蛋串",
      "kg_a1:guide_recipe_gluten": "麵筋串",
      "kg_a1:guide_recipe_lamb": "羊肉串",
      "kg_a1:guide_recipe_golden": "黃金串",
      "kg_a1:guide_recipe_ordinary": "特殊串",
      "kg_a1:guide_seasoning_0": "紅石",
      "kg_a1:guide_seasoning_1": "火藥",
      "kg_a1:guide_seasoning_2": "魚腥草粉",
      "kg_a1:guide_seasoning_3": "圖騰粉",
      "kg_a1:guide_seasoning_4": "龍蛋粉",
      "kg_a1:guide_seasoning_5": "花椒",
      "kg_a1:guide_saved": "自訂配方記錄待接入"
    },
    "en_US": {
      "kg_a1:guide_start": "Read first",
      "kg_a1:guide_grill": "Grill",
      "kg_a1:guide_rack": "Advanced rack",
      "kg_a1:guide_press": "Oil press",
      "kg_a1:guide_vat": "Large vat",
      "kg_a1:guide_canola": "Canola · eight visual ages",
      "kg_a1:guide_recipe_beef": "Beef skewer",
      "kg_a1:guide_recipe_pork_belly": "Pork belly skewer",
      "kg_a1:guide_recipe_chicken_skin": "Chicken skin skewer",
      "kg_a1:guide_recipe_mid_wing": "Chicken wing skewer",
      "kg_a1:guide_recipe_squid_tentacle": "Squid tentacle skewer",
      "kg_a1:guide_recipe_fish": "Fish skewer",
      "kg_a1:guide_recipe_sweet_potato_sheet": "Sweet potato starch sheet skewer",
      "kg_a1:guide_recipe_potato_slice": "Potato slice skewer",
      "kg_a1:guide_recipe_caterpillar": "Caterpillar skewer",
      "kg_a1:guide_recipe_mushroom": "Mushroom skewer",
      "kg_a1:guide_recipe_bun_slice": "Mantou slice skewer",
      "kg_a1:guide_recipe_ender_pearl": "Ender pearl skewer",
      "kg_a1:guide_recipe_meatball": "Meatball skewer",
      "kg_a1:guide_recipe_slime": "Slime skewer",
      "kg_a1:guide_recipe_meat_and_bone": "Meat and bone skewer",
      "kg_a1:guide_recipe_fried_egg": "Fried egg skewer",
      "kg_a1:guide_recipe_gluten": "Gluten skewer",
      "kg_a1:guide_recipe_lamb": "Lamb skewer",
      "kg_a1:guide_recipe_golden": "Golden skewer",
      "kg_a1:guide_recipe_ordinary": "Ordinary special skewer",
      "kg_a1:guide_seasoning_0": "Redstone",
      "kg_a1:guide_seasoning_1": "Gunpowder",
      "kg_a1:guide_seasoning_2": "Houttuynia Powder",
      "kg_a1:guide_seasoning_3": "Totem Powder",
      "kg_a1:guide_seasoning_4": "Dragon Egg Powder",
      "kg_a1:guide_seasoning_5": "Sichuan Pepper",
      "kg_a1:guide_saved": "Custom recipe storage is not implemented"
    }
  },
  "text": {
    "zh_TW": {
      "title": "煙火 · 素材預覽",
      "intro": "此包只測試指南章節。煙火食物、設備操作與作物生長尚未加入遊戲。",
      "all": "全部條目",
      "select": "選擇資料條目。",
      "back": "返回",
      "language_note": "標題跟隨森羅物語語言；本版說明使用繁中＋英文，以避開1.0.6語系過濾問題。",
      "start": "開始／版本範圍",
      "equipment": "設備圖鑑",
      "crops": "作物",
      "recipes": "固定串配方（來源參考）",
      "seasonings": "調料資料（來源參考）",
      "saved": "我的配方（開發中）"
    },
    "zh_CN": {
      "title": "煙火 · 素材預覽",
      "intro": "此包只測試指南章節。煙火食物、設備操作與作物生長尚未加入遊戲。",
      "all": "全部條目",
      "select": "選擇資料條目。",
      "back": "返回",
      "language_note": "標題跟隨森羅物語語言；本版說明使用繁中＋英文，以避開1.0.6語系過濾問題。",
      "start": "開始／版本範圍",
      "equipment": "設備圖鑑",
      "crops": "作物",
      "recipes": "固定串配方（來源參考）",
      "seasonings": "調料資料（來源參考）",
      "saved": "我的配方（開發中）"
    },
    "en_US": {
      "title": "Grilling · asset preview",
      "intro": "Guide-only development preview. No playable Grilling items, station recipes or crop growth are installed.",
      "all": "All entries",
      "select": "Select a reference entry.",
      "back": "Back",
      "language_note": "Titles follow Cookery language; descriptions use Traditional Chinese + English for v1.0.6 compatibility.",
      "start": "Start / scope",
      "equipment": "Equipment",
      "crops": "Crops",
      "recipes": "Skewer recipes (source reference)",
      "seasonings": "Seasoning references",
      "saved": "My recipes (planned)"
    }
  }
};
