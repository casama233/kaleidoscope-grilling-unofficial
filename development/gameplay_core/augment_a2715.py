from __future__ import annotations
import hashlib,json,shutil,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,15]
UP='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
SEED_TEX=('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/canola_seeds.png','89a7008164006a16dcd194ce27b6e5c165b14987')
TEX={
 'stage0':'afc9eb650ca70bece3a5f0fb08e979d64512e71c',
 'stage1':'f4fa3cc14f2876aaf932dce2ebf7c4bd1a149aae',
 'stage2':'18ec9e2d1e55e491c90dbeb6c20d7ed652d0474e',
 'stage3':'4cb6afb9df1d62f590f7cea118f88049cbdfef0c',
 'stage4':'4cb6afb9df1d62f590f7cea118f88049cbdfef0c',
 'stage5':'314dcd4e949c5f610b1d07431424ec278ece5dc2',
 'stage6':'314dcd4e949c5f610b1d07431424ec278ece5dc2',
 'stage7':'5f7f96c41be52be77d53a2e337e7b2dbfa9f7218'
}
P_BONUS=0.5714286

def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path,sha):
 req=urllib.request.Request(UP+path,headers={'User-Agent':'Grilling-A2.7.15/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 got=blob(v)
 if got!=sha:raise RuntimeError(f'pinned upstream mismatch {path}: {got} != {sha}')
 return v
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text((json.dumps(d,ensure_ascii=False,indent=2)+'\n') if isinstance(d,(dict,list)) else d,encoding='utf-8')
def replace_once(s,old,new,label):
 if old not in s:raise RuntimeError('A2.7.15 patch anchor missing: '+label)
 return s.replace(old,new,1)

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.15 Canola Crop BP'),(rm,'Kaleidoscope Grilling A2.7.15 Canola Crop RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.15 Canola Crop';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_15_Canola_Crop';write(P/'config.json',cfg)

def seed_item():
 return {'format_version':'1.26.30','minecraft:item':{
  'description':{'identifier':'kaleidoscope_grilling:canola_seeds','menu_category':{'category':'items'}},
  'components':{
   'minecraft:display_name':{'value':'item.kaleidoscope_grilling:canola_seeds.name'},
   'minecraft:icon':{'textures':{'default':'canola_seeds'}},
   'minecraft:max_stack_size':64,
   'minecraft:block_placer':{'block':'kaleidoscope_grilling:canola_crop','use_on':['minecraft:farmland'],'replace_block_item':False},
   'minecraft:compostable':{'composting_chance':30}
  }
 }}

def mat(stage):return {'minecraft:material_instances':{'*':{'texture':'canola_'+stage,'render_method':'alpha_test','face_dimming':False,'ambient_occlusion':False}}}
def selection(age):return {'minecraft:selection_box':{'origin':[-8,0,-8],'size':[16,min(16,2+age*2),16]}}

def crop_block():
 perms=[]
 for age in range(8):
  comp={};comp.update(mat(f'stage{age}'));comp.update(selection(age))
  if age==7:comp['minecraft:loot']='loot_tables/blocks/canola_crop_mature.json'
  perms.append({'condition':f"query.block_state('kaleidoscope_grilling:age') == {age}",'components':comp})
 return {'format_version':'1.26.30','minecraft:block':{
  'description':{'identifier':'kaleidoscope_grilling:canola_crop','states':{'kaleidoscope_grilling:age':list(range(8))}},
  'permutations':perms,
  'components':{
   'minecraft:geometry':'geometry.kaleidoscope_grilling.houttuynia_crop',
   'minecraft:material_instances':{'*':{'texture':'canola_stage0','render_method':'alpha_test','face_dimming':False,'ambient_occlusion':False}},
   'minecraft:destructible_by_mining':{'seconds_to_destroy':0},
   'minecraft:collision_box':False,'minecraft:light_dampening':0,
   'minecraft:selection_box':{'origin':[-8,0,-8],'size':[16,2,16]},
   'minecraft:placement_filter':{'conditions':[{'allowed_faces':['up'],'block_filter':['minecraft:farmland']}]},
   'minecraft:loot':'loot_tables/blocks/canola_crop.json',
   'tag:minecraft:crop':{},
   'kaleidoscope_grilling:canola_crop_logic':{}
  }
 }}

def immature_loot():
 return {'pools':[{'rolls':1,'entries':[{'type':'item','name':'kaleidoscope_grilling:canola_seeds','weight':1}]}]}

def mature_loot():
 pools=[{'rolls':1,'entries':[{'type':'item','name':'kaleidoscope_grilling:canola_seeds','weight':1,'functions':[{'function':'set_count','count':2}]}]}]
 for _ in range(2):
  pools.append({'rolls':1,'conditions':[{'condition':'random_chance','chance':P_BONUS}],'entries':[{'type':'item','name':'kaleidoscope_grilling:canola_seeds','weight':1}]})
 for level in (1,2,3):
  pools.append({'rolls':1,'conditions':[{'condition':'random_chance','chance':P_BONUS},{'condition':'match_tool','enchantments':[{'enchantment':'fortune','levels':{'range_min':level}}]}],'entries':[{'type':'item','name':'kaleidoscope_grilling:canola_seeds','weight':1}]})
 return {'pools':pools}

def patch_assets():
 write(BP/'items/canola_seeds.json',seed_item())
 write(BP/'blocks/canola_crop.json',crop_block())
 write(BP/'loot_tables/blocks/canola_crop.json',immature_loot())
 write(BP/'loot_tables/blocks/canola_crop_mature.json',mature_loot())
 if not (RP/'models/blocks/houttuynia_crop.geo.json').is_file():raise RuntimeError('A2.7.15 reuses the A2.7.14 official-pattern cross crop geometry')
 seed_out=RP/'textures/items/canola_seeds.png';seed_out.parent.mkdir(parents=True,exist_ok=True);seed_out.write_bytes(fetch(*SEED_TEX))
 item_atlas=load(RP/'textures/item_texture.json');item_atlas['texture_data']['canola_seeds']={'textures':'textures/items/canola_seeds'};write(RP/'textures/item_texture.json',item_atlas)
 terrain=load(RP/'textures/terrain_texture.json')
 for name,sha in TEX.items():
  rel=f'textures/blocks/crop/canola/{name}';out=RP/(rel+'.png');out.parent.mkdir(parents=True,exist_ok=True)
  out.write_bytes(fetch(f'common/src/main/resources/assets/kaleidoscope_grilling/textures/block/crop/canola/{name}.png',sha))
  terrain['texture_data']['canola_'+name]={'textures':rel}
 write(RP/'textures/terrain_texture.json',terrain)
 labels={
  'zh_TW':{'item.kaleidoscope_grilling:canola_seeds.name':'油菜籽','tile.kaleidoscope_grilling:canola_crop.name':'油菜'},
  'zh_CN':{'item.kaleidoscope_grilling:canola_seeds.name':'油菜籽','tile.kaleidoscope_grilling:canola_crop.name':'油菜'},
  'en_US':{'item.kaleidoscope_grilling:canola_seeds.name':'Canola Seeds','tile.kaleidoscope_grilling:canola_crop.name':'Canola Crop'}
 }
 for lang,rows in labels.items():
  path=RP/f'texts/{lang}.lang';text=path.read_text(encoding='utf-8')
  for k,v in rows.items():
   if k+'=' not in text:text+='\n'+k+'='+v
  path.write_text(text.rstrip()+'\n',encoding='utf-8')

def patch_runtime():
 shutil.copy2(DEV/'a2715_canola_crop_core.js',BP/'scripts/a2715_canola_crop_core.js')
 shutil.copy2(DEV/'a2715_canola_crop_runtime.js',BP/'scripts/a2715_canola_crop_runtime.js')
 path=BP/'scripts/main.js';s=path.read_text(encoding='utf-8')
 anchor="import './a2714_houttuynia_crop_runtime.js';"
 s=replace_once(s,anchor,anchor+"\nimport './a2715_canola_crop_runtime.js';",'runtime import')
 path.write_text(s,encoding='utf-8')

def report():
 write(P/'reports/a2715-parity.json',{
  'version':'A2.7.15','scope':'Canola seeds acquisition + 8-age crop + composting',
  'java_baseline':'breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c',
  'item':{
   'id':'kaleidoscope_grilling:canola_seeds','plain_seed_item':True,'max_stack_size':64,
   'plants':'kaleidoscope_grilling:canola_crop','plantable_on':['minecraft:farmland'],
   'composting_chance_percent':30,'texture_git_blob_sha1':SEED_TEX[1]
  },
  'crop':{
   'ages':[0,1,2,3,4,5,6,7],'max_age':7,'farmland_only':True,
   'farmland_survival_min_light':8,'growth_min_light':9,'bonemeal_age_increase':[2,5],
   'growth_speed':'reuses A2.7.14 Java CropBlock 3x3 farmland weighting + crowding helper',
   'cross_geometry':'reuses A2.7.14 official Microsoft custom-crop-pattern geometry',
   'texture_git_blob_sha1':TEX
  },
  'drops':{
   'immature':'1 canola_seeds',
   'mature':'2 + Binomial(Fortune+2, 0.5714286) canola_seeds; exact for vanilla Fortune 0..3',
   'overleveled_fortune_exact':False
  },
  'initial_acquisition':{
   'trigger':'successful minecraft:short_grass break',
   'creative':False,
   'required_head':['kaleidoscope_cookery:straw_hat','kaleidoscope_cookery:straw_hat_flower'],
   'chance':0.125,'count':'1 + random(0..Fortune level)',
   'fortune_source':'itemStackBeforeBreak',
   'other_java_cropdrop_outputs_deferred':['kaleidoscope_grilling:sweet_potato','kaleidoscope_grilling:onion']
  },
  'downstream':{
   'canola_powder_item_already_present':True,
   'oil_cake_recipe_already_present':True,
   'oil_press_chain_already_present':True,
   'canola_seed_to_powder_processing_complete':False,
   'next_gap':'Cookery millstone: canola_seeds -> canola_powder x1'
  },
  'survival_canola_seed_acquisition_complete':True,
  'survival_canola_oil_chain_complete':False,
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,14]:raise RuntimeError('A2.7.15 must augment verified A2.7.14')
 patch_versions();patch_assets();patch_runtime();report();print('A2.7.15 canola crop complete')
if __name__=='__main__':main()
