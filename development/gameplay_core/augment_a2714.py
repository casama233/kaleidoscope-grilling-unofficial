from __future__ import annotations
import hashlib,json,shutil,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,14]
UP='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
CROP_SHA='c906c305a2ede0587bdf3d543f5782a05a16d71e'
REPLACEMENT_SHA='e0e5116dbf5f084efad161b1c32190351345ca4c'
TEX={
 'stage0':'228a95ee694f75f6f2770f74fb3b85acf044d92a',
 'stage1':'5a0dda7aa376f96e42e8c20b7b3eb53bc1164592',
 'stage2':'fdfa5a086de21aa2a437f1b2838e8c5a8efe473e',
 'stage3':'1c587cbab8282e3b883f1534eab91bf226a10385',
 'stage4':'5b9c4285c8fc3b23ea3cd5a431935955776f1471',
 'stage5':'40ed161b56ce21c80e4d9b61c68aba1c4f3a616c',
 'stage5_2':'c37ba99aa43123a0393f06c10f0cbe91e74c7056',
 'stage6':'e8865cf66b83766df45123fe13ea81d5cc49149b',
 'stage6_2':'64db168e8dd090b0310ebabaee2d043b64fb9615',
 'stage7':'dc69075167f3a1f7807a0a9aeca7f1753756662f',
 'stage7_2':'9345181aea1ed704ba56ca2b4e299674b9129804'
}

