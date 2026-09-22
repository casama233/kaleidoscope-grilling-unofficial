from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
SOURCE_RP=ROOT/'projects/grilling/resource_pack'
SCRIPTS=('a2748_pepper_tree_core.js','a2748_pepper_tree_runtime.js')
BLOCKS={
 'pepper_log.json':'a2748_pepper_log.block.json',
 'pepper_leaves.json':'a2748_pepper_leaves.block.json',
 'pepper_sapling.json':'a2748_pepper_sapling.block.json',
}
LOOT={
 'pepper_log.json':'a2748_pepper_log.loot.json',
 'pepper_sapling.json':'a2748_pepper_sapling.loot.json',
 'pepper_leaves_fallback.json':'a2748_pepper_leaves_fallback.loot.json',
}
GEOS=('pepper_log.geo.json','pepper_leaves.geo.json','pepper_leaves_fruiting.geo.json','pepper_sapling.geo.json')
TEXTURES=('pepper_log.png','pepper_leaves.png','pepper_leaves_fruiting.png','pepper_sapling.png')
LANG_KEYS=(
 'tile.kaleidoscope_grilling:pepper_log.name',
 'tile.kaleidoscope_grilling:pepper_leaves.name',
 'tile.kaleidoscope_grilling:pepper_sapling.name',
)

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,47] and rm['header']['version']==[2,7,47]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.48 Pepper Tree Lifecycle BP'
 for name in SCRIPTS:assert (BP/'scripts'/name).read_bytes()==(DEV/name).read_bytes(),name
 for dst,src in BLOCKS.items():assert (BP/'blocks'/dst).read_bytes()==(DEV/src).read_bytes(),dst
 for dst,src in LOOT.items():assert (BP/'loot_tables/blocks'/dst).read_bytes()==(DEV/src).read_bytes(),dst
 assert (BP/'recipes/oak_planks_from_pepper_log.json').read_bytes()==(DEV/'a2748_oak_planks_from_pepper_log.recipe.json').read_bytes()

 log=load(BP/'blocks/pepper_log.json')['minecraft:block']
 assert log['description']['identifier']=='kaleidoscope_grilling:pepper_log'
 assert log['description']['traits']['minecraft:placement_position']['enabled_states']==['minecraft:block_face']
 assert log['components']['minecraft:geometry']=='geometry.kg_a1.pepper_log'
 assert 'kaleidoscope_grilling:pepper_log_logic' in log['components']
 leaves=load(BP/'blocks/pepper_leaves.json')['minecraft:block']
 assert leaves['description']['states']['kaleidoscope_grilling:has_pepper']==[False,True]
 assert leaves['description']['states']['kaleidoscope_grilling:persistent']==[False,True]
 assert leaves['components']['minecraft:collision_box']=={'origin':[-8,15,-8],'size':[16,1,16]}
 assert any(x['components'].get('minecraft:geometry')=='geometry.kg_a1.pepper_leaves_fruiting' for x in leaves['permutations'])
 sapling=load(BP/'blocks/pepper_sapling.json')['minecraft:block']
 assert sapling['description']['states']['kaleidoscope_grilling:stage']==[0,1]
 assert sapling['components']['minecraft:collision_box'] is False

 recipe=load(BP/'recipes/oak_planks_from_pepper_log.json')['minecraft:recipe_shapeless']
 assert recipe['ingredients']==[{'item':'kaleidoscope_grilling:pepper_log'}]
 assert recipe['result']=={'item':'minecraft:oak_planks','count':4}

 terrain=load(RP/'textures/terrain_texture.json')['texture_data']
 aliases={
  'kg_a2748_pepper_log':'textures/blocks/pepper_log',
  'kg_a2748_pepper_leaves':'textures/blocks/pepper_leaves',
  'kg_a2748_pepper_leaves_fruiting':'textures/blocks/pepper_leaves_fruiting',
  'kg_a2748_pepper_sapling':'textures/blocks/pepper_sapling',
 }
 for key,value in aliases.items():assert terrain[key]=={'textures':value},key
 for name in GEOS:
  actual=RP/'models/blocks'/name;source=SOURCE_RP/'models/entity/kg_a1'/name
  assert actual.read_bytes()==source.read_bytes(),name
  ident=load(actual)['minecraft:geometry'][0]['description']['identifier']
  assert ident==f"geometry.kg_a1.{name.removesuffix('.geo.json')}",ident
 for name in TEXTURES:
  assert (RP/'textures/blocks'/name).read_bytes()==(SOURCE_RP/'textures/kg_a1'/name).read_bytes(),name

 main_text=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert main_text.count("import './a2748_pepper_tree_runtime.js';")==1
 core=(BP/'scripts/a2748_pepper_tree_core.js').read_text(encoding='utf-8')
 for token in ('pepperTreePlan','pepperLeafBreakPlan','saplingBonemealSucceeds','pepperLogAxis','STING_INTERVAL_TICKS=20'):
  assert token in core,token
 runtime=(BP/'scripts/a2748_pepper_tree_runtime.js').read_text(encoding='utf-8')
 for token in ('registerCustomComponent(LEAVES_COMPONENT_ID','registerCustomComponent(SAPLING_COMPONENT_ID','registerCustomComponent(LOG_COMPONENT_ID',
               "block?.hasTag('dirt')","world.beforeEvents.playerBreakBlock.subscribe","BlockPermutation.resolve('minecraft:stripped_oak_log'",
               'a2735_player_io.js','connectedToPepperLog','placePepperTree'):
  assert token in runtime,token
 assert 'system.runInterval(' not in runtime
 assert "entity.typeId==='minecraft:fox'" in runtime and "entity.typeId==='minecraft:bee'" in runtime

 for lang in ('en_US.lang','zh_CN.lang','zh_TW.lang'):
  rows=(RP/'texts'/lang).read_text(encoding='utf-8').splitlines()
  for key in LANG_KEYS:assert sum(1 for row in rows if row.startswith(key+'='))==1,(lang,key)

 subprocess.run(['node',str(DEV/'test_a2748_core.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2748-pepper-tree-lifecycle.json')
 assert report['version']=='A2.7.48'
 assert report['java']['sapling_stages']==2
 assert report['java']['bonemeal_success']==0.45
 assert report['java']['tree_height']==[2,3]
 assert report['reuse']['preconverted_assets'] is True
 assert report['reuse']['global_poll_loop'] is False
 assert report['deferred']['forest_worldgen'] is True
 assert report['deferred']['village_chest_acquisition'] is True
 assert report['minecraft_tested'] is False and report['bds_tested'] is False

 compiled=[]
 if a.compiled:
  dist=P/'builds/dist'
  for name,source in [('behavior_pack',BP),('resource_pack',RP)]:
   manifest=load(source/'manifest.json')
   matches=[x.parent for x in dist.rglob('manifest.json') if load(x).get('header',{}).get('uuid')==manifest['header']['uuid']]
   assert len(matches)==1,(name,matches);target=matches[0];count=0
   for p in source.rglob('*'):
    if not p.is_file() or p.name.startswith('.'):continue
    q=target/p.relative_to(source);assert q.is_file(),str(q)
    if p.suffix=='.json':assert load(p)==load(q),str(q)
    else:assert p.read_bytes()==q.read_bytes(),str(q)
    count+=1
   compiled.append({'pack':name,'compared_files':count,'matches_source':True})

 result={
  'version':'A2.7.48','pepper_tree_lifecycle':True,'sapling_growth':True,'leaf_fruiting':True,
  'leaf_harvest':True,'leaf_decay':True,'pepper_sting':True,'log_stripping':True,
  'preconverted_assets_reused':True,'forest_worldgen':False,'village_acquisition':False,
  'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2748-dash-verification.json' if a.compiled else 'a2748-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
