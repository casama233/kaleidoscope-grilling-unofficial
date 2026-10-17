from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
GUIDE=ROOT/'projects/grilling/integration/cookery106';BP=GUIDE/'behavior_pack';RP=GUIDE/'resource_pack'
GAME=ROOT/'projects/grilling/gameplay_core';CONTENT=ROOT/'projects/grilling/guide/content.json'
VERSION=[0,1,14];PAYLOAD_VERSION='0.1.14';REVISION='a1_14_0'

HOW_NAMES={
 'zh_CN':{'guide_grill':'烧烤架','guide_threading':'手工穿串','guide_plate':'串盘与保存','guide_crops':'作物与加工','guide_oil':'榨油器与大缸','guide_recipe_book':'串谱与快速制作'},
 'zh_TW':{'guide_grill':'燒烤架','guide_threading':'手工穿串','guide_plate':'串盤與保存','guide_crops':'作物與加工','guide_oil':'榨油器與大缸','guide_recipe_book':'串譜與快速製作'},
 'en_US':{'guide_grill':'Grill','guide_threading':'Hand threading','guide_plate':'Skewer plate & storage','guide_crops':'Crops & processing','guide_oil':'Oil press & large vat','guide_recipe_book':'Skewer recipe book'},
}
SEASON_NAMES={
 'zh_CN':{'base':'特制调料基础','redstone':'红石','gunpowder':'火药','houttuynia':'折耳根粉','totem':'不死图腾粉','dragon':'龙蛋粉','pepper':'花椒'},
 'zh_TW':{'base':'特製調料基礎','redstone':'紅石','gunpowder':'火藥','houttuynia':'折耳根粉','totem':'不死圖騰粉','dragon':'龍蛋粉','pepper':'花椒'},
 'en_US':{'base':'Special seasoning basics','redstone':'Redstone','gunpowder':'Gunpowder','houttuynia':'Houttuynia Powder','totem':'Totem Powder','dragon':'Dragon Egg Powder','pepper':'Sichuan Pepper'},
}
UI_TEXT={
 'zh_CN':{'title':'森罗物语：烟火','intro':'烧烤、穿串、调料、作物与油料的玩法指南。','all':'全部条目','select':'选择一个主题。','back':'返回','language_note':'语言会跟随森罗物语指南设置。','how_to':'玩法与取得方式','recipes':'烤串食谱','seasonings':'调料与效果'},
 'zh_TW':{'title':'森羅物語：煙火','intro':'燒烤、穿串、調料、作物與油料的玩法指南。','all':'全部條目','select':'選擇一個主題。','back':'返回','language_note':'語言會跟隨森羅物語指南設定。','how_to':'玩法與取得方式','recipes':'烤串食譜','seasonings':'調料與效果'},
 'en_US':{'title':'Kaleidoscope Grilling','intro':'Guide to grilling, threading skewers, seasonings, crops, and oils.','all':'All entries','select':'Choose a topic.','back':'Back','language_note':'Language follows the Kaleidoscope Cookery guide setting.','how_to':'Getting started','recipes':'Skewer recipes','seasonings':'Seasonings & effects'},
}
BODY={
 'guide_grill':{
  'zh_CN':['烧烤架一次最多放 3 串。先点火，再放入生串。','刷油后翻面 4 次；需要调料时，在出炉前撒上特制调料。','烤好后及时取出；继续加热会过熟，最后会烧成木炭。'],
  'zh_TW':['燒烤架一次最多放 3 串。先點火，再放入生串。','刷油後翻面 4 次；需要調料時，在出爐前撒上特製調料。','烤好後及時取出；繼續加熱會過熟，最後會燒成木炭。'],
  'en_US':['A grill holds up to 3 skewers. Light it first, then insert raw skewers.','Brush with oil and flip 4 times. Add special seasoning before taking the skewer out.','Remove cooked skewers in time; continued heating overcooks them and eventually burns them into charcoal.']},
 'guide_threading':{
  'zh_CN':['副手拿木棍或未完成烤串，主手拿可穿串食材，使用即可逐份穿入。','每串最多 3 份食材；固定组合会完成对应生串，否则可做成秘制烤串。','潜行时可拆解尚未烤熟的手工串，取回食材与木棍。'],
  'zh_TW':['副手拿木棍或未完成烤串，主手拿可穿串食材，使用即可逐份穿入。','每串最多 3 份食材；固定組合會完成對應生串，否則可做成秘製烤串。','潛行時可拆解尚未烤熟的手工串，取回食材與木棍。'],
  'en_US':['Hold a stick or unfinished skewer in the off hand and a skewerable ingredient in the main hand, then use it to thread one ingredient at a time.','A skewer holds up to 3 ingredients. Fixed combinations become their matching raw skewer; other combinations can become a Secret Mix Skewer.','Sneak to disassemble an uncooked handmade skewer and recover its ingredients and stick.']},
 'guide_plate':{
  'zh_CN':['烤串盘最多收纳 5 串。手持烤串对盘使用可放入，空手使用会取回最后放入的一串。','手持有内容的盘子潜行放置，可把整盘摆到实心方块或森罗物语桌子上。','直接食用盘子时会先吃掉盘中饱食度最高的一串。'],
  'zh_TW':['烤串盤最多收納 5 串。手持烤串對盤使用可放入，空手使用會取回最後放入的一串。','手持有內容的盤子潛行放置，可把整盤擺到實心方塊或森羅物語桌子上。','直接食用盤子時會先吃掉盤中飽食度最高的一串。'],
  'en_US':['A skewer plate stores up to 5 skewers. Use a skewer on the plate to add it; use an empty hand to take back the last skewer.','Sneak-place a non-empty plate on a solid block or Kaleidoscope Cookery table.','Eating from the plate consumes the skewer with the highest nutrition first.']},
 'guide_crops':{
  'zh_CN':['可种植并采收油菜、折耳根、洋葱与红薯；成熟作物可继续进入加工链。','油菜可制油饼并榨成菜籽油；折耳根、洋葱与红薯可继续切碎、研磨或烹调。','Cookery 的红辣椒可用磨石加工成红辣椒粉，再用于制作辣椒油。'],
  'zh_TW':['可種植並採收油菜、折耳根、洋蔥與番薯；成熟作物可繼續進入加工鏈。','油菜可製油餅並榨成菜籽油；折耳根、洋蔥與番薯可繼續切碎、研磨或烹調。','Cookery 的紅辣椒可用磨石加工成紅辣椒粉，再用於製作辣椒油。'],
  'en_US':['Canola, Houttuynia, Onion, and Sweet Potato can be planted and harvested, then processed further.','Canola becomes oil cake and canola oil; Houttuynia, Onion, and Sweet Potato feed into chopping, milling, or cooking chains.','Cookery Red Chili can be milled into Red Chili Powder and then used for Chili Oil.']},
 'guide_oil':{
  'zh_CN':['榨油器最多放 4 个油饼。装满后用铁砧或可压榨石反复敲击，完成后输出菜籽油与油渣。','附近有可接收的大缸时，菜籽油会优先灌入大缸；大缸容量为 8 桶且一次只保存一种流体。','大缸可保存水、熔岩与三种烟火油，也能把烟火油直接灌入 Cookery 油壶。'],
  'zh_TW':['榨油器最多放 4 個油餅。裝滿後用鐵砧或可壓榨石反覆敲擊，完成後輸出菜籽油與油渣。','附近有可接收的大缸時，菜籽油會優先灌入大缸；大缸容量為 8 桶且一次只保存一種流體。','大缸可保存水、熔岩與三種煙火油，也能把煙火油直接灌入 Cookery 油壺。'],
  'en_US':['The oil press holds up to 4 oil cakes. Fill it, then strike it repeatedly with an anvil or valid press stone to produce canola oil and oil residue.','If a compatible large vat is nearby, canola oil is deposited there first. A vat holds 8 buckets and stores one fluid type at a time.','The vat stores water, lava, and the three Grilling oils, and can fill Cookery oil pots directly.']},
 'guide_recipe_book':{
  'zh_CN':['主手拿空串谱、副手拿完整生串，使用即可记录该配方；生串不会被消耗。','已记录的串谱配合副手木棍使用，会从背包按配方取料并自动制作。','已记录的串谱也可贴到方块侧面；拿木棍对墙上的串谱使用即可快速制作。'],
  'zh_TW':['主手拿空串譜、副手拿完整生串，使用即可記錄該配方；生串不會被消耗。','已記錄的串譜配合副手木棍使用，會從背包按配方取料並自動製作。','已記錄的串譜也可貼到方塊側面；拿木棍對牆上的串譜使用即可快速製作。'],
  'en_US':['Hold an empty Skewer Recipe Book in the main hand and a complete raw skewer in the off hand, then use it to record the recipe without consuming the skewer.','Use a recorded book with a stick in the off hand to pull ingredients from inventory and craft automatically.','A recorded book can also be placed on a block side; use a stick on the placed recipe for quick crafting.']},
}
SEASON_BODY={
 'base':{
  'zh_CN':['特制调料的基础三料是绿辣椒粉、花椒与洋葱粉；三种都放入后才能摇匀完成。','调料瓶最多记录 8 份材料，完成后可使用 16 次。'],
  'zh_TW':['特製調料的基礎三料是青辣椒粉、花椒與洋蔥粉；三種都放入後才能搖勻完成。','調料瓶最多記錄 8 份材料，完成後可使用 16 次。'],
  'en_US':['The three base ingredients are Green Chili Powder, Sichuan Pepper, and Onion Powder. All three are required before shaking the seasoning complete.','A seasoning bottle stores up to 8 ingredients and has 16 uses when finished.']},
 'redstone':{'zh_CN':['红石提供速度效果；堆叠更多同种材料时强度会提升。'],'zh_TW':['紅石提供速度效果；堆疊更多同種材料時強度會提升。'],'en_US':['Redstone grants Speed; using more of the same ingredient increases the effect strength.']},
 'gunpowder':{'zh_CN':['火药提供力量效果；堆叠更多同种材料时强度会提升。'],'zh_TW':['火藥提供力量效果；堆疊更多同種材料時強度會提升。'],'en_US':['Gunpowder grants Strength; using more of the same ingredient increases the effect strength.']},
 'houttuynia':{'zh_CN':['折耳根粉用于延长调料效果时间；加入 1 份会延长，加入 4 份以上时延长幅度更高。'],'zh_TW':['折耳根粉用於延長調料效果時間；加入 1 份會延長，加入 4 份以上時延長幅度更高。'],'en_US':['Houttuynia Powder extends seasoning-effect duration; 4 or more gives the stronger duration extension.']},
 'totem':{'zh_CN':['不死图腾粉提供一次重金属保命效果；受到致命伤时可保住生命，之后会进入重金属中毒状态。'],'zh_TW':['不死圖騰粉提供一次重金屬保命效果；受到致命傷時可保住生命，之後會進入重金屬中毒狀態。'],'en_US':['Totem Powder provides a heavy-metal survival effect that can prevent one lethal hit, followed by heavy-metal poisoning.']},
 'dragon':{'zh_CN':['龙蛋粉提供龙血效果，提高生命上限并提供额外伤害吸收。'],'zh_TW':['龍蛋粉提供龍血效果，提高生命上限並提供額外傷害吸收。'],'en_US':['Dragon Egg Powder grants Dragon Blood, increasing maximum health and providing extra damage absorption.']},
 'pepper':{'zh_CN':['花椒也是基础三料之一；花椒累计到 4 份以上时，趁热食用会触发麻木效果。'],'zh_TW':['花椒也是基礎三料之一；花椒累積到 4 份以上時，趁熱食用會觸發麻木效果。'],'en_US':['Sichuan Pepper is also one of the three base ingredients; 4 or more triggers Numbness when the seasoned skewer is eaten hot.']},
}
EN_ING={
 'ingredients/beef_chunks':'Beef Chunks','red_chili':'Red Chili','raw_pork_belly':'Raw Pork Belly','green_chili':'Green Chili',
 'ingredients/chicken_skin':'Chicken Skin','ingredients/chicken_wings':'Chicken Wing','ingredients/squid_tentacles':'Squid Tentacle',
 'cod':'Cod','salmon':'Salmon','tropical_fish':'Tropical Fish','pufferfish':'Pufferfish',
 'ingredients/raw_sweet_potato_sheets':'Raw Sweet Potato Sheet','ingredients/minced_houttuynia':'Minced Houttuynia',
 'ingredients/potato_slices':'Potato Slice','caterpillar':'Caterpillar','brown_mushroom':'Brown Mushroom','red_mushroom':'Red Mushroom',
 'ingredients/carrot_dice':'Carrot Dice','ingredients/raw_mantou_slices':'Raw Mantou Slice','ender_pearl':'Ender Pearl','beetroot':'Beetroot',
 'raw_meatball':'Raw Meatball','slime_ball':'Slimeball','ingredients/houttuynia':'Houttuynia','raw_cut_small_meats':'Raw Cut Meat',
 'bone':'Bone','fried_egg':'Fried Egg','raw_dough':'Raw Dough','raw_lamb_chops':'Raw Lamb Chop','oil':'Oil',
 'golden_apple':'Golden Apple','totem_of_undying':'Totem of Undying','golden_carrot':'Golden Carrot','poisonous_potato':'Poisonous Potato','spider_eye':'Spider Eye'
}
TR_TO_CN=str.maketrans({'燒':'烧','點':'点','後':'后','調':'调','製':'制','會':'会','過':'过','繼':'继','續':'续','與':'与','盤':'盘','實':'实','塊':'块','紅':'红','魚':'鱼','魷':'鱿','鬚':'须','雞':'鸡','蘿':'萝','蔔':'卜','饅':'馒','圖':'图','騰':'腾','麵':'面','黃':'黄','薯':'薯','馬':'马','鈴':'铃','豬':'猪','兒':'儿','蟲':'虫','蘋':'苹','選':'选','擇':'择','順':'顺','類':'类','個':'个','種':'种','為':'为','進':'进','時':'时','間':'间','滿':'满','記':'记','錄':'录','牆':'墙','書':'书','從':'从','壺':'壶','儲':'储','態':'态','層':'层','疊':'叠','傷':'伤','龍':'龙','額':'额','開':'开','關':'关','將':'将','產':'产','區':'区','對':'对','應':'应','顯':'显','條':'条','數':'数','樣':'样','壓':'压','鐵':'铁','砧':'砧','輸':'输','體':'体','爐':'炉','鍋':'锅','湯':'汤','這':'这','裡':'里','復':'复','氣':'气','設':'设','語':'语','簡':'简','讓':'让','隻':'只','餘':'余','餅':'饼','搖':'摇','勻':'匀','礎':'础','堆':'堆','積':'积','觸':'触','發':'发','屬':'属','強':'强','長':'长'})
CN_WORD={'馬鈴薯':'土豆','番薯':'红薯','不死圖騰':'不死图腾'}

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write_json(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def read_lang(p):
 out={}
 for line in p.read_text(encoding='utf-8-sig').splitlines():
  if '=' in line:
   k,v=line.split('=',1);out[k]=v
 return out
def write_lang(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text('\n'.join(f'{k}={v}' for k,v in d.items())+'\n',encoding='utf-8')
def tw_to_cn(s):
 for a,b in CN_WORD.items():s=s.replace(a,b)
 return s.translate(TR_TO_CN)
def clean_label(s):return str(s).replace('（來源標籤）','').replace('（来源标签）','').strip()
def selector_key(x):
 s=x.get('java_selector','').split(':')[-1].lstrip('#')
 return s

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name,desc in ((bm,'Grilling Guide A1.14 — LOCALIZED GUIDE BP','Localized Grilling chapter for the existing Cookery 1.0.6 guidebook.'),(rm,'Grilling Guide A1.14 — LOCALIZED GUIDE RP','Language source files and guide icons for the existing Cookery 1.0.6 guidebook.')):
  doc['header']['version']=VERSION;doc['header']['name']=name;doc['header']['description']=desc
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write_json(BP/'manifest.json',bm);write_json(RP/'manifest.json',rm)
 cfg=load(GUIDE/'config.json');cfg['name']='Grilling Guide — Cookery 1.0.6 localized A1.14';cfg['description']='Localized Grilling entry inside the existing Cookery guidebook; no extra physical guidebook.';cfg['compiler']['plugins'][0][1]['packName']='KG_Grilling_Guide_A114_Localized';write_json(GUIDE/'config.json',cfg)

def game_langs():
 return {loc:read_lang(GAME/f'resource_pack/texts/{loc}.lang') for loc in ('zh_CN','zh_TW','en_US')}

def recipe_name(glang,loc,result):
 key='item.'+result.replace(':',':')+'.name'
 # Bedrock language keys use item.kaleidoscope_grilling:path.name
 key=f"item.{result.split(':')[0]}:{result.split(':')[1]}.name"
 name=glang[loc].get(key,result.split(':')[-1])
 if loc=='en_US' and name.startswith('Raw '):name=name[4:]
 if loc in ('zh_CN','zh_TW') and name.startswith('生'):name=name[1:]
 return name

def recipe_body(row):
 tw=[];cn=[];en=[]
 for slot in row['slots']:
  twalts=[clean_label(x['label']) for x in slot['alternatives']]
  cn_alts=[tw_to_cn(x) for x in twalts]
  en_alts=[]
  for x in slot['alternatives']:
   k=selector_key(x);en_alts.append(EN_ING.get(k,k.replace('_',' ').title()))
  tw.append(' / '.join(twalts));cn.append(' / '.join(cn_alts));en.append(' / '.join(en_alts))
 cooked=bool(row.get('source_cooked_result'))
 return {
  'zh_TW':['材料順序：'+' → '.join(tw), '穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。' if cooked else '這是特殊烤串，沒有另外的生／熟轉換。'],
  'zh_CN':['材料顺序：'+' → '.join(cn), '穿好后放上烧烤架，依刷油、翻面与调味流程烤熟。' if cooked else '这是特殊烤串，没有另外的生／熟转换。'],
  'en_US':['Ingredient order: '+' → '.join(en), 'Put the finished raw skewer on the grill, then oil, flip, and season it until cooked.' if cooked else 'This special skewer has no separate raw-to-cooked conversion.'],
 }

def build():
 glang=game_langs();src=load(CONTENT)
 names={loc:{} for loc in UI_TEXT};mechanics={}
 icons={}
 for slug in HOW_NAMES['zh_CN']:
  id_=f'kg_a1:{slug}';icons[id_]=f"textures/ui/kg_grilling/{slug}"
  for loc in names:names[loc][id_]=HOW_NAMES[loc][slug]
  mechanics[id_]=BODY[slug]
 for row in src['recipes']:
  id_=f"kg_a1:guide_recipe_{row['id']}";preview=row.get('cooked_preview_image') or row.get('preview_image') or 'ordinary_full';icons[id_]=f'textures/ui/kg_grilling/{preview}'
  for loc in names:names[loc][id_]=recipe_name(glang,loc,row['source_recipe_id'])
  mechanics[id_]=recipe_body(row)
 for slug in SEASON_NAMES['zh_CN']:
  id_=f'kg_a1:guide_seasoning_{slug}';icons[id_]=('textures/ui/kg_grilling/guide_seasoning' if slug=='base' else 'textures/items/redstone_dust' if slug=='redstone' else 'textures/items/gunpowder' if slug=='gunpowder' else f'textures/ui/kg_grilling/guide_{"sichuan_pepper" if slug=="pepper" else slug+"_powder"}')
  for loc in names:names[loc][id_]=SEASON_NAMES[loc][slug]
  mechanics[id_]=SEASON_BODY[slug]
 # Normal RP language files are the source of truth for all labels and entry names.
 for loc in UI_TEXT:
  rows={f'guide.kg.{k}':v for k,v in UI_TEXT[loc].items()}
  rows.update({f'guide.kg.name.{id_.split(":")[1]}':v for id_,v in names[loc].items()})
  write_lang(RP/f'texts/{loc}.lang',rows)
 write_json(RP/'texts/languages.json',['zh_CN','zh_TW','en_US'])

 entries=[]
 order=[*[(f'kg_a1:{x}','how_to') for x in HOW_NAMES['zh_CN']],*[(f"kg_a1:guide_recipe_{r['id']}",'recipes') for r in src['recipes']],*[(f'kg_a1:guide_seasoning_{x}','seasonings') for x in SEASON_NAMES['zh_CN']]]
 for id_,cat in order:
  entries.append({'id':id_,'category':cat,'icon':icons[id_],'kinds':[],'mechanics':mechanics[id_]['zh_TW']})
 payload={'api':1,'id':'kg_a1:grilling','version':PAYLOAD_VERSION,'order':300,'icon':'textures/ui/kg_grilling/guide_grill','titleKey':'title','introKey':'intro','allKey':'all','selectKey':'select','backKey':'back','languageNoteKey':'language_note','showAll':False,'showIds':False,'showKinds':False,'showCategoryOnEntry':False,
  'categories':[{'id':'how_to','labelKey':'how_to','fallback':'Getting started','icon':'textures/ui/kg_grilling/guide_grill'},{'id':'recipes','labelKey':'recipes','fallback':'Skewer recipes','icon':'textures/ui/kg_grilling/guide_recipe_book'},{'id':'seasonings','labelKey':'seasonings','fallback':'Seasonings & effects','icon':'textures/ui/kg_grilling/guide_seasoning'}],
  'entries':entries,'names':names,'text':UI_TEXT}
 return payload,mechanics,names

def write_payload(payload):
 (BP/'scripts/payload.js').write_text('// Generated A1.14 localized Cookery guide extension.\nexport const GUIDE_PAYLOAD = '+json.dumps(payload,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
 pub=BP/'scripts/publisher.js';s=pub.read_text(encoding='utf-8');s=s.replace("export const REVISION = 'a1_13_0';",f"export const REVISION = '{REVISION}';");pub.write_text(s,encoding='utf-8')

def main():
 if load(BP/'manifest.json')['header']['version']!=[0,1,13]:raise RuntimeError('A1.14 must augment A1.13')
 patch_versions();payload,mechanics,names=build();write_payload(payload)
 write_json(GUIDE/'a114-localized-mechanics.json',{'schema':1,'locales':['zh_CN','zh_TW','en_US'],'entries':mechanics})
 write_json(GUIDE/'a114-localization-report.json',{'version':'A1.14','language_files':['zh_CN','zh_TW','en_US'],'entry_count':len(payload['entries']),'localized_name_count':{k:len(v) for k,v in names.items()},'localized_mechanics_catalog_entries':len(mechanics),'runtime_labels_follow_host_language':True,'runtime_body_locale_switch_on_stock_cookery_1_0_6':False,'reason':'Cookery 1.0.6 Guidebook Extension API v1 rejects standard locale keys in mechanicsByLocale while its UI reads standard locale keys. A per-player body switch cannot be implemented safely from an extension pack without modifying the host.','fallback_body_locale':'zh_TW','standalone_book_item':False,'host_modified':False,'minecraft_tested':False})
 print('A1.14 localized guide source complete')
if __name__=='__main__':main()
