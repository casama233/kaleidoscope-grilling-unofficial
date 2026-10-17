from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
VERSION=[2,7,23]
GROUP_KEY='kaleidoscope_grilling:itemGroup.main'
HIDDEN=(
 'unfinished_skewer','secret_skewer','pending_seasoning','skewer_plate',
 'canola_oil_brush','secret_chili_oil_brush','premium_chili_oil_brush',
)
RAW=(
 'raw_beef_skewer','raw_pork_belly_skewer','raw_chicken_skin_skewer','raw_mid_wing_skewer',
 'raw_squid_tentacle_skewer','raw_fish_skewer','raw_sweet_potato_sheet_skewer',
 'raw_potato_slice_skewer','raw_caterpillar_skewer','raw_mushroom_skewer',
 'raw_bun_slice_skewer','raw_ender_pearl_skewer','raw_meatball_skewer','raw_slime_skewer',
 'raw_meat_and_bone_skewer','raw_fried_egg_skewer','raw_gluten_skewer',
 'raw_lamb_skewer','raw_golden_skewer',
)
COOKED=(
 'grilled_beef_skewer','grilled_pork_belly_skewer','grilled_chicken_skin_skewer',
 'grilled_mid_wing_skewer','grilled_squid_tentacle_skewer','grilled_fish_skewer',
 'grilled_sweet_potato_sheet_skewer','grilled_potato_slice_skewer',
 'grilled_caterpillar_skewer','grilled_mushroom_skewer','grilled_bun_slice_skewer',
 'grilled_ender_pearl_skewer','grilled_meatball_skewer','grilled_slime_skewer',
 'grilled_meat_and_bone_skewer','grilled_fried_egg_skewer','grilled_gluten_skewer',
 'grilled_lamb_skewer','grilled_golden_skewer','ordinary_skewer',
)
REMAINDER=(
 'beef_chunks','chicken_skin','chicken_wing','squid_tentacle','houttuynia',
 'minced_houttuynia','carrot_dice','raw_sweet_potato_sheet','potato_slice',
 'raw_mantou_slice','green_chili_powder','sichuan_pepper','onion_powder',
 'houttuynia_powder','totem_powder','dragon_egg_powder','oil_cake','oil_residue',
 'canola_powder','onion','sweet_potato','roasted_sweet_potato','sweet_potato_powder',
 'roasted_chicken_wing','cold_houttuynia','canola_seeds',
)
VISIBLE_ITEMS=(
 'skewer_recipe_book','empty_seasoning_bottle','special_seasoning',
 'canola_oil_bucket','secret_chili_oil_bucket','premium_chili_oil_bucket',
)+RAW+COOKED+('mysterious_skewer','dark_grilling')+REMAINDER
CATALOG_IDS=(
 'kaleidoscope_grilling:grill','kaleidoscope_grilling:oil_press','kaleidoscope_grilling:big_vat',
)+tuple('kaleidoscope_grilling:'+x for x in VISIBLE_ITEMS)

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.23 Creative Catalog BP'),(rm,'Kaleidoscope Grilling A2.7.23 Creative Catalog RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.23 Creative Catalog';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_23_Creative_Catalog';write(P/'config.json',cfg)

def patch_hidden_items():
 for item_id in HIDDEN:
  path=BP/'items'/f'{item_id}.json';doc=load(path)
  desc=doc['minecraft:item']['description'];desc['menu_category']={'category':'none'}
  write(path,doc)

def patch_catalog():
 visible_files={p.stem for p in (BP/'items').glob('*.json')} - set(HIDDEN)
 if visible_files!=set(VISIBLE_ITEMS):
  raise RuntimeError('A2.7.23 catalog list drift: missing='+repr(sorted(visible_files-set(VISIBLE_ITEMS)))+' stale='+repr(sorted(set(VISIBLE_ITEMS)-visible_files)))
 catalog={
  'format_version':'1.21.60',
  'minecraft:crafting_items_catalog':{
   'categories':[{
    'category_name':'items',
    'groups':[{
     'group_identifier':{'icon':'kaleidoscope_grilling:grill','name':GROUP_KEY},
     'items':list(CATALOG_IDS),
    }],
   }],
  },
 }
 write(BP/'item_catalog/crafting_item_catalog.json',catalog)

def set_lang(path,rows):
 text=path.read_text(encoding='utf-8')
 lines=text.splitlines();index={}
 for i,line in enumerate(lines):
  if '=' in line:index[line.split('=',1)[0]]=i
 for key,value in rows.items():
  row=key+'='+value
  if key in index:lines[index[key]]=row
  else:lines.append(row)
 path.write_text('\n'.join(lines).rstrip()+'\n',encoding='utf-8')

def patch_names():
 labels={
  'zh_CN':{
   GROUP_KEY:'森罗物语：烟火',
   'item.kaleidoscope_grilling:pending_seasoning.name':'待摇晃的调料',
   'item.kaleidoscope_grilling:secret_skewer.name':'秘制烤串',
  },
  'zh_TW':{
   GROUP_KEY:'森羅物語：煙火',
   'item.kaleidoscope_grilling:pending_seasoning.name':'待搖晃的調料',
   'item.kaleidoscope_grilling:secret_skewer.name':'秘製烤串',
  },
  'en_US':{
   GROUP_KEY:'Kaleidoscope Grilling',
   'item.kaleidoscope_grilling:pending_seasoning.name':'Seasoning to Be Shaken',
   'item.kaleidoscope_grilling:secret_skewer.name':'Secret Mix Skewer',
  },
 }
 for lang,rows in labels.items():set_lang(RP/f'texts/{lang}.lang',rows)

def report():
 write(P/'reports/a2723-creative-catalog.json',{
  'version':'A2.7.23',
  'scope':'creative inventory parity and internal-state hiding',
  'java_baseline':'breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c',
  'java_creative_tab':'itemGroup.kaleidoscope_grilling.main',
  'bedrock_equivalent':{
   'surface':'items category / one collapsible custom group',
   'group_key':GROUP_KEY,'group_icon':'kaleidoscope_grilling:grill',
   'catalog_entry_count':len(CATALOG_IDS),
   'exact_custom_top_level_tab_possible':False,
  },
  'hidden_internal_items':list(HIDDEN),
  'java_order_preserved_for_existing_static_content':True,
  'omitted_java_dynamic_previews':[
   'configured beef skewer recipe book stack','dynamic secret-skewer preview',
   'metadata-bearing mysterious/dark preview variants','Cookery filled oil pots',
  ],
  'missing_java_content_not_faked':['advanced_rack'],
  'minecraft_tested':False,'bds_tested':False,
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,22]:
  raise RuntimeError('A2.7.23 must augment verified A2.7.22')
 patch_versions();patch_hidden_items();patch_catalog();patch_names();report()
 print('A2.7.23 creative catalog complete')
if __name__=='__main__':main()
