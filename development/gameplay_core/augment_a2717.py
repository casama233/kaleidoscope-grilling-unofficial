from __future__ import annotations
import hashlib,json,shutil,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,17]
UP='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
ITEM_TEX=('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/onion.png','103aa78661bf35aa6b3a42989a398573056faff1')
TEX={
 'stage0':'490cd255f3e94a82844e5c0dd4fbc0f39e7ed851',
 'stage1':'27e70b8e92331894e46926a1a9acd19b77a7329d',
 'stage2':'22f7dd1f49602fce4cce32046bc2b70140b2cb7f',
 'stage3':'8963fc4f952806dc0833eb19a4fbe1b831a3eb74',
 'stage4':'348515d3f3c59a5a06a4d366f831b676e71f16b4',
 'stage5':'5a4631796be63179bcf796359eeba00a5986e04c',
 'stage6':'e8badfe410205c7d82745124cec24c5a93802208',
 'stage7':'857cddb6802c9cf63f32d4ff799fd799beb753ff'
}
P_BONUS=0.5714286

def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path,sha):
 req=urllib.request.Request(UP+path,headers={'User-Agent':'Grilling-A2.7.17/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 got=blob(v)
 if got!=sha:raise RuntimeError(f'pinned upstream mismatch {path}: {got} != {sha}')
 return v
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text((json.dumps(d,ensure_ascii=False,indent=2)+'\n') if isinstance(d,(dict,list)) else d,encoding='utf-8')
def replace_once(s,old,new,label):
 if old not in s:raise RuntimeError('A2.7.17 patch anchor missing: '+label)
 return s.replace(old,new,1)

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.17 Onion Crop BP'),(rm,'Kaleidoscope Grilling A2.7.17 Onion Crop RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.17 Onion Crop';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_17_Onion_Crop';write(P/'config.json',cfg)

def onion_item():
 return {'format_version':'1.26.30','minecraft:item':{
  'description':{'identifier':'kaleidoscope_grilling:onion','menu_category':{'category':'items'}},
  'components':{
   'minecraft:display_name':{'value':'item.kaleidoscope_grilling:onion.name'},
   'minecraft:icon':{'textures':{'default':'onion'}},
   'minecraft:max_stack_size':64,
   'minecraft:block_placer':{'block':'kaleidoscope_grilling:onion_crop','use_on':['minecraft:farmland'],'replace_block_item':False},
   'minecraft:compostable':{'composting_chance':65}
  }
 }}

def mat(stage):return {'minecraft:material_instances':{'*':{'texture':'onion_'+stage,'render_method':'alpha_test','face_dimming':False,'ambient_occlusion':False}}}
def selection(age):return {'minecraft:selection_box':{'origin':[-8,0,-8],'size':[16,min(16,2+age*2),16]}}

def crop_block():
 perms=[]
 for age in range(8):
  comp={};comp.update(mat(f'stage{age}'));comp.update(selection(age))
  if age==7:comp['minecraft:loot']='loot_tables/blocks/onion_crop_mature.json'
  perms.append({'condition':f"query.block_state('kaleidoscope_grilling:age') == {age}",'components':comp})
 return {'format_version':'1.26.30','minecraft:block':{
  'description':{'identifier':'kaleidoscope_grilling:onion_crop','states':{'kaleidoscope_grilling:age':list(range(8))}},
  'permutations':perms,
  'components':{
   'minecraft:geometry':'geometry.kaleidoscope_grilling.houttuynia_crop',
   'minecraft:material_instances':{'*':{'texture':'onion_stage0','render_method':'alpha_test','face_dimming':False,'ambient_occlusion':False}},
   'minecraft:destructible_by_mining':{'seconds_to_destroy':0},
   'minecraft:collision_box':False,'minecraft:light_dampening':0,
   'minecraft:selection_box':{'origin':[-8,0,-8],'size':[16,2,16]},
   'minecraft:placement_filter':{'conditions':[{'allowed_faces':['up'],'block_filter':['minecraft:farmland']}]},
   'minecraft:loot':'loot_tables/blocks/onion_crop.json',
   'tag:minecraft:crop':{},
   'kaleidoscope_grilling:onion_crop_logic':{}
  }
 }}

def immature_loot():
 return {'pools':[{'rolls':1,'entries':[{'type':'item','name':'kaleidoscope_grilling:onion','weight':1}]}]}

def mature_loot():
 pools=[{'rolls':1,'entries':[{'type':'item','name':'kaleidoscope_grilling:onion','weight':1,'functions':[{'function':'set_count','count':2}]}]}]
 for _ in range(2):
  pools.append({'rolls':1,'conditions':[{'condition':'random_chance','chance':P_BONUS}],'entries':[{'type':'item','name':'kaleidoscope_grilling:onion','weight':1}]})
 for level in (1,2,3):
  pools.append({'rolls':1,'conditions':[{'condition':'random_chance','chance':P_BONUS},{'condition':'match_tool','enchantments':[{'enchantment':'fortune','levels':{'range_min':level}}]}],'entries':[{'type':'item','name':'kaleidoscope_grilling:onion','weight':1}]})
 return {'pools':pools}

def patch_assets():
 write(BP/'items/onion.json',onion_item())
 write(BP/'blocks/onion_crop.json',crop_block())
 write(BP/'loot_tables/blocks/onion_crop.json',immature_loot())
 write(BP/'loot_tables/blocks/onion_crop_mature.json',mature_loot())
 if not (RP/'models/blocks/houttuynia_crop.geo.json').is_file():raise RuntimeError('A2.7.17 requires verified 16x16 cross-crop geometry from A2.7.14')
 item_out=RP/'textures/items/onion.png';item_out.parent.mkdir(parents=True,exist_ok=True);item_out.write_bytes(fetch(*ITEM_TEX))
 item_atlas=load(RP/'textures/item_texture.json');item_atlas['texture_data']['onion']={'textures':'textures/items/onion'};write(RP/'textures/item_texture.json',item_atlas)
 terrain=load(RP/'textures/terrain_texture.json')
 for name,sha in TEX.items():
  rel=f'textures/blocks/crop/onion/{name}';out=RP/(rel+'.png');out.parent.mkdir(parents=True,exist_ok=True)
  out.write_bytes(fetch(f'common/src/main/resources/assets/kaleidoscope_grilling/textures/block/crop/onion/{name}.png',sha))
  terrain['texture_data']['onion_'+name]={'textures':rel}
 write(RP/'textures/terrain_texture.json',terrain)
 labels={
  'zh_TW':{'item.kaleidoscope_grilling:onion.name':'洋蔥','tile.kaleidoscope_grilling:onion_crop.name':'洋蔥'},
  'zh_CN':{'item.kaleidoscope_grilling:onion.name':'洋葱','tile.kaleidoscope_grilling:onion_crop.name':'洋葱'},
  'en_US':{'item.kaleidoscope_grilling:onion.name':'Onion','tile.kaleidoscope_grilling:onion_crop.name':'Onion Crop'}
 }
 for lang,rows in labels.items():
  path=RP/f'texts/{lang}.lang';text=path.read_text(encoding='utf-8')
  for k,v in rows.items():
   if k+'=' not in text:text+='\n'+k+'='+v
  path.write_text(text.rstrip()+'\n',encoding='utf-8')

def patch_runtime():
 shutil.copy2(DEV/'a2717_onion_crop_core.js',BP/'scripts/a2717_onion_crop_core.js')
 shutil.copy2(DEV/'a2717_onion_crop_runtime.js',BP/'scripts/a2717_onion_crop_runtime.js')
 path=BP/'scripts/main.js';s=path.read_text(encoding='utf-8')
 anchor="import './a2716_canola_processing_runtime.js';"
 s=replace_once(s,anchor,anchor+"\nimport './a2717_onion_crop_runtime.js';",'runtime import')
 path.write_text(s,encoding='utf-8')

def report():
 write(P/'reports/a2717-parity.json',{
  'version':'A2.7.17','scope':'Onion item + 8-age crop + straw-hat short-grass acquisition',
  'java_baseline':'breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c',
  'item':{
   'id':'kaleidoscope_grilling:onion','plain_crop_item':True,'max_stack_size':64,'food':False,
   'plants':'kaleidoscope_grilling:onion_crop','plantable_on':['minecraft:farmland'],
   'composting_chance_percent':65,'texture_git_blob_sha1':ITEM_TEX[1]
  },
  'crop':{
   'ages':[0,1,2,3,4,5,6,7],'max_age':7,'farmland_only':True,
   'farmland_survival_min_light':8,'growth_min_light':9,'bonemeal_age_increase':[2,5],
   'growth_speed':'reuses tested Java CropBlock 3x3 farmland weighting + crowding helper',
   'cross_geometry':'reuses A2.7.14 verified 16x16 crop geometry',
   'texture_git_blob_sha1':TEX
  },
  'drops':{
   'immature':'1 onion',
   'mature':'2 + Binomial(Fortune+2, 0.5714286) onion; exact for vanilla Fortune 0..3',
   'overleveled_fortune_exact':False
  },
  'initial_acquisition':{
   'trigger':'successful minecraft:short_grass break',
   'creative':False,
   'required_head':['kaleidoscope_cookery:straw_hat','kaleidoscope_cookery:straw_hat_flower'],
   'chance':0.125,'count':'1 + random(0..Fortune level)','fortune_source':'itemStackBeforeBreak',
   'per_branch_probability_count_exact':True,
   'full_java_rng_call_order_complete':False,
   'reason':'Java calls Canola, Sweet Potato, then Onion tryDrop in one handler; Sweet Potato branch remains deferred, so raw RNG stream order is not byte-for-byte identical yet.'
  },
  'downstream':{
   'onion_powder_item_already_present':True,
   'onion_to_powder_processing_complete':False,
   'next_gap':'Cookery millstone: onion tag -> onion_powder x1'
  },
  'survival_onion_acquisition_complete':True,
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,16]:raise RuntimeError('A2.7.17 must augment verified A2.7.16')
 patch_versions();patch_assets();patch_runtime();report();print('A2.7.17 onion crop complete')
if __name__=='__main__':main()
