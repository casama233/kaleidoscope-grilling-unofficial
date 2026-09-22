from __future__ import annotations
import hashlib,json,urllib.request

JAVA_COMMIT='9a1acdab27698457bec16c9362678e574895a28c'
JAVA_BASE=f'https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/{JAVA_COMMIT}/'
MS_COMMIT='73a171fc8393a1052b4ca0669dc82231f775d8b1'
MS_BASE=f'https://raw.githubusercontent.com/microsoft/minecraft-scripting-samples/{MS_COMMIT}/'

FEAST=(
 'grilled_beef_skewer','grilled_pork_belly_skewer','grilled_chicken_skin_skewer','grilled_mid_wing_skewer',
 'grilled_squid_tentacle_skewer','grilled_fish_skewer','grilled_sweet_potato_sheet_skewer','grilled_potato_slice_skewer',
 'grilled_caterpillar_skewer','grilled_mushroom_skewer','grilled_bun_slice_skewer','grilled_ender_pearl_skewer',
 'grilled_meatball_skewer','grilled_slime_skewer','grilled_meat_and_bone_skewer','grilled_fried_egg_skewer',
 'grilled_lamb_skewer','grilled_gluten_skewer','grilled_golden_skewer','ordinary_skewer','cold_houttuynia',
 'sugared_tomato','pepper_honey','houttuynia_stir_fried_pork','green_pepper_squid_tentacles',
 'braised_chicken_wings','potato_beef_stew','red_sweet_potato_porridge','sour_spicy_noodles'
)

def git_blob(v:bytes)->str:
 return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def fetch(base,path):
 req=urllib.request.Request(base+path,headers={'User-Agent':'Grilling-A2.7.59-contract/1'})
 with urllib.request.urlopen(req,timeout=90) as r:return r.read()

def verify_blob(base,path,sha):
 data=fetch(base,path);actual=git_blob(data);assert actual==sha,(path,actual,sha);return data

def main():
 mod=verify_blob(
  JAVA_BASE,
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/registry/ModAdvancements.java',
  '2791f158caf5885946d377da0b2a3686dcc89146'
 ).decode('utf-8')
 assert 'private static final String EATEN_KEY = KaleidoscopeGrilling.MOD_ID + ":advancement_foods";' in mod
 assert 'private static final Set<String> FEAST_FOODS' in mod
 for food in FEAST:assert f'"{food}"' in mod,food
 assert len(FEAST)==29 and len(set(FEAST))==29
 assert 'if (FEAST_FOODS.contains(path)) {' in mod
 assert 'Set<String> eaten = readEaten(player);' in mod
 assert 'if (eaten.add(path)) player.getPersistentData().putString(EATEN_KEY, String.join(",", eaten));' in mod
 assert 'if (eaten.containsAll(FEAST_FOODS)) award(player, "fireworks_feast");' in mod

 adv=json.loads(verify_blob(
  JAVA_BASE,
  'common/src/main/resources/data/kaleidoscope_grilling/advancement/fireworks_feast.json',
  '8a1ea9752529f46be2027479cbc325318968df1c'
 ))
 assert adv['parent']=='kaleidoscope_grilling:eat_it_hot'
 assert adv['display']['frame']=='challenge'
 assert adv['display']['hidden'] is False
 assert adv['display']['show_toast'] is True and adv['display']['announce_to_chat'] is True
 assert adv['rewards']['experience']==100

 en=json.loads(verify_blob(
  JAVA_BASE,'common/src/main/resources/assets/kaleidoscope_grilling/lang/en_us.json',
  '807c7f40618d409ca17ccb4c0a39e211a84a7b18'
 ))
 zh=json.loads(verify_blob(
  JAVA_BASE,'common/src/main/resources/assets/kaleidoscope_grilling/lang/zh_cn.json',
  'bbc7465f6bf6ab0c698729e9800fbc3c03ae56db'
 ))
 assert en['advancement.kaleidoscope_grilling.fireworks_feast.title']=='Fireworks Feast'
 assert en['advancement.kaleidoscope_grilling.fireworks_feast.description']=='Eat every fixed cooked skewer, cold dish, and linked meal.'
 assert zh['advancement.kaleidoscope_grilling.fireworks_feast.title']=='烟火全席'
 assert zh['advancement.kaleidoscope_grilling.fireworks_feast.description']=='吃过全部固定熟烤串、凉菜与联动料理。'

 sample=verify_blob(
  MS_BASE,'editor-multi/scripts/goto-mark.ts',
  '833e034c9e04dd920680f4287a66efb008a81449'
 ).decode('utf-8')
 assert 'const me = uiSession.extensionContext.player;' in sample
 assert 'me.setDynamicProperty(storedLocationDynamicPropertyName, JSON.stringify(storage.storedLocations));' in sample
 assert 'me.getDynamicProperty(storedLocationDynamicPropertyName)' in sample

 print('A2.7.59 pinned Java Fireworks Feast + Microsoft player dynamic-property contracts: PASS')
 print('foods:',len(FEAST))
 print('java:',JAVA_COMMIT)
 print('microsoft:',MS_COMMIT)

if __name__=='__main__':main()
