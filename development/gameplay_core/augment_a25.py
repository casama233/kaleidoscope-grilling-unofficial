from __future__ import annotations
import hashlib,json,shutil,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'projects/grilling'
P=SRC/'gameplay_core'
BP=P/'behavior_pack'
RP=P/'resource_pack'
DEV=Path(__file__).parent
VERSION=[2,5,0]
GRILL_UP='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
COOKERY_UP='https://raw.githubusercontent.com/KaleidoscopeMods/KaleidoscopeCookery/a94bf82a162056d254c68989442d1708eb4a98b0/'
ASSETS={
 'book':(GRILL_UP,'common/src/main/resources/assets/kaleidoscope_grilling/textures/item/skewer_recipe_book.png','825261abf54bd2afa042e36196511bda302841b3'),
 'plate':(COOKERY_UP,'src/main/resources/assets/kaleidoscope_cookery/textures/block/plate.png','f2e6b208b55b9b3d6d4011216355f01517e0210b'),
 'recipe':(COOKERY_UP,'src/main/resources/assets/kaleidoscope_cookery/textures/block/recipe_block.png','13d45f089746f0d375b817d628b61b7a2c24dd7c'),
}

def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(base,path,sha):
 req=urllib.request.Request(base+path,headers={'User-Agent':'Grilling-A2.5/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 if blob(v)!=sha:raise RuntimeError('pinned upstream mismatch '+path)
 return v
def load(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def write(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 if isinstance(data,(dict,list)):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 else:path.write_text(data,encoding='utf-8')
def replace_once(text,old,new,label):
 if old not in text:raise RuntimeError('A2.5 patch anchor missing: '+label)
 return text.replace(old,new,1)

def patch_manifest():
 bm=load(BP/'manifest.json');rm=load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.5 Gameplay BP'),(rm,'Kaleidoscope Grilling A2.5 Gameplay RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.5 Gameplay';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_5';write(P/'config.json',cfg)

def copy_runtime():
 shutil.copy2(DEV/'a25_plate_recipe_core.js',BP/'scripts/a25_plate_recipe_core.js')
 shutil.copy2(DEV/'a25_plate_recipe_runtime.js',BP/'scripts/a25_plate_recipe_runtime.js')

def patch_items_blocks_assets():
 write(BP/'items/skewer_plate.json',{
  'format_version':'1.26.30','minecraft:item':{
   'description':{'identifier':'kaleidoscope_grilling:skewer_plate','menu_category':{'category':'items'}},
   'components':{
    'minecraft:display_name':{'value':'item.kaleidoscope_grilling:skewer_plate.name'},
    'minecraft:icon':{'textures':{'default':'skewer_plate'}},
    'minecraft:max_stack_size':1,'minecraft:allow_off_hand':True,
    'minecraft:use_modifiers':{'start_using':'always','use_duration':0.8,'movement_modifier':0.35},
    'minecraft:food':{'can_always_eat':True,'nutrition':0,'saturation_modifier':0.0},
    'minecraft:use_animation':{'value':'eat'},'minecraft:tags':{'tags':['minecraft:is_food']}
   }
  }
 })
 # Food(0) is intentionally a cancellable stable item-use trigger. Runtime cancels every book use.
 write(BP/'items/skewer_recipe_book.json',{
  'format_version':'1.26.30','minecraft:item':{
   'description':{'identifier':'kaleidoscope_grilling:skewer_recipe_book','menu_category':{'category':'items'}},
   'components':{
    'minecraft:display_name':{'value':'item.kaleidoscope_grilling:skewer_recipe_book.name'},
    'minecraft:icon':{'textures':{'default':'skewer_recipe_book'}},
    'minecraft:max_stack_size':1,'minecraft:allow_off_hand':True,
    'minecraft:use_modifiers':{'start_using':'always','use_duration':0.1,'movement_modifier':1.0},
    'minecraft:food':{'can_always_eat':True,'nutrition':0,'saturation_modifier':0.0},
    'minecraft:use_animation':{'value':'eat'}
   }
  }
 })
 write(BP/'blocks/skewer_plate_block.json',{
  'format_version':'1.26.50','minecraft:block':{
   'description':{'identifier':'kaleidoscope_grilling:skewer_plate_block','states':{'kaleidoscope_grilling:plate_count':[0,1,2,3,4,5]}},
   'components':{
    'minecraft:display_name':'tile.kaleidoscope_grilling:skewer_plate.name',
    'minecraft:geometry':'geometry.kg_a25.skewer_plate',
    'minecraft:material_instances':{'*':{'texture':'kg_a25_plate','render_method':'alpha_test','ambient_occlusion':1.0,'face_dimming':True}},
    'minecraft:collision_box':{'origin':[-7,0,-7],'size':[14,7,14]},
    'minecraft:selection_box':{'origin':[-7,0,-7],'size':[14,7,14]},
    'minecraft:destructible_by_mining':{'seconds_to_destroy':0.5},
    'minecraft:destructible_by_explosion':{'explosion_resistance':1.0}
   }
  }
 })
 recipe_block={
  'format_version':'1.26.50','minecraft:block':{
   'description':{
    'identifier':'kaleidoscope_grilling:skewer_recipe',
    'traits':{'minecraft:placement_direction':{'enabled_states':['minecraft:cardinal_direction']}}
   },
   'components':{
    'minecraft:display_name':'tile.kaleidoscope_grilling:skewer_recipe.name',
    'minecraft:geometry':'geometry.kg_a25.skewer_recipe',
    'minecraft:material_instances':{'*':{'texture':'kg_a25_recipe','render_method':'alpha_test','ambient_occlusion':False,'face_dimming':False}},
    'minecraft:collision_box':False,
    'minecraft:selection_box':{'origin':[-6,1.5,7.5],'size':[12,13,0.5]},
    'minecraft:destructible_by_mining':{'seconds_to_destroy':0.2},
    'minecraft:destructible_by_explosion':{'explosion_resistance':0.2}
   },
   'permutations':[]
  }
 }
 for direction,rot in [('north',0),('south',180),('west',90),('east',270)]:
  recipe_block['minecraft:block']['permutations'].append({
   'condition':f"q.block_state('minecraft:cardinal_direction') == '{direction}'",
   'components':{'minecraft:transformation':{'rotation':[0,rot,0]}}
  })
 write(BP/'blocks/skewer_recipe.json',recipe_block)

 plate_geo={
  'format_version':'1.16.0','minecraft:geometry':[{
   'description':{'identifier':'geometry.kg_a25.skewer_plate','texture_width':16,'texture_height':16,'visible_bounds_width':2,'visible_bounds_height':1,'visible_bounds_offset':[0,.25,0]},
   'bones':[{'name':'root','pivot':[0,0,0],'cubes':[{
    'origin':[-7,0,-7],'size':[14,2,14],
    'uv':{
     'north':{'uv':[1,0],'uv_size':[14,2]},'east':{'uv':[1,0],'uv_size':[14,2]},
     'south':{'uv':[1,0],'uv_size':[14,2]},'west':{'uv':[1,0],'uv_size':[14,2]},
     'up':{'uv':[1,1],'uv_size':[14,14]},'down':{'uv':[1,1],'uv_size':[14,14]}
    }
   }]}]
  }]
 }
 recipe_geo={
  'format_version':'1.16.0','minecraft:geometry':[{
   'description':{'identifier':'geometry.kg_a25.skewer_recipe','texture_width':32,'texture_height':32,'visible_bounds_width':2,'visible_bounds_height':2,'visible_bounds_offset':[0,.5,0]},
   'bones':[{'name':'root','pivot':[0,8,0],'cubes':[{
    'origin':[-6,1.5,7.75],'size':[12,13,.25],
    'uv':{
     'north':{'uv':[0,0],'uv_size':[12,14]},'south':{'uv':[0,0],'uv_size':[12,14]},
     'east':{'uv':[0,0],'uv_size':[1,13]},'west':{'uv':[0,0],'uv_size':[1,13]},
     'up':{'uv':[0,0],'uv_size':[12,1]},'down':{'uv':[0,0],'uv_size':[12,1]}
    }
   }]}]
  }]
 }
 write(RP/'models/blocks/skewer_plate.geo.json',plate_geo);write(RP/'models/blocks/skewer_recipe.geo.json',recipe_geo)

 tex=load(RP/'textures/item_texture.json')
 tex['texture_data']['skewer_plate']={'textures':'textures/items/skewer_plate'}
 tex['texture_data']['skewer_recipe_book']={'textures':'textures/items/skewer_recipe_book'}
 write(RP/'textures/item_texture.json',tex)
 terrain=load(RP/'textures/terrain_texture.json')
 terrain['texture_data']['kg_a25_plate']={'textures':'textures/blocks/skewer_plate'}
 terrain['texture_data']['kg_a25_recipe']={'textures':'textures/blocks/skewer_recipe'}
 write(RP/'textures/terrain_texture.json',terrain)
 raw_plate=fetch(*ASSETS['plate']);raw_recipe=fetch(*ASSETS['recipe']);raw_book=fetch(*ASSETS['book'])
 (RP/'textures/items/skewer_plate.png').write_bytes(raw_plate)
 (RP/'textures/blocks/skewer_plate.png').write_bytes(raw_plate)
 (RP/'textures/blocks/skewer_recipe.png').write_bytes(raw_recipe)
 (RP/'textures/items/skewer_recipe_book.png').write_bytes(raw_book)

 labels={
  'zh_TW':('有烤串的盤子','烤串盤','串譜','串譜'),
  'zh_CN':('有烤串的盘子','烤串盘','串谱','串谱'),
  'en_US':('Plate of Skewers','Skewer Plate','Skewer Recipe Book','Skewer Recipe')
 }
 for lang,(item_plate,block_plate,book,recipe) in labels.items():
  path=RP/f'texts/{lang}.lang';text=path.read_text(encoding='utf-8')
  rows=[
   ('item.kaleidoscope_grilling:skewer_plate.name',item_plate),
   ('tile.kaleidoscope_grilling:skewer_plate.name',block_plate),
   ('tile.kaleidoscope_grilling:skewer_plate_block.name',block_plate),
   ('item.kaleidoscope_grilling:skewer_recipe_book.name',book),
   ('tile.kaleidoscope_grilling:skewer_recipe.name',recipe),
  ]
  for key,value in rows:
   if key+'=' not in text:text+='\n'+key+'='+value
  path.write_text(text.rstrip()+'\n',encoding='utf-8')

def patch_main_runtime():
 path=BP/'scripts/main.js';s=path.read_text(encoding='utf-8')
 old="import {UNFINISHED_ID,SECRET_ID,SKEWER_INGREDIENTS_KEY,SECRET_COOKED_KEY,SECRET_COOKED_INGREDIENTS_KEY,SECRET_CREATOR_KEY,FLUID_CAPACITY,appendOutcome,secretFood,isDisassemblableRaw} from './a24_skewering_core.js';"
 new=old+"\nimport {PLATE_ID,plateHighestNutritionIndex} from './a25_plate_recipe_core.js';\nimport {a25PlateRows,a25PlateItem,a25RestoreStack} from './a25_plate_recipe_runtime.js';"
 s=replace_once(s,old,new,'A2.5 imports')
 s=replace_once(s,
  "const ACTIVE_EATS=new Map(),SETTLED=new Map(),VIGOR_LAST=new Map(),SNEAK_LAST=new Map(),SEASON_PLACE_CACHE=new Map(),THREAD_LAST=new Map();",
  "const ACTIVE_EATS=new Map(),PLATE_EATS=new Map(),SETTLED=new Map(),VIGOR_LAST=new Map(),SNEAK_LAST=new Map(),SEASON_PLACE_CACHE=new Map(),THREAD_LAST=new Map();",
  'plate eat state')
 old_fn="function addSecretNutrition(player,stack,meta){\n const d=dynamicFood(stack),h=player.getComponent('minecraft:player.hunger'),sat=player.getComponent('minecraft:player.saturation');if(!d||!h||!sat)return;\n const hunger=Math.min(h.effectiveMax,h.currentValue+d.nutrition);h.setCurrentValue(hunger);\n const gain=d.nutrition*d.saturation*2*(meta?.hot?1.25:1);sat.setCurrentValue(Math.min(hunger,sat.currentValue+gain));\n}"
 new_fn=old_fn+"\nfunction addNestedNutrition(player,stack,meta){addSecretNutrition(player,stack,meta)}"
 s=replace_once(s,old_fn,new_fn,'nested plate nutrition')
 marker="function completePending(player,stack){"
 plate_fn="""function completePlateUse(player,eventStack){
 const a=PLATE_EATS.get(player.id)??{plate:eventStack,hand:'main',nativeBefore:{},fxBefore:{},saturationBefore:undefined};PLATE_EATS.delete(player.id);
 const rows=a25PlateRows(a.plate??eventStack),index=plateHighestNutritionIndex(rows);if(index<0){setHand(player,a.hand,undefined);return}
 const row=rows.splice(index,1)[0],eaten=a25RestoreStack(row);if(!eaten){setHand(player,a.hand,rows.length?a25PlateItem(rows,a.plate):undefined);return}
 const id=eaten.typeId,meta=stackMeta(eaten);dangerousPreservation(player,id);addNestedNutrition(player,eaten,meta);
 if(id===SECRET_ID)secretRemainders(player,eaten);
 if(RAW_NAUSEA[id])try{player.addEffect('nausea',60,{showParticles:true})}catch{};if(id===MYSTERIOUS_ID)try{player.addEffect('nausea',100,{showParticles:true})}catch{};if(id===DARK_ID)try{player.addEffect('blindness',200,{showParticles:true})}catch{}
 afterCommitted(player,id,meta,{...a,meta},false);setHand(player,a.hand,rows.length?a25PlateItem(rows,a.plate):undefined);
}
"""
 s=replace_once(s,marker,plate_fn+marker,'plate completion helper')
 old_start=""" if(id===PENDING_SEASONING){const hand=handFor(e.source,id)?.name??'main';try{e.source.playAnimation('animation.kg_a21.player.shake.'+hand,{blendOutTime:.08})}catch{}return}
 if(!FOOD_DATA[id]&&id!==SECRET_ID)return;"""
 new_start=""" if(id===PENDING_SEASONING){const hand=handFor(e.source,id)?.name??'main';try{e.source.playAnimation('animation.kg_a21.player.shake.'+hand,{blendOutTime:.08})}catch{}return}
 if(id===PLATE_ID){
  const rows=a25PlateRows(e.itemStack),index=plateHighestNutritionIndex(rows);if(index<0)return;
  const selected=a25RestoreStack(rows[index]),meta=stackMeta(selected),sat=e.source.getComponent('minecraft:player.saturation'),hand=handFor(e.source,id)?.name??'main';
  PLATE_EATS.set(e.source.id,{id,plate:e.itemStack.clone(),hand,meta,nativeBefore:meta.hot?nativeSnapshot(e.source):{},fxBefore:meta.hot?fxSnapshot(e.source):{},saturationBefore:meta.hot?sat?.currentValue:undefined});return;
 }
 if(!FOOD_DATA[id]&&id!==SECRET_ID)return;"""
 s=replace_once(s,old_start,new_start,'plate start use')
 old_complete=""" const id=e.itemStack?.typeId;if(id===PENDING_SEASONING){completePending(e.source,e.itemStack);return}
 dangerousPreservation(e.source,id);if(!FOOD_DATA[id]&&id!==SECRET_ID)return;"""
 new_complete=""" const id=e.itemStack?.typeId;if(id===PENDING_SEASONING){completePending(e.source,e.itemStack);return}
 if(id===PLATE_ID){completePlateUse(e.source,e.itemStack);return}
 dangerousPreservation(e.source,id);if(!FOOD_DATA[id]&&id!==SECRET_ID)return;"""
 s=replace_once(s,old_complete,new_complete,'plate complete use')
 path.write_text(s,encoding='utf-8')

def report():
 out=P/'reports'/'a25-parity.json'
 write(out,{
  'version':'A2.5.0','java_baseline':'breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c',
  'scope':['SkewerPlateBlock','SkewerPlateBlockEntity','SkewerPlateItem','SkewerPlatePlacement','SkewerRecipeBookItem','SkewerRecipeBlock','SkewerRecipeBlockEntity'],
  'plate_capacity':5,'plate_lifo_take':True,'packed_metadata':True,'plate_highest_nutrition_eating':True,
  'recipe_book_fixed_and_secret_recording':True,'recipe_book_inventory_autocraft':True,'wall_recipe_block':True,
  'bedrock_internal_plate_block_id':'kaleidoscope_grilling:skewer_plate_block',
  'known_platform_substitutions':[
   'Java BlockItem cannot be both an edible custom item and a Bedrock custom block with the same runtime identifier, so the world block uses an internal _block id.',
   'Java shapeless NBT recipe recording is represented by a stable two-hand recording action; Cookery recipe item + recorded raw skewer is also intercepted when available.',
   'Plate base and recipe paper use pinned upstream textures; arbitrary per-skewer block-entity rendering remains a static plate visual until a Bedrock renderer equivalent is added.'
  ],
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,4,0]:raise RuntimeError('A2.5 must augment the verified A2.4 baseline')
 patch_manifest();copy_runtime();patch_items_blocks_assets();patch_main_runtime();report()
 print('A2.5 augmentation complete')

if __name__=='__main__':main()