def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path,sha):
 req=urllib.request.Request(UP+path,headers={'User-Agent':'Grilling-A2.7.14/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 got=blob(v)
 if got!=sha:raise RuntimeError(f'pinned upstream mismatch {path}: {got} != {sha}')
 return v
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text((json.dumps(d,ensure_ascii=False,indent=2)+'\n') if isinstance(d,(dict,list)) else d,encoding='utf-8')
def replace_once(s,old,new,label):
 if old not in s:raise RuntimeError('A2.7.14 patch anchor missing: '+label)
 return s.replace(old,new,1)

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.14 Houttuynia Crop BP'),(rm,'Kaleidoscope Grilling A2.7.14 Houttuynia Crop RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.14 Houttuynia Crop';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_14_Houttuynia_Crop';write(P/'config.json',cfg)

def patch_item():
 p=BP/'items/houttuynia.json';doc=load(p);c=doc['minecraft:item']['components']
 c['minecraft:use_modifiers']['start_using']='if_first'
 c['minecraft:block_placer']={'block':'kaleidoscope_grilling:houttuynia_crop','use_on':['minecraft:farmland','minecraft:soul_sand'],'replace_block_item':False}
 write(p,doc)

def crop_geometry():
 return {'format_version':'1.21.10','minecraft:geometry':[{'description':{
  'identifier':'geometry.kaleidoscope_grilling.houttuynia_crop','texture_width':16,'texture_height':16,
  'visible_bounds_width':2,'visible_bounds_height':2,'visible_bounds_offset':[0,0,0]},
  'bones':[{'name':'world','pivot':[0,0,0],'cubes':[
   {'origin':[-8,-1,0],'size':[16,16,0],'pivot':[0,-1,0],'rotation':[0,45,0],'uv':[0,0]},
   {'origin':[-8,-1,0],'size':[16,16,0],'pivot':[0,-1,0],'rotation':[0,-45,0],'uv':[0,0]}
  ]}]}]}

def mat(tex):return {'minecraft:material_instances':{'*':{'texture':'houttuynia_'+tex,'render_method':'alpha_test','face_dimming':False,'ambient_occlusion':False}}}
def selection(age):return {'minecraft:selection_box':{'origin':[-8,0,-8],'size':[16,min(16,2+age*2),16]}}

def crop_block():
 perms=[]
 for age in range(5):
  comp={};comp.update(mat(f'stage{age}'));comp.update(selection(age))
  perms.append({'condition':f"query.block_state('kaleidoscope_grilling:age') == {age}",'components':comp})
 for age in (5,6,7):
  for red in (False,True):
   suffix=f'stage{age}_2' if red else f'stage{age}'
   comp={};comp.update(mat(suffix));comp.update(selection(age))
   if age==7:comp['minecraft:loot']='loot_tables/blocks/houttuynia_crop_mature.json'
   cond=f"query.block_state('kaleidoscope_grilling:age') == {age} && query.block_state('kaleidoscope_grilling:red_variant') == {'true' if red else 'false'}"
   perms.append({'condition':cond,'components':comp})
 return {'format_version':'1.26.30','minecraft:block':{
  'description':{'identifier':'kaleidoscope_grilling:houttuynia_crop','states':{
   'kaleidoscope_grilling:age':list(range(8)),'kaleidoscope_grilling:red_variant':[False,True]}},
  'permutations':perms,
  'components':{
   'minecraft:geometry':'geometry.kaleidoscope_grilling.houttuynia_crop',
   'minecraft:material_instances':{'*':{'texture':'houttuynia_stage0','render_method':'alpha_test','face_dimming':False,'ambient_occlusion':False}},
   'minecraft:destructible_by_mining':{'seconds_to_destroy':0},
   'minecraft:collision_box':False,
   'minecraft:light_dampening':0,
   'minecraft:selection_box':{'origin':[-8,0,-8],'size':[16,2,16]},
   'minecraft:placement_filter':{'conditions':[{'allowed_faces':['up'],'block_filter':['minecraft:farmland','minecraft:soul_sand']}]},
   'minecraft:loot':'loot_tables/blocks/houttuynia_crop.json',
   'tag:minecraft:crop':{},
   'kaleidoscope_grilling:houttuynia_crop_logic':{}
  }
 }}

def immature_loot():
 return {'pools':[{'rolls':1,'entries':[{'type':'item','name':'kaleidoscope_grilling:houttuynia','weight':1}]}]}

def mature_loot():
 pools=[{'rolls':1,'entries':[{'type':'item','name':'kaleidoscope_grilling:houttuynia','weight':1,'functions':[{'function':'set_count','count':2}]}]}]
 p=0.5714286
 pools.append({'rolls':1,'conditions':[{'condition':'random_chance','chance':p}],'entries':[{'type':'item','name':'kaleidoscope_grilling:houttuynia','weight':1}]})
 for level in (1,2,3):
  pools.append({'rolls':1,'conditions':[{'condition':'random_chance','chance':p},{'condition':'match_tool','enchantments':[{'enchantment':'fortune','levels':{'range_min':level}}]}],'entries':[{'type':'item','name':'kaleidoscope_grilling:houttuynia','weight':1}]})
 return {'pools':pools}

def patch_crop_assets():
 write(BP/'blocks/houttuynia_crop.json',crop_block())
 write(BP/'loot_tables/blocks/houttuynia_crop.json',immature_loot())
 write(BP/'loot_tables/blocks/houttuynia_crop_mature.json',mature_loot())
 write(RP/'models/blocks/houttuynia_crop.geo.json',crop_geometry())
 atlas=load(RP/'textures/terrain_texture.json')
 for name,sha in TEX.items():
  rel=f'textures/blocks/crop/houttuynia/{name}'
  out=RP/(rel+'.png');out.parent.mkdir(parents=True,exist_ok=True)
  src=f'common/src/main/resources/assets/kaleidoscope_grilling/textures/block/crop/houttuynia/{name}.png'
  out.write_bytes(fetch(src,sha));atlas['texture_data']['houttuynia_'+name]={'textures':rel}
 write(RP/'textures/terrain_texture.json',atlas)
 for lang,value in {'zh_TW':'折耳根作物','zh_CN':'折耳根作物','en_US':'Houttuynia Crop'}.items():
  path=RP/f'texts/{lang}.lang';text=path.read_text(encoding='utf-8');key='tile.kaleidoscope_grilling:houttuynia_crop.name'
  if key+'=' not in text:text+='\n'+key+'='+value
  path.write_text(text.rstrip()+'\n',encoding='utf-8')

def patch_runtime():
 shutil.copy2(DEV/'a2714_houttuynia_crop_core.js',BP/'scripts/a2714_houttuynia_crop_core.js')
 shutil.copy2(DEV/'a2714_houttuynia_crop_runtime.js',BP/'scripts/a2714_houttuynia_crop_runtime.js')
 path=BP/'scripts/main.js';s=path.read_text(encoding='utf-8')
 anchor="import './a2713_houttuynia_processing_runtime.js';"
 s=replace_once(s,anchor,anchor+"\nimport './a2714_houttuynia_crop_runtime.js';",'runtime import')
 path.write_text(s,encoding='utf-8')

def report():
 write(P/'reports/a2714-parity.json',{
  'version':'A2.7.14','scope':'Houttuynia crop planting, growth, variants, bonemeal, visuals and drops',
  'java_baseline':'breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c',
  'java_crop_source_sha1':CROP_SHA,'java_fortress_replacement_source_sha1':REPLACEMENT_SHA,
  'crop':{
   'ages':[0,1,2,3,4,5,6,7],'max_age':7,'plantable_on':['minecraft:farmland','minecraft:soul_sand'],
   'farmland_survival_min_light':8,'growth_min_light':9,'soul_sand_forces_red':True,'farmland_red_placement_chance':0.3,
   'red_variant_preserved_through_growth':True,'bonemeal_age_increase':[2,5],
   'growth_speed':'Java CropBlock 3x3 farmland weighting + adjacency crowding penalty',
   'runtime':'BlockCustomComponent registered from system.beforeEvents.startup; no global crop scan',
   'support_loss':'mature support-loss drop uses Fortune-0 Java formula instead of collapsing to one item'
  },
  'visuals':{'java_texture_blob_sha1':TEX,'cross_geometry':'adapted from Microsoft official custom crop sample pattern','red_variant_texture_starts_at_age':5},
  'drops':{
   'immature':'1 houttuynia',
   'mature':'2 + Binomial(Fortune+1, 0.5714286) houttuynia; Bedrock table exact for vanilla Fortune 0..3',
   'overleveled_fortune_exact':False
  },
  'item':{'same_houttuynia_food_item_places_crop':True,'use_on':['minecraft:farmland','minecraft:soul_sand'],'use_modifiers_start_using':'if_first'},
  'fortress_acquisition':{
   'wart_age_mapping':{'0':0,'1':3,'2':7},
   'java_replacement_percent':25,
   'exact_structure_bounded_replacement':False,
   'reason':'@minecraft/server 2.9.0 stable does not expose generated-structure containment; getGeneratedStructures is pre-release, so no heuristic replacement is claimed.'
  },
  'fortress_chest_bonus':False,'survival_houttuynia_acquisition_complete':False,
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,13]:raise RuntimeError('A2.7.14 must augment verified A2.7.13')
 patch_versions();patch_item();patch_crop_assets();patch_runtime();report();print('A2.7.14 houttuynia crop complete')
if __name__=='__main__':main()
