from __future__ import annotations
import copy,hashlib,json,shutil,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'projects/grilling'
P=SRC/'gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
A1RP=SRC/'resource_pack'
VERSION=[2,6,0]
UP='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
ASSETS={
 'canola_powder':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/canola_powder.png','1772fc66d797448e29396b41eb45ae408e959786'),
 'oil_cake':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/oil_cake.png','7fe58aa3aec5c9ba01d47efed453f65f54dceaca'),
 'oil_residue':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/oil_residue.png','6160880abe309657cd7e9e6ffe7ebaa109179052')
}
def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path,sha):
 req=urllib.request.Request(UP+path,headers={'User-Agent':'Grilling-A2.6/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 if blob(v)!=sha:raise RuntimeError('pinned upstream mismatch '+path)
 return v
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text((json.dumps(d,ensure_ascii=False,indent=2)+'\n') if isinstance(d,(dict,list)) else d,encoding='utf-8')
def replace_once(s,old,new,label):
 if old not in s:raise RuntimeError('A2.6 patch anchor missing: '+label)
 return s.replace(old,new,1)

def patch_manifest():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.6 Gameplay BP'),(rm,'Kaleidoscope Grilling A2.6 Gameplay RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.6 Gameplay';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_6';write(P/'config.json',cfg)

def copy_runtime():
 shutil.copy2(DEV/'a26_oil_machine_core.js',BP/'scripts/a26_oil_machine_core.js')
 shutil.copy2(DEV/'a26_oil_machine_runtime.js',BP/'scripts/a26_oil_machine_runtime.js')
 main=BP/'scripts/main.js';s=main.read_text(encoding='utf-8')
 anchor="import {a25PlateRows,a25PlateItem,a25RestoreStack} from './a25_plate_recipe_runtime.js';"
 s=replace_once(s,anchor,anchor+"\nimport './a26_oil_machine_runtime.js';",'main runtime import')
 main.write_text(s,encoding='utf-8')
 oil=BP/'scripts/a23_oil_world.js';s=oil.read_text(encoding='utf-8')
 anchor="world.beforeEvents.playerInteractWithBlock.subscribe(e=>{\n const item=e.itemStack,typeFromBlock=BLOCK_TO_TYPE[e.block.typeId],bucketType=item?BUCKET_TO_TYPE[item.typeId]:undefined;"
 repl="world.beforeEvents.playerInteractWithBlock.subscribe(e=>{\n if(e.block.typeId==='kaleidoscope_grilling:big_vat')return;\n const item=e.itemStack,typeFromBlock=BLOCK_TO_TYPE[e.block.typeId],bucketType=item?BUCKET_TO_TYPE[item.typeId]:undefined;"
 s=replace_once(s,anchor,repl,'oil world big vat exclusion');oil.write_text(s,encoding='utf-8')

def ingredient_item(id,icon):
 return {'format_version':'1.26.30','minecraft:item':{'description':{'identifier':'kaleidoscope_grilling:'+id,'menu_category':{'category':'items'}},'components':{'minecraft:display_name':{'value':'item.kaleidoscope_grilling:'+id+'.name'},'minecraft:icon':{'textures':{'default':icon}},'minecraft:max_stack_size':64}}}

def prefix_bones(doc,prefix):
 g=copy.deepcopy(doc['minecraft:geometry'][0]);out=[]
 for b in g.get('bones',[]):
  if b.get('name')=='root':continue
  b=copy.deepcopy(b);old=b['name'];b['name']=prefix+old
  if b.get('parent') and b['parent']!='root':b['parent']=prefix+b['parent']
  else:b['parent']='root'
  out.append(b)
 return out,g['description']

def merged_press(parts,identifier):
 bones=[{'name':'root','pivot':[0,0,0]}];desc=None
 for i,name in enumerate(parts):
  doc=load(A1RP/f'models/entity/kg_a1/{name}.geo.json');rows,d=prefix_bones(doc,f'p{i}_');bones+=rows
  if desc is None:desc=copy.deepcopy(d)
 desc['identifier']=identifier
 return {'format_version':'1.16.0','minecraft:geometry':[{'description':desc,'bones':bones}]}

def vat_geo(level):
 doc=load(A1RP/'models/entity/kg_a1/big_vat.geo.json');g=copy.deepcopy(doc['minecraft:geometry'][0])
 g['description']['identifier']=f'geometry.kg_a26.big_vat_{level}'
 if level>0:
  y={1:5,2:8,3:11,4:14}[level]
  faces={}
  for f in ('up','down','north','south','east','west'):
   faces[f]={'uv':[0,0],'uv_size':[64,64],'material_instance':'fluid'}
  g['bones'].append({'name':'fluid_surface','pivot':[0,0,0],'cubes':[{'origin':[-6,y,-6],'size':[12,0.0625,12],'uv':faces}]})
 return {'format_version':'1.16.0','minecraft:geometry':[g]}

def patch_content():
 for id in ('canola_powder','oil_cake','oil_residue'):write(BP/f'items/{id}.json',ingredient_item(id,id))
 for id,(path,sha) in ASSETS.items():
  out=RP/f'textures/items/{id}.png';out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(fetch(path,sha))

 press={
  'format_version':'1.26.50','minecraft:block':{
   'description':{
    'identifier':'kaleidoscope_grilling:oil_press','menu_category':{'category':'items'},
    'states':{'kaleidoscope_grilling:cake_count':[0,1,2,3,4],'kaleidoscope_grilling:press_stage':[0,1,2,3,4]},
    'traits':{'minecraft:placement_direction':{'enabled_states':['minecraft:cardinal_direction'],'y_rotation_offset':180.0}}
   },
   'components':{
    'minecraft:display_name':'tile.kaleidoscope_grilling:oil_press.name',
    'minecraft:geometry':'geometry.kg_a26.oil_press_c0_s0',
    'minecraft:material_instances':{'*':{'texture':'kg_a26_oil_press','render_method':'alpha_test','ambient_occlusion':1.0,'face_dimming':True}},
    'minecraft:collision_box':{'origin':[-8,0,-8],'size':[16,16,16]},
    'minecraft:selection_box':{'origin':[-8,0,-8],'size':[16,16,16]},
    'minecraft:destructible_by_mining':{'seconds_to_destroy':2.5},
    'minecraft:destructible_by_explosion':{'explosion_resistance':3.0}
   },
   'permutations':[]
  }
 }
 for c in range(5):
  press['minecraft:block']['permutations'].append({'condition':f"q.block_state('kaleidoscope_grilling:press_stage') == 0 && q.block_state('kaleidoscope_grilling:cake_count') == {c}",'components':{'minecraft:geometry':f'geometry.kg_a26.oil_press_c{c}_s0'}})
 for st in range(1,5):
  press['minecraft:block']['permutations'].append({'condition':f"q.block_state('kaleidoscope_grilling:press_stage') == {st}",'components':{'minecraft:geometry':f'geometry.kg_a26.oil_press_c4_s{st}'}})
 for direction,rot in [('north',0),('south',180),('west',90),('east',270)]:
  press['minecraft:block']['permutations'].append({'condition':f"q.block_state('minecraft:cardinal_direction') == '{direction}'",'components':{'minecraft:transformation':{'rotation':[0,rot,0]}}})
 write(BP/'blocks/oil_press.json',press)

 vat={
  'format_version':'1.26.50','minecraft:block':{
   'description':{'identifier':'kaleidoscope_grilling:big_vat','menu_category':{'category':'items'},'states':{'kaleidoscope_grilling:vat_level':[0,1,2,3,4],'kaleidoscope_grilling:vat_fluid':['empty','water','lava','canola','secret_chili','premium_chili']}},
   'components':{
    'minecraft:display_name':'tile.kaleidoscope_grilling:big_vat.name',
    'minecraft:geometry':'geometry.kg_a26.big_vat_0',
    'minecraft:material_instances':{
     '*':{'texture':'kg_a26_big_vat','render_method':'alpha_test','ambient_occlusion':1.0,'face_dimming':True},
     'fluid':{'texture':'kg_a26_water','render_method':'blend','ambient_occlusion':0.0,'face_dimming':False}
    },
    'minecraft:collision_box':{'origin':[-8,0,-8],'size':[16,16,16]},
    'minecraft:selection_box':{'origin':[-8,0,-8],'size':[16,16,16]},
    'minecraft:destructible_by_mining':{'seconds_to_destroy':2.0},
    'minecraft:destructible_by_explosion':{'explosion_resistance':6.0}
   },
   'permutations':[]
  }
 }
 for lv in range(5):vat['minecraft:block']['permutations'].append({'condition':f"q.block_state('kaleidoscope_grilling:vat_level') == {lv}",'components':{'minecraft:geometry':f'geometry.kg_a26.big_vat_{lv}'}})
 tex={'water':'kg_a26_water','lava':'kg_a26_lava','canola':'kg_a23_canola_oil','secret_chili':'kg_a23_secret_chili_oil','premium_chili':'kg_a23_premium_chili_oil'}
 for typ,key in tex.items():
  vat['minecraft:block']['permutations'].append({'condition':f"q.block_state('kaleidoscope_grilling:vat_fluid') == '{typ}'",'components':{'minecraft:material_instances':{'*':{'texture':'kg_a26_big_vat','render_method':'alpha_test','ambient_occlusion':1.0,'face_dimming':True},'fluid':{'texture':key,'render_method':'blend','ambient_occlusion':0.0,'face_dimming':False}}}})
 write(BP/'blocks/big_vat.json',vat)

 models=RP/'models/blocks';models.mkdir(parents=True,exist_ok=True)
 for c in range(5):
  parts=['oil_press_frame','oil_press_hit_0']+([] if c==0 else [f'oil_press_oil1_{c}'])
  write(models/f'oil_press_c{c}_s0.geo.json',merged_press(parts,f'geometry.kg_a26.oil_press_c{c}_s0'))
 for st,oil in [(1,'oil_press_oil2'),(2,'oil_press_oil3'),(3,'oil_press_oil4'),(4,'oil_press_oil5')]:
  write(models/f'oil_press_c4_s{st}.geo.json',merged_press(['oil_press_frame',f'oil_press_hit_{st}',oil],f'geometry.kg_a26.oil_press_c4_s{st}'))
 for lv in range(5):write(models/f'big_vat_{lv}.geo.json',vat_geo(lv))

 for src,dst in [('oil_press.png','oil_press.png'),('big_vat.png','big_vat.png')]:
  out=RP/'textures/blocks'/dst;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(A1RP/'textures/kg_a1'/src,out)
 itemtex=load(RP/'textures/item_texture.json')
 for id in ('canola_powder','oil_cake','oil_residue'):itemtex['texture_data'][id]={'textures':f'textures/items/{id}'}
 write(RP/'textures/item_texture.json',itemtex)
 terrain=load(RP/'textures/terrain_texture.json')
 terrain['texture_data']['kg_a26_oil_press']={'textures':'textures/blocks/oil_press'}
 terrain['texture_data']['kg_a26_big_vat']={'textures':'textures/blocks/big_vat'}
 terrain['texture_data']['kg_a26_water']={'textures':'textures/blocks/water_still_grey'}
 terrain['texture_data']['kg_a26_lava']={'textures':'textures/blocks/lava_still'}
 write(RP/'textures/terrain_texture.json',terrain)

 anim={'format_version':'1.8.0','animations':{'animation.kg_a26.player.anvil_press':{
  'animation_length':0.45,'override_previous_animation':False,
  'bones':{
   'rightarm':{'rotation':{'0.0':[-125,0,10],'0.30':[-25,0,5],'0.45':[0,0,0]}},
   'leftarm':{'rotation':{'0.0':[-125,0,-10],'0.30':[-25,0,-5],'0.45':[0,0,0]}},
   'body':{'rotation':{'0.0':[-8,0,0],'0.30':[18,0,0],'0.45':[0,0,0]}}
  }
 }}}
 write(RP/'animations/a26_oil_press.animation.json',anim)

 recipes=BP/'recipes';recipes.mkdir(parents=True,exist_ok=True)
 def shaped(id,pattern,key,result):
  return {'format_version':'1.20.10','minecraft:recipe_shaped':{'description':{'identifier':'kaleidoscope_grilling:'+id},'tags':['crafting_table'],'pattern':pattern,'key':key,'result':{'item':'kaleidoscope_grilling:'+result,'count':1}}}
 write(recipes/'oil_cake.json',shaped('oil_cake',['PPP','PWP','PPP'],{'P':{'item':'kaleidoscope_grilling:canola_powder'},'W':{'item':'minecraft:wheat'}},'oil_cake'))
 write(recipes/'big_vat.json',shaped('big_vat',['B B','BUB','BBB'],{'B':{'item':'minecraft:brick_block'},'U':{'item':'minecraft:bucket'}},'big_vat'))
 write(recipes/'oil_press.json',shaped('oil_press',['LIL','F F','LHL'],{'L':{'tag':'minecraft:logs'},'I':{'item':'minecraft:iron_ingot'},'F':{'item':'minecraft:oak_fence'},'H':{'item':'minecraft:hopper'}},'oil_press'))

 labels={
  'zh_TW':{'canola_powder':'菜籽粉','oil_cake':'油餅','oil_residue':'油渣','oil_press':'榨油器','big_vat':'大缸'},
  'zh_CN':{'canola_powder':'菜籽粉','oil_cake':'油饼','oil_residue':'油渣','oil_press':'榨油器','big_vat':'大缸'},
  'en_US':{'canola_powder':'Canola Powder','oil_cake':'Oil Cake','oil_residue':'Oil Residue','oil_press':'Wooden Oil Press','big_vat':'Big Vat'}
 }
 for lang,v in labels.items():
  path=RP/f'texts/{lang}.lang';text=path.read_text(encoding='utf-8')
  rows=[
   ('item.kaleidoscope_grilling:canola_powder.name',v['canola_powder']),
   ('item.kaleidoscope_grilling:oil_cake.name',v['oil_cake']),
   ('item.kaleidoscope_grilling:oil_residue.name',v['oil_residue']),
   ('tile.kaleidoscope_grilling:oil_press.name',v['oil_press']),
   ('tile.kaleidoscope_grilling:big_vat.name',v['big_vat'])
  ]
  for k,val in rows:
   if k+'=' not in text:text+='\n'+k+'='+val
  path.write_text(text.rstrip()+'\n',encoding='utf-8')

def report():
 write(P/'reports/a26-parity.json',{
  'version':'A2.6.0','java_baseline':'breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c',
  'oil_press':{
   'max_cakes':4,'required_progress':16,'anvil_progress':4,'press_stone_progress':1,'player_cooldown_ticks':10,
   'impact_tick':6,'completion_delay_ticks':10,'nearby_scan':[4,2,4],'canola_output_buckets':4,'residue_output':4,
   'waits_for_container':True,'break_returns_unpressed_cakes':True
  },
  'big_vat':{'capacity_buckets':8,'single_fluid':True,'packed_break_state':True,'oil_pot_points_per_bucket':8,'java_visual_levels':4},
  'supported_stable_vat_fluids':['water','lava','canola','secret_chili','premium_chili'],
  'oil_residue_double_growth_approximation':True,
  'known_platform_substitutions':[
   'Forge arbitrary IFluidHandler/third-party fluids are not discoverable through stable Bedrock Script API; the vat supports vanilla water/lava plus all three Grilling oils.',
   'Create funnel/tank automation hooks are unavailable without an installed Bedrock Create compatibility layer; manual machine semantics are preserved.',
   'Oil Residue emulates the two BoneMealItem applications for numeric growth-state crops; non-age bonemeal targets remain a platform gap.',
   'The Java c:fences crafting tag is represented by oak_fence in the A2.6 machine recipe; tag-wide recipe normalization remains in the all-recipes pass.'
  ],
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,5,0]:raise RuntimeError('A2.6 must augment the verified A2.5 baseline')
 patch_manifest();copy_runtime();patch_content();report();print('A2.6 augmentation complete')
if __name__=='__main__':main()
