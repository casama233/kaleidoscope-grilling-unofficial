from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
SOURCE_RP=ROOT/'projects/grilling/resource_pack'
VERSION=[2,7,47]
SCRIPTS=('a2747_pepper_tree_core.js','a2747_pepper_tree_runtime.js')
BLOCKS={
 'a2747_pepper_log.block.json':'pepper_log.json',
 'a2747_pepper_leaves.block.json':'pepper_leaves.json',
 'a2747_pepper_sapling.block.json':'pepper_sapling.json',
}
LOOT={
 'a2747_pepper_log.loot.json':'pepper_log.json',
 'a2747_pepper_sapling.loot.json':'pepper_sapling.json',
 'a2747_pepper_leaves_fallback.loot.json':'pepper_leaves_fallback.json',
}
GEOS=('pepper_log.geo.json','pepper_leaves.geo.json','pepper_leaves_fruiting.geo.json','pepper_sapling.geo.json')
TEXTURES=('pepper_log.png','pepper_leaves.png','pepper_leaves_fruiting.png','pepper_sapling.png')
LANG={
 'en_US.lang':[
  'tile.kaleidoscope_grilling:pepper_log.name=Pepper Log',
  'tile.kaleidoscope_grilling:pepper_leaves.name=Pepper Leaves',
  'tile.kaleidoscope_grilling:pepper_sapling.name=Pepper Sapling',
 ],
 'zh_CN.lang':[
  'tile.kaleidoscope_grilling:pepper_log.name=花椒原木',
  'tile.kaleidoscope_grilling:pepper_leaves.name=花椒树叶',
  'tile.kaleidoscope_grilling:pepper_sapling.name=花椒树苗',
 ],
 'zh_TW.lang':[
  'tile.kaleidoscope_grilling:pepper_log.name=花椒原木',
  'tile.kaleidoscope_grilling:pepper_leaves.name=花椒樹葉',
  'tile.kaleidoscope_grilling:pepper_sapling.name=花椒樹苗',
 ],
}

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.47 Pepper Tree Lifecycle BP'),(rm,'Kaleidoscope Grilling A2.7.47 Pepper Tree Lifecycle RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.47 Pepper Tree Lifecycle'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_47_Pepper_Tree_Lifecycle'
 write(P/'config.json',cfg)

def patch_scripts():
 scripts=BP/'scripts'
 for name in SCRIPTS:shutil.copy2(DEV/name,scripts/name)
 main=scripts/'main.js';s=main.read_text(encoding='utf-8')
 anchor="import './a2746_advanced_rack_runtime.js';\n"
 add=anchor+"import './a2747_pepper_tree_runtime.js';\n"
 if s.count(anchor)!=1:raise RuntimeError('A2.7.47 main import anchor drift')
 if 'a2747_pepper_tree_runtime.js' in s:raise RuntimeError('A2.7.47 runtime already active')
 main.write_text(s.replace(anchor,add,1),encoding='utf-8')

def patch_behavior_content():
 for src,dst in BLOCKS.items():shutil.copy2(DEV/src,BP/'blocks'/dst)
 loot_dir=BP/'loot_tables/blocks';loot_dir.mkdir(parents=True,exist_ok=True)
 for src,dst in LOOT.items():shutil.copy2(DEV/src,loot_dir/dst)
 shutil.copy2(DEV/'a2747_oak_planks_from_pepper_log.recipe.json',BP/'recipes/oak_planks_from_pepper_log.json')

def patch_resource_content():
 model_dir=RP/'models/blocks';model_dir.mkdir(parents=True,exist_ok=True)
 texture_dir=RP/'textures/blocks';texture_dir.mkdir(parents=True,exist_ok=True)
 for name in GEOS:shutil.copy2(SOURCE_RP/'models/entity/kg_a1'/name,model_dir/name)
 for name in TEXTURES:shutil.copy2(SOURCE_RP/'textures/kg_a1'/name,texture_dir/name)
 terrain=load(RP/'textures/terrain_texture.json');data=terrain.setdefault('texture_data',{})
 aliases={
  'kg_a2747_pepper_log':'textures/blocks/pepper_log',
  'kg_a2747_pepper_leaves':'textures/blocks/pepper_leaves',
  'kg_a2747_pepper_leaves_fruiting':'textures/blocks/pepper_leaves_fruiting',
  'kg_a2747_pepper_sapling':'textures/blocks/pepper_sapling',
 }
 for key,value in aliases.items():
  if key in data:raise RuntimeError(f'terrain alias already exists: {key}')
  data[key]={'textures':value}
 write(RP/'textures/terrain_texture.json',terrain)

def patch_lang():
 for name,lines in LANG.items():
  p=RP/'texts'/name;s=p.read_text(encoding='utf-8');rows=s.splitlines()
  for line in lines:
   key=line.split('=',1)[0]
   if any(row.startswith(key+'=') for row in rows):raise RuntimeError(f'{name}: duplicate localization key {key}')
  if s and not s.endswith('\n'):s+='\n'
  p.write_text(s+'\n'.join(lines)+'\n',encoding='utf-8')

def report():
 write(P/'reports/a2747-pepper-tree-lifecycle.json',{
  'version':'A2.7.47',
  'scope':'Pepper Log/Leaves/Sapling lifecycle and manual tree growth; acquisition/worldgen deferred',
  'java':{
   'sapling_stages':2,'bonemeal_success':0.45,'growth_light':9,'random_growth_denominator':7,
   'tree_height':[2,3],'new_leaf_pepper_chance':0.25,'leaf_refruit_chance':0.05,
   'harvest_pepper':[1,2],'sting_interval_ticks':20,'sting_damage':1,
   'strip_result':'minecraft:stripped_oak_log'
  },
  'reuse':{
   'block_custom_component_pattern':True,
   'shared_player_io':'a2735_player_io.js',
   'preconverted_assets':True,
   'global_poll_loop':False,
   'dirt_tag_first':True
  },
  'deferred':{
   'forest_worldgen':True,'village_chest_acquisition':True,'pepper_picked_advancement':True,
   'continuous_entity_inside_slowdown':True
  },
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,46]:raise RuntimeError('A2.7.47 must augment published A2.7.46')
 patch_scripts();patch_behavior_content();patch_resource_content();patch_lang();patch_versions();report()
 print('A2.7.47 Pepper Tree lifecycle complete')

if __name__=='__main__':main()
