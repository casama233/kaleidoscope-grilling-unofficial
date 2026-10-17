from __future__ import annotations
import hashlib,json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
GUIDE=ROOT/'projects/grilling/integration/cookery106'
BP=GUIDE/'behavior_pack';RP=GUIDE/'resource_pack'
GAME=ROOT/'projects/grilling/gameplay_core'
CONTENT=ROOT/'projects/grilling/guide/content.json'
VERSION=[0,1,13]
PAYLOAD_VERSION='0.1.13'
REVISION='a1_13_0'
UI=RP/'textures/ui/kg_grilling'

ICON_SOURCES={
 'guide_grill':'blocks/grill.png',
 'guide_plate':'items/skewer_plate.png',
 'guide_crops':'items/canola_seeds.png',
 'guide_threading':'items/raw_beef_skewer.png',
 'guide_oil':'blocks/oil_press.png',
 'guide_recipe_book':'items/skewer_recipe_book.png',
 'guide_seasoning':'items/special_seasoning.png',
 'guide_houttuynia_powder':'items/houttuynia_powder.png',
 'guide_totem_powder':'items/totem_powder.png',
 'guide_dragon_egg_powder':'items/dragon_egg_powder.png',
 'guide_sichuan_pepper':'items/sichuan_pepper.png',
}

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write_json(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha256(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def read_lang(path):
 out={}
 for line in path.read_text(encoding='utf-8').splitlines():
  if '=' not in line:continue
  k,v=line.split('=',1);out[k]=v
 return out

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name,desc in (
  (bm,'Grilling Guide A1.13 — PLAYER GUIDE BP','Adds the player-facing Kaleidoscope Grilling chapter to the existing Cookery 1.0.6 guidebook.'),
  (rm,'Grilling Guide A1.13 — PLAYER GUIDE RP','Player-facing Grilling guide icons for the existing Cookery 1.0.6 guidebook.'),
 ):
  doc['header']['version']=VERSION;doc['header']['name']=name;doc['header']['description']=desc
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write_json(BP/'manifest.json',bm);write_json(RP/'manifest.json',rm)
 cfg=load(GUIDE/'config.json')
 cfg['name']='Grilling Guide — Cookery 1.0.6 player guide A1.13'
 cfg['description']='One player-facing Grilling entry inside the existing Cookery guidebook; no extra physical guidebook.'
 cfg['compiler']['plugins'][0][1]['packName']='KG_Grilling_Guide_A113'
 write_json(GUIDE/'config.json',cfg)

def copy_icons():
 UI.mkdir(parents=True,exist_ok=True)
 result={}
 base=GAME/'resource_pack/textures'
 for name,rel in ICON_SOURCES.items():
  src=base/rel
  if not src.is_file():raise RuntimeError('missing guide icon source '+str(src))
  dst=UI/f'{name}.png';shutil.copy2(src,dst)
  result[name]={'source':str(src.relative_to(ROOT)).replace('\\','/'),'sha256':sha256(dst)}
 return result

def item_name(lang,id_):
 path=id_.split(':',1)[1]
 key=f'item.kaleidoscope_grilling:{path}.name'
 v=lang.get(key)
 if not v:raise RuntimeError('missing localized Grilling item name '+key)
 return v

def short_recipe_name(label,locale):
 if locale=='en_US':
  return label[4:] if label.startswith('Raw ') else label
 return label[1:] if label.startswith('生') else label

def clean_slot_label(v):
 return str(v).replace('（來源標籤）','').replace('（来源标签）','').strip()

def recipe_lines(row):
 groups=[]
 for slot in row['slots']:
  alts=[clean_slot_label(x['label']) for x in slot['alternatives']]
  groups.append(' / '.join(alts))
 line='材料順序：'+' → '.join(groups)
 if row.get('source_cooked_result'):
  return [line,'穿好後放上燒烤架，依刷油、翻面與調味流程烤熟。']
 return [line,'這是特殊烤串，沒有另外的生／熟轉換。']

def build_payload():
 source=load(CONTENT)
 langs={k:read_lang(GAME/f'resource_pack/texts/{k}.lang') for k in ('zh_CN','zh_TW','en_US')}
 icon=lambda n:f'textures/ui/kg_grilling/{n}'
 categories=[
  {'id':'how_to','labelKey':'how_to','fallback':'Getting started','icon':icon('guide_grill')},
  {'id':'recipes','labelKey':'recipes','fallback':'Skewer recipes','icon':icon('guide_recipe_book')},
  {'id':'seasonings','labelKey':'seasonings','fallback':'Seasonings & effects','icon':icon('guide_seasoning')},
 ]
 basics=[
  ('kg_a1:guide_grill','guide_grill',[
   '燒烤架一次最多放 3 串。先點火，再放入生串。',
   '刷油後翻面 4 次；需要調料時，在出爐前把特製調料撒到烤串上。',
   '烤好後要及時取出；放太久會先過熟，繼續加熱最後會燒成木炭。',
  ]),
  ('kg_a1:guide_threading','guide_threading',[
   '副手拿木棍或未完成烤串，主手拿可穿串的食材，使用即可逐份穿入。',
   '每串最多 3 份食材；符合固定配方時會完成對應生串，否則可做成秘製烤串。',
   '潛行時可拆解尚未烤熟的手工串，取回食材與木棍。',
  ]),
  ('kg_a1:guide_plate','guide_plate',[
   '烤串盤最多收納 5 串。手持烤串對盤使用可放入，空手使用會取回最後放入的一串。',
   '手持有內容的盤子潛行放置，可把整盤擺到實心方塊或森羅物語桌子上。',
   '直接食用盤子時會先吃掉盤中飽食度最高的一串；剩餘內容會繼續保存在盤中。',
  ]),
  ('kg_a1:guide_crops','guide_crops',[
   '目前可種植並採收油菜、魚腥草、洋蔥與紅薯；成熟作物可接到各自加工鏈。',
   '油菜可製油餅並榨成菜籽油；魚腥草、洋蔥與紅薯可繼續切碎、研磨或烹調。',
   'Cookery 的紅辣椒可用磨石加工成紅辣椒粉，再用於製作辣椒油。',
  ]),
  ('kg_a1:guide_oil','guide_oil',[
   '榨油器最多放 4 個油餅。裝滿後用鐵砧或可壓榨石反覆敲擊，進度完成會輸出菜籽油與油渣。',
   '附近有可接收的大缸時，菜籽油會優先灌入大缸；大缸容量為 8 桶，同一時間只保存一種流體。',
   '大缸可保存水、熔岩與三種煙火油，也能把煙火油直接灌入 Cookery 油壺。',
  ]),
  ('kg_a1:guide_recipe_book','guide_recipe_book',[
   '主手拿空串譜、副手拿完整生串，使用即可記錄該串配方；被記錄的生串不會被消耗。',
   '已記錄的串譜配合副手木棍使用，會從背包按配方取料並自動製作。',
   '已記錄的串譜還可以貼到方塊側面；拿木棍對牆上的串譜使用也能快速製作。',
  ]),
 ]
 entries=[{'id':id_,'category':'how_to','icon':icon(ic),'kinds':[],'mechanics':m} for id_,ic,m in basics]

 for row in source['recipes']:
  rid=row['id'];preview=row.get('cooked_preview_image') or row.get('preview_image') or 'ordinary_full'
  entries.append({
   'id':f'kg_a1:guide_recipe_{rid}','category':'recipes',
   'icon':f'textures/ui/kg_grilling/{preview}','kinds':[],'mechanics':recipe_lines(row)
  })

 season_entries=[
  ('kg_a1:guide_seasoning_base','guide_seasoning',[
   '特製調料的基礎三料是青辣椒粉、花椒與洋蔥粉；三種都放入後才能搖勻完成。',
   '調料瓶最多記錄 8 份材料，完成後可使用 16 次；不同附加材料會改變趁熱食用時得到的效果。',
  ]),
  ('kg_a1:guide_seasoning_redstone',None,['紅石提供速度效果；同種材料堆得更多時，效果強度會提升。']),
  ('kg_a1:guide_seasoning_gunpowder',None,['火藥提供力量效果；同種材料堆得更多時，效果強度會提升。']),
  ('kg_a1:guide_seasoning_houttuynia','guide_houttuynia_powder',['魚腥草粉用來延長調料效果時間；加入 1 份會延長，加入 4 份以上時延長幅度更高。']),
  ('kg_a1:guide_seasoning_totem','guide_totem_powder',['圖騰粉提供一次重金屬保命效果；受到致命傷時可保住生命，之後會進入重金屬中毒狀態。']),
  ('kg_a1:guide_seasoning_dragon','guide_dragon_egg_powder',['龍蛋粉提供龍血效果，提高生命上限並提供額外傷害吸收。']),
  ('kg_a1:guide_seasoning_pepper','guide_sichuan_pepper',['花椒同時是基礎三料之一；花椒累積到 4 份以上時，趁熱食用會觸發麻木效果。']),
 ]
 for id_,ic,m in season_entries:
  if ic is None:
   path='textures/items/redstone_dust' if id_.endswith('redstone') else 'textures/items/gunpowder'
  else:path=icon(ic)
  entries.append({'id':id_,'category':'seasonings','icon':path,'kinds':[],'mechanics':m})

 manual_names={
  'zh_CN':{
   'kg_a1:guide_grill':'烧烤架','kg_a1:guide_threading':'手工穿串','kg_a1:guide_plate':'串盘与保存',
   'kg_a1:guide_crops':'作物与加工','kg_a1:guide_oil':'榨油器与大缸','kg_a1:guide_recipe_book':'串谱与快速制作',
   'kg_a1:guide_seasoning_base':'特制调料基础','kg_a1:guide_seasoning_redstone':'红石',
   'kg_a1:guide_seasoning_gunpowder':'火药','kg_a1:guide_seasoning_houttuynia':'鱼腥草粉',
   'kg_a1:guide_seasoning_totem':'图腾粉','kg_a1:guide_seasoning_dragon':'龙蛋粉','kg_a1:guide_seasoning_pepper':'花椒',
  },
  'zh_TW':{
   'kg_a1:guide_grill':'燒烤架','kg_a1:guide_threading':'手工穿串','kg_a1:guide_plate':'串盤與保存',
   'kg_a1:guide_crops':'作物與加工','kg_a1:guide_oil':'榨油器與大缸','kg_a1:guide_recipe_book':'串譜與快速製作',
   'kg_a1:guide_seasoning_base':'特製調料基礎','kg_a1:guide_seasoning_redstone':'紅石',
   'kg_a1:guide_seasoning_gunpowder':'火藥','kg_a1:guide_seasoning_houttuynia':'魚腥草粉',
   'kg_a1:guide_seasoning_totem':'圖騰粉','kg_a1:guide_seasoning_dragon':'龍蛋粉','kg_a1:guide_seasoning_pepper':'花椒',
  },
  'en_US':{
   'kg_a1:guide_grill':'Grill','kg_a1:guide_threading':'Hand threading','kg_a1:guide_plate':'Skewer plate & storage',
   'kg_a1:guide_crops':'Crops & processing','kg_a1:guide_oil':'Oil press & large vat','kg_a1:guide_recipe_book':'Skewer recipe book',
   'kg_a1:guide_seasoning_base':'Special seasoning basics','kg_a1:guide_seasoning_redstone':'Redstone',
   'kg_a1:guide_seasoning_gunpowder':'Gunpowder','kg_a1:guide_seasoning_houttuynia':'Houttuynia Powder',
   'kg_a1:guide_seasoning_totem':'Totem Powder','kg_a1:guide_seasoning_dragon':'Dragon Egg Powder','kg_a1:guide_seasoning_pepper':'Sichuan Pepper',
  },
 }
 names={loc:dict(rows) for loc,rows in manual_names.items()}
 for row in source['recipes']:
  id_=f"kg_a1:guide_recipe_{row['id']}"
  result=row['source_recipe_id']
  for loc in names:
   names[loc][id_]=short_recipe_name(item_name(langs[loc],result),loc)

 text={
  'zh_CN':{
   'title':'森罗物语：烟火','intro':'烧烤、穿串、调料、作物与油料的玩法指南。',
   'all':'全部条目','select':'选择一个主题。','back':'返回',
   'language_note':'不同烤串、油料与调料会有不同效果。',
   'how_to':'玩法与取得方式','recipes':'烤串食谱','seasonings':'调料与效果',
  },
  'zh_TW':{
   'title':'森羅物語：煙火','intro':'燒烤、穿串、調料、作物與油料的玩法指南。',
   'all':'全部條目','select':'選擇一個主題。','back':'返回',
   'language_note':'不同烤串、油料與調料會有不同效果。',
   'how_to':'玩法與取得方式','recipes':'烤串食譜','seasonings':'調料與效果',
  },
  'en_US':{
   'title':'Kaleidoscope Grilling','intro':'Guide to grilling, threading skewers, seasonings, crops, and oils.',
   'all':'All entries','select':'Choose a topic.','back':'Back',
   'language_note':'Different skewers, oils, and seasonings have different effects.',
   'how_to':'Getting started','recipes':'Skewer recipes','seasonings':'Seasonings & effects',
  },
 }
 return {
  'api':1,'id':'kg_a1:grilling','version':PAYLOAD_VERSION,'order':300,
  'icon':icon('guide_grill'),'titleKey':'title','introKey':'intro','allKey':'all','selectKey':'select','backKey':'back',
  'languageNoteKey':'language_note','showAll':False,'showIds':False,'showKinds':False,'showCategoryOnEntry':False,
  'categories':categories,'entries':entries,'names':names,'text':text,
 }

def write_payload(payload):
 body='// Generated A1.13 player-facing Cookery guide extension.\nexport const GUIDE_PAYLOAD = '+json.dumps(payload,ensure_ascii=False,indent=2)+';\n'
 (BP/'scripts/payload.js').write_text(body,encoding='utf-8')
 pub=BP/'scripts/publisher.js';s=pub.read_text(encoding='utf-8')
 s=s.replace("export const REVISION = 'a1_12_0';",f"export const REVISION = '{REVISION}';")
 if f"export const REVISION = '{REVISION}';" not in s:raise RuntimeError('publisher revision patch failed')
 pub.write_text(s,encoding='utf-8')

def write_readme():
 text='''# A1.13 — 森羅物語：煙火 玩家指南\n\n本包只負責把「煙火」作為一個章節接入 Cookery 1.0.6 原有指南，不新增第二本指南書。\n\nA1.13 把早期「素材預覽／來源參考」頁改為玩家實際使用的指南：\n\n- 正式名稱：森羅物語：煙火 / Kaleidoscope Grilling。\n- 三個清楚分類：玩法與取得方式、烤串食譜、調料與效果。\n- 玩法頁使用不同實物圖標，不再所有按鈕重複同一根烤串。\n- 說明改成操作步驟，不再顯示 source id、開發狀態或中英混排的測試文字。\n- 20 組固定串仍依 Java 1.1.1 的順序顯示。\n- 指南內容已更新到目前 Gameplay Core 已完成的串盤、串譜、榨油器、大缸、四種作物與紅辣椒粉加工鏈。\n\nCookery 1.0.6 的 Guidebook Extension API v1 對 mechanics 的 locale 有已知限制，因此正文仍使用單一中文 fallback；分類名、標題與條目名稱會正常跟隨 zh_CN / zh_TW / en_US。\n\n這仍不是 Minecraft/BDS 實機驗收聲明；UI 尺寸、觸控與控制器顯示需要遊戲內再確認。\n'''
 (GUIDE/'README.zh-TW.md').write_text(text,encoding='utf-8')

def report(icon_report,payload):
 write_json(GUIDE/'a113-guide-report.json',{
  'version':'A1.13','payload_version':PAYLOAD_VERSION,'revision':REVISION,
  'title_zh_cn':payload['text']['zh_CN']['title'],'title_zh_tw':payload['text']['zh_TW']['title'],
  'categories':[x['id'] for x in payload['categories']],
  'entry_count':len(payload['entries']),'how_to_entries':sum(x['category']=='how_to' for x in payload['entries']),
  'recipe_entries':sum(x['category']=='recipes' for x in payload['entries']),
  'seasoning_entries':sum(x['category']=='seasonings' for x in payload['entries']),
  'distinct_category_icons':len({x['icon'] for x in payload['categories']}),
  'icon_copies':icon_report,'standalone_book_item':False,'host_modified':False,
  'minecraft_tested':False,'bds_tested':False,
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[0,1,12]:
  raise RuntimeError('A1.13 guide must augment A1.12 guide baseline')
 patch_versions();icons=copy_icons();payload=build_payload();write_payload(payload);write_readme();report(icons,payload)
 print('A1.13 player-facing guide complete')
if __name__=='__main__':main()
