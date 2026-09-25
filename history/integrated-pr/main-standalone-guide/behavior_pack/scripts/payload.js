// Generated A1.16 per-player localized Cookery guide extension.
export const GUIDE_PAYLOAD = {
  "api": 1,
  "id": "kg_a1:grilling",
  "version": "0.1.16",
  "order": 300,
  "icon": "textures/ui/kg_grilling/guide_grill",
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
      "id": "how_to",
      "labelKey": "how_to",
      "fallback": "Getting started",
      "icon": "textures/ui/kg_grilling/guide_grill"
    },
    {
      "id": "recipes",
      "labelKey": "recipes",
      "fallback": "Skewer recipes",
      "icon": "textures/ui/kg_grilling/guide_recipe_book"
    },
    {
      "id": "seasonings",
      "labelKey": "seasonings",
      "fallback": "Seasonings & effects",
      "icon": "textures/ui/kg_grilling/guide_seasoning"
    }
  ],
  "entries": [
    {
      "id": "kg_a1:guide_grill",
      "category": "how_to",
      "icon": "textures/ui/kg_grilling/guide_grill",
      "kinds": [],
      "mechanics": [
        "燒烤架一次最多放 3 串。先點火，再放入生串。",
        "刷油後翻面 4 次；需要調料時，在出爐前撒上特製調料。",
        "烤好後及時取出；繼續加熱會過熟，最後會燒成木炭。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "烧烤架一次最多放 3 串。先点火，再放入生串。",
          "刷油后翻面 4 次；需要调料时，在出炉前撒上特制调料。",
          "烤好后及时取出；继续加热会过熟，最后会烧成木炭。"
        ],
        "zh_TW": [
          "燒烤架一次最多放 3 串。先點火，再放入生串。",
          "刷油後翻面 4 次；需要調料時，在出爐前撒上特製調料。",
          "烤好後及時取出；繼續加熱會過熟，最後會燒成木炭。"
        ],
        "en_US": [
          "A grill holds up to 3 skewers. Light it first, then insert raw skewers.",
          "Brush with oil and flip 4 times. Add special seasoning before taking the skewer out.",
          "Remove cooked skewers in time; continued heating overcooks them and eventually burns them into charcoal."
        ]
      }
    },
    {
      "id": "kg_a1:guide_threading",
      "category": "how_to",
      "icon": "textures/ui/kg_grilling/guide_threading",
      "kinds": [],
      "mechanics": [
        "副手拿木棍或未完成烤串，主手拿可穿串食材，使用即可逐份穿入。",
        "每串最多 3 份食材；固定組合會完成對應生串，否則可做成秘製烤串。",
        "潛行時可拆解尚未烤熟的手工串，取回食材與木棍。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "副手拿木棍或未完成烤串，主手拿可穿串食材，使用即可逐份穿入。",
          "每串最多 3 份食材；固定组合会完成对应生串，否则可做成秘制烤串。",
          "潜行时可拆解尚未烤熟的手工串，取回食材与木棍。"
        ],
        "zh_TW": [
          "副手拿木棍或未完成烤串，主手拿可穿串食材，使用即可逐份穿入。",
          "每串最多 3 份食材；固定組合會完成對應生串，否則可做成秘製烤串。",
          "潛行時可拆解尚未烤熟的手工串，取回食材與木棍。"
        ],
        "en_US": [
          "Hold a stick or unfinished skewer in the off hand and a skewerable ingredient in the main hand, then use it to thread one ingredient at a time.",
          "A skewer holds up to 3 ingredients. Fixed combinations become their matching raw skewer; other combinations can become a Secret Mix Skewer.",
          "Sneak to disassemble an uncooked handmade skewer and recover its ingredients and stick."
        ]
      }
    },
    {
      "id": "kg_a1:guide_plate",
      "category": "how_to",
      "icon": "textures/ui/kg_grilling/guide_plate",
      "kinds": [],
      "mechanics": [
        "烤串盤最多收納 5 串。手持烤串對盤使用可放入，空手使用會取回最後放入的一串。",
        "手持有內容的盤子潛行放置，可把整盤擺到實心方塊或森羅物語桌子上。",
        "直接食用盤子時會先吃掉盤中飽食度最高的一串。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "烤串盘最多收纳 5 串。手持烤串对盘使用可放入，空手使用会取回最后放入的一串。",
          "手持有内容的盘子潜行放置，可把整盘摆到实心方块或森罗物语桌子上。",
          "直接食用盘子时会先吃掉盘中饱食度最高的一串。"
        ],
        "zh_TW": [
          "烤串盤最多收納 5 串。手持烤串對盤使用可放入，空手使用會取回最後放入的一串。",
          "手持有內容的盤子潛行放置，可把整盤擺到實心方塊或森羅物語桌子上。",
          "直接食用盤子時會先吃掉盤中飽食度最高的一串。"
        ],
        "en_US": [
          "A skewer plate stores up to 5 skewers. Use a skewer on the plate to add it; use an empty hand to take back the last skewer.",
          "Sneak-place a non-empty plate on a solid block or Kaleidoscope Cookery table.",
          "Eating from the plate consumes the skewer with the highest nutrition first."
        ]
      }
    },
    {
      "id": "kg_a1:guide_crops",
      "category": "how_to",
      "icon": "textures/ui/kg_grilling/guide_crops",
      "kinds": [],
      "mechanics": [
        "可種植並採收油菜、折耳根、洋蔥與番薯；成熟作物可繼續進入加工鏈。",
        "油菜可製油餅並榨成菜籽油；折耳根、洋蔥與番薯可繼續切碎、研磨或烹調。",
        "Cookery 的紅辣椒可用磨石加工成紅辣椒粉，再用於製作辣椒油。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "可种植并采收油菜、折耳根、洋葱与红薯；成熟作物可继续进入加工链。",
          "油菜可制油饼并榨成菜籽油；折耳根、洋葱与红薯可继续切碎、研磨或烹调。",
          "Cookery 的红辣椒可用磨石加工成红辣椒粉，再用于制作辣椒油。"
        ],
        "zh_TW": [
          "可種植並採收油菜、折耳根、洋蔥與番薯；成熟作物可繼續進入加工鏈。",
          "油菜可製油餅並榨成菜籽油；折耳根、洋蔥與番薯可繼續切碎、研磨或烹調。",
          "Cookery 的紅辣椒可用磨石加工成紅辣椒粉，再用於製作辣椒油。"
        ],
        "en_US": [
          "Canola, Houttuynia, Onion, and Sweet Potato can be planted and harvested, then processed further.",
          "Canola becomes oil cake and canola oil; Houttuynia, Onion, and Sweet Potato feed into chopping, milling, or cooking chains.",
          "Cookery Red Chili can be milled into Red Chili Powder and then used for Chili Oil."
        ]
      }
    },
    {
      "id": "kg_a1:guide_oil",
      "category": "how_to",
      "icon": "textures/ui/kg_grilling/guide_oil",
      "kinds": [],
      "mechanics": [
        "榨油器最多放 4 個油餅。裝滿後用鐵砧或可壓榨石反覆敲擊，完成後輸出菜籽油與油渣。",
        "附近有可接收的大缸時，菜籽油會優先灌入大缸；大缸容量為 8 桶且一次只保存一種流體。",
        "大缸可保存水、熔岩與三種煙火油，也能把煙火油直接灌入 Cookery 油壺。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "榨油器最多放 4 个油饼。装满后用铁砧或可压榨石反复敲击，完成后输出菜籽油与油渣。",
          "附近有可接收的大缸时，菜籽油会优先灌入大缸；大缸容量为 8 桶且一次只保存一种流体。",
          "大缸可保存水、熔岩与三种烟火油，也能把烟火油直接灌入 Cookery 油壶。"
        ],
        "zh_TW": [
          "榨油器最多放 4 個油餅。裝滿後用鐵砧或可壓榨石反覆敲擊，完成後輸出菜籽油與油渣。",
          "附近有可接收的大缸時，菜籽油會優先灌入大缸；大缸容量為 8 桶且一次只保存一種流體。",
          "大缸可保存水、熔岩與三種煙火油，也能把煙火油直接灌入 Cookery 油壺。"
        ],
        "en_US": [
          "The oil press holds up to 4 oil cakes. Fill it, then strike it repeatedly with an anvil or valid press stone to produce canola oil and oil residue.",
          "If a compatible large vat is nearby, canola oil is deposited there first. A vat holds 8 buckets and stores one fluid type at a time.",
          "The vat stores water, lava, and the three Grilling oils, and can fill Cookery oil pots directly."
        ]
      }
    },
    {
      "id": "kg_a1:guide_recipe_book",
      "category": "how_to",
      "icon": "textures/ui/kg_grilling/guide_recipe_book",
      "kinds": [],
      "mechanics": [
        "主手拿空串譜、副手拿完整生串，使用即可記錄該配方；生串不會被消耗。",
        "已記錄的串譜配合副手木棍使用，會從背包按配方取料並自動製作。",
        "已記錄的串譜也可貼到方塊側面；拿木棍對牆上的串譜使用即可快速製作。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "主手拿空串谱、副手拿完整生串，使用即可记录该配方；生串不会被消耗。",
          "已记录的串谱配合副手木棍使用，会从背包按配方取料并自动制作。",
          "已记录的串谱也可贴到方块侧面；拿木棍对墙上的串谱使用即可快速制作。"
        ],
        "zh_TW": [
          "主手拿空串譜、副手拿完整生串，使用即可記錄該配方；生串不會被消耗。",
          "已記錄的串譜配合副手木棍使用，會從背包按配方取料並自動製作。",
          "已記錄的串譜也可貼到方塊側面；拿木棍對牆上的串譜使用即可快速製作。"
        ],
        "en_US": [
          "Hold an empty Skewer Recipe Book in the main hand and a complete raw skewer in the off hand, then use it to record the recipe without consuming the skewer.",
          "Use a recorded book with a stick in the off hand to pull ingredients from inventory and craft automatically.",
          "A recorded book can also be placed on a block side; use a stick on the placed recipe for quick crafting."
        ]
      }
    },
    {
      "id": "kg_a1:guide_recipe_beef",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/beef_cooked",
      "kinds": [],
      "mechanics": [
        "材料順序：牛肉塊 → 紅辣椒 → 牛肉塊",
        "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "材料顺序：牛肉块 → 红辣椒 → 牛肉块",
          "穿好后放上烧烤架，依刷油、翻面与调味流程烤熟。"
        ],
        "zh_TW": [
          "材料順序：牛肉塊 → 紅辣椒 → 牛肉塊",
          "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
        ],
        "en_US": [
          "Ingredient order: Beef Chunks → Red Chili → Beef Chunks",
          "Put the finished raw skewer on the grill, then oil, flip, and season it until cooked."
        ]
      }
    },
    {
      "id": "kg_a1:guide_recipe_pork_belly",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/pork_belly_cooked",
      "kinds": [],
      "mechanics": [
        "材料順序：生五花肉 → 青辣椒 → 生五花肉",
        "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "材料顺序：生五花肉 → 青辣椒 → 生五花肉",
          "穿好后放上烧烤架，依刷油、翻面与调味流程烤熟。"
        ],
        "zh_TW": [
          "材料順序：生五花肉 → 青辣椒 → 生五花肉",
          "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
        ],
        "en_US": [
          "Ingredient order: Raw Pork Belly → Green Chili → Raw Pork Belly",
          "Put the finished raw skewer on the grill, then oil, flip, and season it until cooked."
        ]
      }
    },
    {
      "id": "kg_a1:guide_recipe_chicken_skin",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/chicken_skin_cooked",
      "kinds": [],
      "mechanics": [
        "材料順序：雞皮 → 雞皮",
        "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "材料顺序：鸡皮 → 鸡皮",
          "穿好后放上烧烤架，依刷油、翻面与调味流程烤熟。"
        ],
        "zh_TW": [
          "材料順序：雞皮 → 雞皮",
          "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
        ],
        "en_US": [
          "Ingredient order: Chicken Skin → Chicken Skin",
          "Put the finished raw skewer on the grill, then oil, flip, and season it until cooked."
        ]
      }
    },
    {
      "id": "kg_a1:guide_recipe_mid_wing",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/mid_wing_cooked",
      "kinds": [],
      "mechanics": [
        "材料順序：雞翅 → 紅辣椒 → 雞翅",
        "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "材料顺序：鸡翅 → 红辣椒 → 鸡翅",
          "穿好后放上烧烤架，依刷油、翻面与调味流程烤熟。"
        ],
        "zh_TW": [
          "材料順序：雞翅 → 紅辣椒 → 雞翅",
          "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
        ],
        "en_US": [
          "Ingredient order: Chicken Wing → Red Chili → Chicken Wing",
          "Put the finished raw skewer on the grill, then oil, flip, and season it until cooked."
        ]
      }
    },
    {
      "id": "kg_a1:guide_recipe_squid_tentacle",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/squid_tentacle_cooked",
      "kinds": [],
      "mechanics": [
        "材料順序：魷魚鬚 → 魷魚鬚 → 魷魚鬚",
        "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "材料顺序：鱿鱼须 → 鱿鱼须 → 鱿鱼须",
          "穿好后放上烧烤架，依刷油、翻面与调味流程烤熟。"
        ],
        "zh_TW": [
          "材料順序：魷魚鬚 → 魷魚鬚 → 魷魚鬚",
          "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
        ],
        "en_US": [
          "Ingredient order: Squid Tentacle → Squid Tentacle → Squid Tentacle",
          "Put the finished raw skewer on the grill, then oil, flip, and season it until cooked."
        ]
      }
    },
    {
      "id": "kg_a1:guide_recipe_fish",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/fish_cooked",
      "kinds": [],
      "mechanics": [
        "材料順序：鱈魚 / 鮭魚 / 熱帶魚 / 河豚",
        "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "材料顺序：鳕鱼 / 鲑鱼 / 热带鱼 / 河豚",
          "穿好后放上烧烤架，依刷油、翻面与调味流程烤熟。"
        ],
        "zh_TW": [
          "材料順序：鱈魚 / 鮭魚 / 熱帶魚 / 河豚",
          "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
        ],
        "en_US": [
          "Ingredient order: Cod / Salmon / Tropical Fish / Pufferfish",
          "Put the finished raw skewer on the grill, then oil, flip, and season it until cooked."
        ]
      }
    },
    {
      "id": "kg_a1:guide_recipe_sweet_potato_sheet",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/sweet_potato_sheet_cooked",
      "kinds": [],
      "mechanics": [
        "材料順序：生苕皮 → 碎魚腥草 → 碎魚腥草",
        "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "材料顺序：生苕皮 → 碎鱼腥草 → 碎鱼腥草",
          "穿好后放上烧烤架，依刷油、翻面与调味流程烤熟。"
        ],
        "zh_TW": [
          "材料順序：生苕皮 → 碎魚腥草 → 碎魚腥草",
          "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
        ],
        "en_US": [
          "Ingredient order: Raw Sweet Potato Sheet → Minced Houttuynia → Minced Houttuynia",
          "Put the finished raw skewer on the grill, then oil, flip, and season it until cooked."
        ]
      }
    },
    {
      "id": "kg_a1:guide_recipe_potato_slice",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/potato_slice_cooked",
      "kinds": [],
      "mechanics": [
        "材料順序：土豆片 → 土豆片 → 土豆片",
        "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "材料顺序：土豆片 → 土豆片 → 土豆片",
          "穿好后放上烧烤架，依刷油、翻面与调味流程烤熟。"
        ],
        "zh_TW": [
          "材料順序：土豆片 → 土豆片 → 土豆片",
          "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
        ],
        "en_US": [
          "Ingredient order: Potato Slice → Potato Slice → Potato Slice",
          "Put the finished raw skewer on the grill, then oil, flip, and season it until cooked."
        ]
      }
    },
    {
      "id": "kg_a1:guide_recipe_caterpillar",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/caterpillar_cooked",
      "kinds": [],
      "mechanics": [
        "材料順序：毛毛蟲",
        "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "材料顺序：毛毛虫",
          "穿好后放上烧烤架，依刷油、翻面与调味流程烤熟。"
        ],
        "zh_TW": [
          "材料順序：毛毛蟲",
          "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
        ],
        "en_US": [
          "Ingredient order: Caterpillar",
          "Put the finished raw skewer on the grill, then oil, flip, and season it until cooked."
        ]
      }
    },
    {
      "id": "kg_a1:guide_recipe_mushroom",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/mushroom_cooked",
      "kinds": [],
      "mechanics": [
        "材料順序：棕色蘑菇 / 紅色蘑菇 → 胡蘿蔔丁 → 棕色蘑菇 / 紅色蘑菇",
        "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "材料顺序：棕色蘑菇 / 红色蘑菇 → 胡萝卜丁 → 棕色蘑菇 / 红色蘑菇",
          "穿好后放上烧烤架，依刷油、翻面与调味流程烤熟。"
        ],
        "zh_TW": [
          "材料順序：棕色蘑菇 / 紅色蘑菇 → 胡蘿蔔丁 → 棕色蘑菇 / 紅色蘑菇",
          "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
        ],
        "en_US": [
          "Ingredient order: Brown Mushroom / Red Mushroom → Carrot Dice → Brown Mushroom / Red Mushroom",
          "Put the finished raw skewer on the grill, then oil, flip, and season it until cooked."
        ]
      }
    },
    {
      "id": "kg_a1:guide_recipe_bun_slice",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/bun_slice_cooked",
      "kinds": [],
      "mechanics": [
        "材料順序：生饅頭片 → 生饅頭片 → 生饅頭片",
        "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "材料顺序：生馒头片 → 生馒头片 → 生馒头片",
          "穿好后放上烧烤架，依刷油、翻面与调味流程烤熟。"
        ],
        "zh_TW": [
          "材料順序：生饅頭片 → 生饅頭片 → 生饅頭片",
          "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
        ],
        "en_US": [
          "Ingredient order: Raw Mantou Slice → Raw Mantou Slice → Raw Mantou Slice",
          "Put the finished raw skewer on the grill, then oil, flip, and season it until cooked."
        ]
      }
    },
    {
      "id": "kg_a1:guide_recipe_ender_pearl",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/ender_pearl_cooked",
      "kinds": [],
      "mechanics": [
        "材料順序：末影珍珠 → 甜菜根 → 末影珍珠",
        "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "材料顺序：末影珍珠 → 甜菜根 → 末影珍珠",
          "穿好后放上烧烤架，依刷油、翻面与调味流程烤熟。"
        ],
        "zh_TW": [
          "材料順序：末影珍珠 → 甜菜根 → 末影珍珠",
          "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
        ],
        "en_US": [
          "Ingredient order: Ender Pearl → Beetroot → Ender Pearl",
          "Put the finished raw skewer on the grill, then oil, flip, and season it until cooked."
        ]
      }
    },
    {
      "id": "kg_a1:guide_recipe_meatball",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/meatball_cooked",
      "kinds": [],
      "mechanics": [
        "材料順序：生肉丸 → 生肉丸 → 生肉丸",
        "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "材料顺序：生肉丸 → 生肉丸 → 生肉丸",
          "穿好后放上烧烤架，依刷油、翻面与调味流程烤熟。"
        ],
        "zh_TW": [
          "材料順序：生肉丸 → 生肉丸 → 生肉丸",
          "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
        ],
        "en_US": [
          "Ingredient order: Raw Meatball → Raw Meatball → Raw Meatball",
          "Put the finished raw skewer on the grill, then oil, flip, and season it until cooked."
        ]
      }
    },
    {
      "id": "kg_a1:guide_recipe_slime",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/slime_frame_2",
      "kinds": [],
      "mechanics": [
        "材料順序：黏液球 → 魚腥草 → 黏液球",
        "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "材料顺序：黏液球 → 鱼腥草 → 黏液球",
          "穿好后放上烧烤架，依刷油、翻面与调味流程烤熟。"
        ],
        "zh_TW": [
          "材料順序：黏液球 → 魚腥草 → 黏液球",
          "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
        ],
        "en_US": [
          "Ingredient order: Slimeball → Houttuynia → Slimeball",
          "Put the finished raw skewer on the grill, then oil, flip, and season it until cooked."
        ]
      }
    },
    {
      "id": "kg_a1:guide_recipe_meat_and_bone",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/meat_and_bone_cooked",
      "kinds": [],
      "mechanics": [
        "材料順序：生小肉塊 → 骨頭 → 生小肉塊",
        "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "材料顺序：生小肉块 → 骨头 → 生小肉块",
          "穿好后放上烧烤架，依刷油、翻面与调味流程烤熟。"
        ],
        "zh_TW": [
          "材料順序：生小肉塊 → 骨頭 → 生小肉塊",
          "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
        ],
        "en_US": [
          "Ingredient order: Raw Cut Meat → Bone → Raw Cut Meat",
          "Put the finished raw skewer on the grill, then oil, flip, and season it until cooked."
        ]
      }
    },
    {
      "id": "kg_a1:guide_recipe_fried_egg",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/fried_egg_cooked",
      "kinds": [],
      "mechanics": [
        "材料順序：煎蛋 → 煎蛋",
        "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "材料顺序：煎蛋 → 煎蛋",
          "穿好后放上烧烤架，依刷油、翻面与调味流程烤熟。"
        ],
        "zh_TW": [
          "材料順序：煎蛋 → 煎蛋",
          "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
        ],
        "en_US": [
          "Ingredient order: Fried Egg → Fried Egg",
          "Put the finished raw skewer on the grill, then oil, flip, and season it until cooked."
        ]
      }
    },
    {
      "id": "kg_a1:guide_recipe_gluten",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/gluten_cooked",
      "kinds": [],
      "mechanics": [
        "材料順序：生麵團 → 生麵團",
        "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "材料顺序：生面团 → 生面团",
          "穿好后放上烧烤架，依刷油、翻面与调味流程烤熟。"
        ],
        "zh_TW": [
          "材料順序：生麵團 → 生麵團",
          "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
        ],
        "en_US": [
          "Ingredient order: Raw Dough → Raw Dough",
          "Put the finished raw skewer on the grill, then oil, flip, and season it until cooked."
        ]
      }
    },
    {
      "id": "kg_a1:guide_recipe_lamb",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/lamb_cooked",
      "kinds": [],
      "mechanics": [
        "材料順序：生羊排 → 油 → 生羊排",
        "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "材料顺序：生羊排 → 油 → 生羊排",
          "穿好后放上烧烤架，依刷油、翻面与调味流程烤熟。"
        ],
        "zh_TW": [
          "材料順序：生羊排 → 油 → 生羊排",
          "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
        ],
        "en_US": [
          "Ingredient order: Raw Lamb Chop → Oil → Raw Lamb Chop",
          "Put the finished raw skewer on the grill, then oil, flip, and season it until cooked."
        ]
      }
    },
    {
      "id": "kg_a1:guide_recipe_golden",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/golden_cooked",
      "kinds": [],
      "mechanics": [
        "材料順序：金蘋果 → 不死圖騰 → 金胡蘿蔔",
        "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "材料顺序：金苹果 → 不死图腾 → 金胡萝卜",
          "穿好后放上烧烤架，依刷油、翻面与调味流程烤熟。"
        ],
        "zh_TW": [
          "材料順序：金蘋果 → 不死圖騰 → 金胡蘿蔔",
          "穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。"
        ],
        "en_US": [
          "Ingredient order: Golden Apple → Totem of Undying → Golden Carrot",
          "Put the finished raw skewer on the grill, then oil, flip, and season it until cooked."
        ]
      }
    },
    {
      "id": "kg_a1:guide_recipe_ordinary",
      "category": "recipes",
      "icon": "textures/ui/kg_grilling/ordinary_full",
      "kinds": [],
      "mechanics": [
        "材料順序：毒馬鈴薯 → 蜘蛛眼 → 河豚",
        "這是特殊烤串，沒有另外的生／熟轉換。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "材料顺序：毒土豆 → 蜘蛛眼 → 河豚",
          "这是特殊烤串，没有另外的生／熟转换。"
        ],
        "zh_TW": [
          "材料順序：毒馬鈴薯 → 蜘蛛眼 → 河豚",
          "這是特殊烤串，沒有另外的生／熟轉換。"
        ],
        "en_US": [
          "Ingredient order: Poisonous Potato → Spider Eye → Pufferfish",
          "This special skewer has no separate raw-to-cooked conversion."
        ]
      }
    },
    {
      "id": "kg_a1:guide_seasoning_base",
      "category": "seasonings",
      "icon": "textures/ui/kg_grilling/guide_seasoning",
      "kinds": [],
      "mechanics": [
        "特製調料的基礎三料是青辣椒粉、花椒與洋蔥粉；三種都放入後才能搖勻完成。",
        "調料瓶最多記錄 8 份材料，完成後可使用 16 次。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "特制调料的基础三料是绿辣椒粉、花椒与洋葱粉；三种都放入后才能摇匀完成。",
          "调料瓶最多记录 8 份材料，完成后可使用 16 次。"
        ],
        "zh_TW": [
          "特製調料的基礎三料是青辣椒粉、花椒與洋蔥粉；三種都放入後才能搖勻完成。",
          "調料瓶最多記錄 8 份材料，完成後可使用 16 次。"
        ],
        "en_US": [
          "The three base ingredients are Green Chili Powder, Sichuan Pepper, and Onion Powder. All three are required before shaking the seasoning complete.",
          "A seasoning bottle stores up to 8 ingredients and has 16 uses when finished."
        ]
      }
    },
    {
      "id": "kg_a1:guide_seasoning_redstone",
      "category": "seasonings",
      "icon": "textures/items/redstone_dust",
      "kinds": [],
      "mechanics": [
        "紅石提供速度效果；堆疊更多同種材料時強度會提升。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "红石提供速度效果；堆叠更多同种材料时强度会提升。"
        ],
        "zh_TW": [
          "紅石提供速度效果；堆疊更多同種材料時強度會提升。"
        ],
        "en_US": [
          "Redstone grants Speed; using more of the same ingredient increases the effect strength."
        ]
      }
    },
    {
      "id": "kg_a1:guide_seasoning_gunpowder",
      "category": "seasonings",
      "icon": "textures/items/gunpowder",
      "kinds": [],
      "mechanics": [
        "火藥提供力量效果；堆疊更多同種材料時強度會提升。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "火药提供力量效果；堆叠更多同种材料时强度会提升。"
        ],
        "zh_TW": [
          "火藥提供力量效果；堆疊更多同種材料時強度會提升。"
        ],
        "en_US": [
          "Gunpowder grants Strength; using more of the same ingredient increases the effect strength."
        ]
      }
    },
    {
      "id": "kg_a1:guide_seasoning_houttuynia",
      "category": "seasonings",
      "icon": "textures/ui/kg_grilling/guide_houttuynia_powder",
      "kinds": [],
      "mechanics": [
        "折耳根粉用於延長調料效果時間；加入 1 份會延長，加入 4 份以上時延長幅度更高。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "折耳根粉用于延长调料效果时间；加入 1 份会延长，加入 4 份以上时延长幅度更高。"
        ],
        "zh_TW": [
          "折耳根粉用於延長調料效果時間；加入 1 份會延長，加入 4 份以上時延長幅度更高。"
        ],
        "en_US": [
          "Houttuynia Powder extends seasoning-effect duration; 4 or more gives the stronger duration extension."
        ]
      }
    },
    {
      "id": "kg_a1:guide_seasoning_totem",
      "category": "seasonings",
      "icon": "textures/ui/kg_grilling/guide_totem_powder",
      "kinds": [],
      "mechanics": [
        "不死圖騰粉提供一次重金屬保命效果；受到致命傷時可保住生命，之後會進入重金屬中毒狀態。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "不死图腾粉提供一次重金属保命效果；受到致命伤时可保住生命，之后会进入重金属中毒状态。"
        ],
        "zh_TW": [
          "不死圖騰粉提供一次重金屬保命效果；受到致命傷時可保住生命，之後會進入重金屬中毒狀態。"
        ],
        "en_US": [
          "Totem Powder provides a heavy-metal survival effect that can prevent one lethal hit, followed by heavy-metal poisoning."
        ]
      }
    },
    {
      "id": "kg_a1:guide_seasoning_dragon",
      "category": "seasonings",
      "icon": "textures/ui/kg_grilling/guide_dragon_powder",
      "kinds": [],
      "mechanics": [
        "龍蛋粉提供龍血效果，提高生命上限並提供額外傷害吸收。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "龙蛋粉提供龙血效果，提高生命上限并提供额外伤害吸收。"
        ],
        "zh_TW": [
          "龍蛋粉提供龍血效果，提高生命上限並提供額外傷害吸收。"
        ],
        "en_US": [
          "Dragon Egg Powder grants Dragon Blood, increasing maximum health and providing extra damage absorption."
        ]
      }
    },
    {
      "id": "kg_a1:guide_seasoning_pepper",
      "category": "seasonings",
      "icon": "textures/ui/kg_grilling/guide_sichuan_pepper",
      "kinds": [],
      "mechanics": [
        "花椒也是基礎三料之一；花椒累積到 4 份以上時，趁熱食用會觸發麻木效果。"
      ],
      "mechanicsByLocale": {
        "zh_CN": [
          "花椒也是基础三料之一；花椒累计到 4 份以上时，趁热食用会触发麻木效果。"
        ],
        "zh_TW": [
          "花椒也是基礎三料之一；花椒累積到 4 份以上時，趁熱食用會觸發麻木效果。"
        ],
        "en_US": [
          "Sichuan Pepper is also one of the three base ingredients; 4 or more triggers Numbness when the seasoned skewer is eaten hot."
        ]
      }
    }
  ],
  "names": {
    "zh_CN": {
      "kg_a1:guide_grill": "烧烤架",
      "kg_a1:guide_threading": "手工穿串",
      "kg_a1:guide_plate": "串盘与保存",
      "kg_a1:guide_crops": "作物与加工",
      "kg_a1:guide_oil": "榨油器与大缸",
      "kg_a1:guide_recipe_book": "串谱与快速制作",
      "kg_a1:guide_recipe_beef": "牛肉串",
      "kg_a1:guide_recipe_pork_belly": "五花肉串",
      "kg_a1:guide_recipe_chicken_skin": "鸡皮串",
      "kg_a1:guide_recipe_mid_wing": "中翅串",
      "kg_a1:guide_recipe_squid_tentacle": "鱿鱼须串",
      "kg_a1:guide_recipe_fish": "鱼串",
      "kg_a1:guide_recipe_sweet_potato_sheet": "苕皮串",
      "kg_a1:guide_recipe_potato_slice": "土豆片串",
      "kg_a1:guide_recipe_caterpillar": "猪儿虫串",
      "kg_a1:guide_recipe_mushroom": "蘑菇串",
      "kg_a1:guide_recipe_bun_slice": "馒头片串",
      "kg_a1:guide_recipe_ender_pearl": "末影珍珠串",
      "kg_a1:guide_recipe_meatball": "丸子串",
      "kg_a1:guide_recipe_slime": "黏液串",
      "kg_a1:guide_recipe_meat_and_bone": "骨肉相连串",
      "kg_a1:guide_recipe_fried_egg": "煎蛋串",
      "kg_a1:guide_recipe_gluten": "面筋串",
      "kg_a1:guide_recipe_lamb": "羊肉串",
      "kg_a1:guide_recipe_golden": "黄金烤串",
      "kg_a1:guide_recipe_ordinary": "“普通”烤串",
      "kg_a1:guide_seasoning_base": "特制调料基础",
      "kg_a1:guide_seasoning_redstone": "红石",
      "kg_a1:guide_seasoning_gunpowder": "火药",
      "kg_a1:guide_seasoning_houttuynia": "折耳根粉",
      "kg_a1:guide_seasoning_totem": "不死图腾粉",
      "kg_a1:guide_seasoning_dragon": "龙蛋粉",
      "kg_a1:guide_seasoning_pepper": "花椒"
    },
    "zh_TW": {
      "kg_a1:guide_grill": "燒烤架",
      "kg_a1:guide_threading": "手工穿串",
      "kg_a1:guide_plate": "串盤與保存",
      "kg_a1:guide_crops": "作物與加工",
      "kg_a1:guide_oil": "榨油器與大缸",
      "kg_a1:guide_recipe_book": "串譜與快速製作",
      "kg_a1:guide_recipe_beef": "牛肉串",
      "kg_a1:guide_recipe_pork_belly": "五花肉串",
      "kg_a1:guide_recipe_chicken_skin": "雞皮串",
      "kg_a1:guide_recipe_mid_wing": "中翅串",
      "kg_a1:guide_recipe_squid_tentacle": "魷魚鬚串",
      "kg_a1:guide_recipe_fish": "魚串",
      "kg_a1:guide_recipe_sweet_potato_sheet": "苕皮串",
      "kg_a1:guide_recipe_potato_slice": "馬鈴薯片串",
      "kg_a1:guide_recipe_caterpillar": "豬兒蟲串",
      "kg_a1:guide_recipe_mushroom": "蘑菇串",
      "kg_a1:guide_recipe_bun_slice": "饅頭片串",
      "kg_a1:guide_recipe_ender_pearl": "末影珍珠串",
      "kg_a1:guide_recipe_meatball": "丸子串",
      "kg_a1:guide_recipe_slime": "黏液串",
      "kg_a1:guide_recipe_meat_and_bone": "骨肉相連串",
      "kg_a1:guide_recipe_fried_egg": "煎蛋串",
      "kg_a1:guide_recipe_gluten": "麵筋串",
      "kg_a1:guide_recipe_lamb": "羊肉串",
      "kg_a1:guide_recipe_golden": "黃金烤串",
      "kg_a1:guide_recipe_ordinary": "“普通”烤串",
      "kg_a1:guide_seasoning_base": "特製調料基礎",
      "kg_a1:guide_seasoning_redstone": "紅石",
      "kg_a1:guide_seasoning_gunpowder": "火藥",
      "kg_a1:guide_seasoning_houttuynia": "折耳根粉",
      "kg_a1:guide_seasoning_totem": "不死圖騰粉",
      "kg_a1:guide_seasoning_dragon": "龍蛋粉",
      "kg_a1:guide_seasoning_pepper": "花椒"
    },
    "en_US": {
      "kg_a1:guide_grill": "Grill",
      "kg_a1:guide_threading": "Hand threading",
      "kg_a1:guide_plate": "Skewer plate & storage",
      "kg_a1:guide_crops": "Crops & processing",
      "kg_a1:guide_oil": "Oil press & large vat",
      "kg_a1:guide_recipe_book": "Skewer recipe book",
      "kg_a1:guide_recipe_beef": "Beef Skewer",
      "kg_a1:guide_recipe_pork_belly": "Pork Belly Skewer",
      "kg_a1:guide_recipe_chicken_skin": "Chicken Skin Skewer",
      "kg_a1:guide_recipe_mid_wing": "Mid-Wing Skewer",
      "kg_a1:guide_recipe_squid_tentacle": "Squid Tentacle Skewer",
      "kg_a1:guide_recipe_fish": "Fish Skewer",
      "kg_a1:guide_recipe_sweet_potato_sheet": "Sweet Potato Sheet Skewer",
      "kg_a1:guide_recipe_potato_slice": "Potato Slice Skewer",
      "kg_a1:guide_recipe_caterpillar": "Caterpillar Skewer",
      "kg_a1:guide_recipe_mushroom": "Mushroom Skewer",
      "kg_a1:guide_recipe_bun_slice": "Bun Slice Skewer",
      "kg_a1:guide_recipe_ender_pearl": "Ender Pearl Skewer",
      "kg_a1:guide_recipe_meatball": "Meatball Skewer",
      "kg_a1:guide_recipe_slime": "Slime Skewer",
      "kg_a1:guide_recipe_meat_and_bone": "Meat and Bone Skewer",
      "kg_a1:guide_recipe_fried_egg": "Fried Egg Skewer",
      "kg_a1:guide_recipe_gluten": "Gluten Skewer",
      "kg_a1:guide_recipe_lamb": "Lamb Skewer",
      "kg_a1:guide_recipe_golden": "Golden Skewer",
      "kg_a1:guide_recipe_ordinary": "\"Ordinary\" Skewer",
      "kg_a1:guide_seasoning_base": "Special seasoning basics",
      "kg_a1:guide_seasoning_redstone": "Redstone",
      "kg_a1:guide_seasoning_gunpowder": "Gunpowder",
      "kg_a1:guide_seasoning_houttuynia": "Houttuynia Powder",
      "kg_a1:guide_seasoning_totem": "Totem Powder",
      "kg_a1:guide_seasoning_dragon": "Dragon Egg Powder",
      "kg_a1:guide_seasoning_pepper": "Sichuan Pepper"
    }
  },
  "text": {
    "zh_CN": {
      "title": "森罗物语：烟火",
      "intro": "烧烤、穿串、调料、作物与油料的玩法指南。",
      "all": "全部条目",
      "select": "选择一个主题。",
      "back": "返回",
      "language_note": "语言会跟随森罗物语指南设置。",
      "how_to": "玩法与取得方式",
      "recipes": "烤串食谱",
      "seasonings": "调料与效果"
    },
    "zh_TW": {
      "title": "森羅物語：煙火",
      "intro": "燒烤、穿串、調料、作物與油料的玩法指南。",
      "all": "全部條目",
      "select": "選擇一個主題。",
      "back": "返回",
      "language_note": "語言會跟隨森羅物語指南設定。",
      "how_to": "玩法與取得方式",
      "recipes": "烤串食譜",
      "seasonings": "調料與效果"
    },
    "en_US": {
      "title": "Kaleidoscope Grilling",
      "intro": "Guide to grilling, threading skewers, seasonings, crops, and oils.",
      "all": "All entries",
      "select": "Choose a topic.",
      "back": "Back",
      "language_note": "Language follows the Kaleidoscope Cookery guide setting.",
      "how_to": "Getting started",
      "recipes": "Skewer recipes",
      "seasonings": "Seasonings & effects"
    }
  }
};
