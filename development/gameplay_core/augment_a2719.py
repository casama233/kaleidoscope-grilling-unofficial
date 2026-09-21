from __future__ import annotations
import hashlib,json,shutil,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,19]
UP='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
ITEM_SHA='6761c2d89d46df2e536dd6df3fe9fdb7c2262259'
TEX={
 'stage0':'608a3eefe99930634897aee339356fd4d87a3829',
 'stage1':'22f4433daf385c206e6da0e4860c5877c3ddbb66',
 'stage2':'22f4433daf385c206e6da0e4860c5877c3ddbb66',
 'stage3':'7b8349e033f88b4f5e79a55e258da8e38a1ccee7',
 'stage4':'7b8349e033f88b4f5e79a55e258da8e38a1ccee7',
 'stage5':'bec26da1ffb404891263206e4918de9e80fa19a8',
 'stage6':'bec26da1ffb404891263206e4918de9e80fa19a8',
 'stage7':'1c4f02073284ed2efb738bd69d090750a38ff75e'
}
P_BONUS=0.5714286

def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path,sha):
 req=urllib.request.Request(UP+path,headers={'User-Agent':'Grilling-A2.7.19/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 got=blob(v)
 if got!=sha:raise RuntimeError(f'pinned upstream mismatch {path}: {got} != {sha}')
 return v
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text((json.dumps(d,ensure_ascii=False,indent=2)+'\n') if isinstance(d,(dict,list)) else d,encoding='utf-8')
def replace_once(s,old,new,label):
 if old not in s:raise RuntimeError('A2.7.19 patch anchor missing: '+label)
 return s.replace(old,new,1)

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.19 Sweet Potato Crop BP'),(rm,'Kaleidoscope Grilling A2.7.19 Sweet Potato Crop RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.19 Sweet Potato Crop';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_19_Sweet_Potato_Crop';write(P/'config.json',cfg)

def patch_item():
 p=BP/'items/sweet_potato.json';doc=load(p);item=doc['minecraft:item'];c=item['components']
 assert item['description']['identifier']=='kaleidoscope_grilling:sweet_potato'
 assert c['minecraft:food']['nutrition']==3 and abs(c['minecraft:food']['saturation_modifier']-.1)<1e-9
 assert c['minecraft:use_modifiers']['start_using']=='always'
 c['minecraft:use_modifiers']['start_using']='if_first'
 c['minecraft:block_placer']={'block':'kaleidoscope_grilling:sweet_potato_crop','use_on':['minecraft:farmland'],'replace_block_item':False}
 c['minecraft:compostable']={'composting_chance':65}
 write(p,doc)

def mat(stage):return {'minecraft:material_instances':{'*':{'texture':'sweet_potato_'+stage,'render_method':'alpha_test','face_dimming':False,'ambient_occlusion':False}}}
def selection(age):return {'minecraft:selection_box':{'origin':[-8,0,-8],'size':[16,min(16,2+age*2),16]}}

def crop_block():
 perms=[]
 for age in range(8):
  comp={};comp.update(mat(f'stage{age}'));comp.update(selection(age))
  if age==7:comp['minecraft:loot']='loot_tables/blocks/sweet_potato_crop_mature.json'
  perms.append({'condition':f"query.block_state('kaleidoscope_grilling:age') == {age}",'components':comp})
 return {'format_version':'1.26.30','minecraft:block':{
  'description':{'identifier':'kaleidoscope_grilling:sweet_potato_crop','states':{'kaleidoscope_grilling:age':list(range(8))}},
  'permutations':perms,
  'components':{
   'minecraft:geometry':'geometry.kaleidoscope_grilling.houttuynia_crop',
   'minecraft:material_instances':{'*':{'texture':'sweet_potato_stage0','render_method':'alpha_test','face_dimming':False,'ambient_occlusion':False}},
   'minecraft:destructible_by_mining':{'seconds_to_destroy':0},
   'minecraft:collision_box':False,'minecraft:light_dampening':0,
   'minecraft:selection_box':{'origin':[-8,0,-8],'size':[16,2,16]},
   'minecraft:placement_filter':{'conditions':[{'allowed_faces':['up'],'block_filter':['minecraft:farmland']}]},
   'minecraft:loot':'loot_tables/blocks/sweet_potato_crop.json',
   'tag:minecraft:crop':{},
   'kaleidoscope_grilling:sweet_potato_crop_logic':{}
  }
 }}

def immature_loot():
 return {'pools':[{'rolls':1,'entries':[{'type':'item','name':'kaleidoscope_grilling:sweet_potato','weight':1}]}]}

def mature_loot():
 pools=[{'rolls':1,'entries':[{'type':'item','name':'kaleidoscope_grilling:sweet_potato','weight':1,'functions':[{'function':'set_count','count':3}]}]}]
 for _ in range(3):
  pools.append({'rolls':1,'conditions':[{'condition':'random_chance','chance':P_BONUS}],'entries':[{'type':'item','name':'kaleidoscope_grilling:sweet_potato','weight':1}]})
 for level in (1,2,3):
  pools.append({'rolls':1,'conditions':[{'condition':'random_chance','chance':P_BONUS},{'condition':'match_tool','enchantments':[{'enchantment':'fortune','levels':{'range_min':level}}]}],'entries':[{'type':'item','name':'kaleidoscope_grilling:sweet_potato','weight':1}]})
 return {'pools':pools}

def strip_old_cropdrop(path):
 s=path.read_text(encoding='utf-8')
 marker='\nworld.afterEvents.playerBreakBlock.subscribe(event=>{'
 start=s.find(marker)
 if start<0:raise RuntimeError(f'A2.7.19 expected old crop-drop subscriber in {path.name}')
 end=s.find('\n});',start)
 if end<0:raise RuntimeError(f'A2.7.19 crop-drop subscriber terminator missing in {path.name}')
 s=s[:start]+s[end+4:]
 path.write_text(s,encoding='utf-8')

def patch_assets():
 write(BP/'blocks/sweet_potato_crop.json',crop_block())
 write(BP/'loot_tables/blocks/sweet_potato_crop.json',immature_loot())
 write(BP/'loot_tables/blocks/sweet_potato_crop_mature.json',mature_loot())
 if not (RP/'models/blocks/houttuynia_crop.geo.json').is_file():raise RuntimeError('A2.7.19 requires verified 16x16 cross-crop geometry')
 terrain=load(RP/'textures/terrain_texture.json')
 for name,sha in TEX.items():
  rel=f'textures/blocks/crop/sweet_potato/{name}';out=RP/(rel+'.png');out.parent.mkdir(parents=True,exist_ok=True)
  out.write_bytes(fetch(f'common/src/main/resources/assets/kaleidoscope_grilling/textures/block/crop/sweet_potato/{name}.png',sha))
  terrain['texture_data']['sweet_potato_'+name]={'textures':rel}
 write(RP/'textures/terrain_texture.json',terrain)
 labels={
  'zh_TW':{'tile.kaleidoscope_grilling:sweet_potato_crop.name':'番薯'},
  'zh_CN':{'tile.kaleidoscope_grilling:sweet_potato_crop.name':'红薯'},
  'en_US':{'tile.kaleidoscope_grilling:sweet_potato_crop.name':'Sweet Potato Crop'}
 }
 for lang,rows in labels.items():
  path=RP/f'texts/{lang}.lang';text=path.read_text(encoding='utf-8')
  for k,v in rows.items():
   if k+'=' not in text:text+='\n'+k+'='+v
  path.write_text(text.rstrip()+'\n',encoding='utf-8')

def patch_runtime():
 shutil.copy2(DEV/'a2719_sweet_potato_crop_core.js',BP/'scripts/a2719_sweet_potato_crop_core.js')
 shutil.copy2(DEV/'a2719_sweet_potato_crop_runtime.js',BP/'scripts/a2719_sweet_potato_crop_runtime.js')
 strip_old_cropdrop(BP/'scripts/a2715_canola_crop_runtime.js')
 strip_old_cropdrop(BP/'scripts/a2717_onion_crop_runtime.js')
 path=BP/'scripts/main.js';s=path.read_text(encoding='utf-8')
 anchor="import './a2718_onion_processing_runtime.js';"
 s=replace_once(s,anchor,anchor+"\nimport './a2719_sweet_potato_crop_runtime.js';",'runtime import')
 path.write_text(s,encoding='utf-8')

def report():
 item=RP/'textures/items/sweet_potato.png'
 if blob(item.read_bytes())!=ITEM_SHA:raise RuntimeError('published sweet potato item texture drifted from pinned Java source')
 write(P/'reports/a2719-parity.json',{
  'version':'A2.7.19','scope':'Sweet Potato crop + complete Java-order straw-hat CropDropHandler',
  'java_baseline':'breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c',
  'item':{
   'id':'kaleidoscope_grilling:sweet_potato','food':True,'nutrition':3,'saturation_modifier':0.1,
   'plants':'kaleidoscope_grilling:sweet_potato_crop','plantable_on':['minecraft:farmland'],
   'planting_priority':'minecraft:use_modifiers.start_using=if_first','composting_chance_percent':65,
   'texture_git_blob_sha1':ITEM_SHA
  },
  'crop':{
   'ages':[0,1,2,3,4,5,6,7],'max_age':7,'farmland_only':True,
   'farmland_survival_min_light':8,'growth_min_light':9,'bonemeal_age_increase':[2,5],
   'java_block_properties_source':'minecraft:beetroots','growth_math':'standard CropBlock helper',
   'texture_git_blob_sha1':TEX
  },
  'drops':{
   'immature':'1 sweet_potato',
   'mature':'3 + Binomial(Fortune+3, 0.5714286) sweet_potato; exact for vanilla Fortune 0..3',
   'overleveled_fortune_exact':False
  },
  'initial_acquisition':{
   'trigger':'successful minecraft:short_grass break','creative':False,
   'required_head':['kaleidoscope_cookery:straw_hat','kaleidoscope_cookery:straw_hat_flower'],
   'each_branch_chance':0.125,'each_branch_count':'1 + random(0..Fortune level)',
   'java_branch_order':['kaleidoscope_grilling:canola_seeds','kaleidoscope_grilling:sweet_potato','kaleidoscope_grilling:onion'],
   'single_unified_subscriber':True,'java_branch_draw_order_complete':True,
   'java_rng_algorithm_identical':False,
   'reason':'Bedrock Script uses Math.random rather than Java RandomSource; branch/count/chance call order and distributions are matched, not the PRNG algorithm.'
  },
  'downstream':{
   'sweet_potato_to_powder_millstone':'A2.7.2',
   'powder_kneading':'A2.7.1',
   'powder_chopping_board':'A2.7.2',
   'survival_acquisition_and_processing_to_sheet_complete':True
  },
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,18]:raise RuntimeError('A2.7.19 must augment verified A2.7.18')
 patch_versions();patch_item();patch_assets();patch_runtime();report();print('A2.7.19 sweet potato crop complete')
if __name__=='__main__':main()
