from __future__ import annotations
import hashlib,urllib.request

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
FILES={
 'items':('neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/registry/ModItems.java','6f190e03dc1b7c54bbbae1d5d49d35c78c19b63a',(
  '"sugared_tomato"','"pepper_honey"','"wedding_candy"','"houttuynia_stir_fried_pork"',
  '"green_pepper_squid_tentacles"','"braised_chicken_wings"','"potato_beef_stew"',
  '"red_sweet_potato_porridge"','"sour_spicy_noodles"',
  '.nutrition(20)','.saturationModifier(0.5F)','alwaysEdible()'
 )),
 'seasoning_use':('neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/seasoning/SeasoningUse.java','b9452cabae45997272de474ca39825c9fa3c5b6c',(
  'if (ingredients.isEmpty()) return false;','SeasoningData.getUses(seasoning) + 1',
  'next >= SeasoningData.MAX_USES','new ItemStack(ModItems.EMPTY_SEASONING_BOTTLE.get())'
 )),
 'pot_mixin':('neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/mixin/PotBlockEntityMixin.java','49cc8d6cc009cebf8c4ade038f3de9d092b5edfb',(
  'grilling$seasoning','grilling$oilType','case "secret_chili" -> 600;',
  'case "premium_chili" -> 1200;','default -> 60;','grilling$seasoning.clear();'
 )),
 'stockpot_mixin':('neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/mixin/StockpotBlockEntityMixin.java','44e786b3e609623747e8b3a5e7124f02b501ccaa',(
  'grilling$seasoning','SeasoningData.getUses(stack) + 1','HotFoodApi.makeHot(result, level, 60);'
 )),
 'sugared':('common/src/main/resources/data/kaleidoscope_grilling/recipe/sugared_tomato.json','bd5dbd8d3ed3788e3637e3766d04243c32808cec',(
  'c:crops/tomato','minecraft:sugar','kaleidoscope_grilling:sugared_tomato'
 )),
 'pepper_honey':('common/src/main/resources/data/kaleidoscope_grilling/recipe/pepper_honey.json','2eeb3b30c9fd3090605c6c39c681e4d0d0b18a2e',(
  'kaleidoscope_grilling:sichuan_pepper','minecraft:honey_bottle','kaleidoscope_grilling:pepper_honey'
 )),
 'wok_houttuynia':('common/src/main/resources/data/kaleidoscope_grilling/recipe/pot/houttuynia_stir_fried_pork.json','31676dd8c13331aec31560df1028f21aeb77feef',(
  'kaleidoscope_cookery:pot','minecraft:porkchop','kaleidoscope_grilling:houttuynia_stir_fried_pork'
 )),
 'wok_squid':('common/src/main/resources/data/kaleidoscope_grilling/recipe/pot/green_pepper_squid_tentacles.json','4b7a16790f96ba00e112d3ce94c1492263d703a0',(
  'kaleidoscope_cookery:green_chili','ingredients/squid_tentacles','ingredients/onions'
 )),
 'wok_wings':('common/src/main/resources/data/kaleidoscope_grilling/recipe/pot/braised_chicken_wings.json','3a07fd7c9c9252db9134043b2438e10c46089d0c',(
  'ingredients/chicken_wings','minecraft:sugar','kaleidoscope_grilling:braised_chicken_wings'
 )),
 'stockpot_beef':('common/src/main/resources/data/kaleidoscope_grilling/recipe/stockpot/potato_beef_stew.json','7596270b1a876561e70fec6afa8966d3be08c9be',(
  'kaleidoscope_cookery:stockpot','ingredients/beef_chunks','minecraft:potato','ingredients/carrot_dice','ingredients/onions'
 )),
 'stockpot_porridge':('common/src/main/resources/data/kaleidoscope_grilling/recipe/stockpot/red_sweet_potato_porridge.json','b8fed24b8ea41e93fdcb4611dbb61a0b12301c4c',(
  'ingredients/sweet_potatoes','kaleidoscope_cookery:rice','kaleidoscope_grilling:red_sweet_potato_porridge'
 )),
 'stockpot_noodles':('common/src/main/resources/data/kaleidoscope_grilling/recipe/stockpot/sour_spicy_noodles.json','0726d66b1e7a004826eb108dc078ef0f3a490361',(
  'kaleidoscope_tavern:vinegar','kaleidoscope_cookery:red_chili','raw_sweet_potato_sheet','ingredients/leafy_greens'
 )),
 'flex_beef':('common/src/main/resources/data/kaleidoscope_grilling/recipe/flex_stockpot/potato_beef_stew.json','30bf95328b2648c9e4c2d3e9f22352c6966f5c1d',('kaleidoscope_cookery:flex_stockpot','soup_base')),
 'flex_porridge':('common/src/main/resources/data/kaleidoscope_grilling/recipe/flex_stockpot/red_sweet_potato_porridge.json','7329e081c912aaa32cd3d84e50994eff471cdb2b',('kaleidoscope_cookery:flex_stockpot','soup_base')),
 'flex_noodles':('common/src/main/resources/data/kaleidoscope_grilling/recipe/flex_stockpot/sour_spicy_noodles.json','4a6693123f50e07b078d858c23b3a7dba84956f9',('kaleidoscope_cookery:flex_stockpot','soup_base')),
}
def git_blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def main():
 for name,(path,expected,tokens) in FILES.items():
  req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.45-contract/1'})
  with urllib.request.urlopen(req,timeout=90) as r:data=r.read()
  actual=git_blob(data);assert actual==expected,(name,actual,expected)
  s=data.decode('utf-8')
  for token in tokens:assert token in s,(name,token)
 print('A2.7.45 pinned Java P0 cuisine contract: PASS')
if __name__=='__main__':main()
