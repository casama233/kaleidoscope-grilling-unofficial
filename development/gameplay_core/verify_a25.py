from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
COOKERY_BP='10f37ae2-9ccf-435f-b34b-0eec8191cd94';COOKERY_RP='c89dc8df-c3fc-4bc8-8bd0-527abba76681';CV=[1,0,6]

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def blob(p):
 v=p.read_bytes();return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,5,0] and rm['header']['version']==[2,5,0]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.5 Gameplay BP'
 assert rm['header']['name']=='Kaleidoscope Grilling A2.5 Gameplay RP'
 assert {'uuid':COOKERY_BP,'version':CV} in bm['dependencies'] and {'uuid':COOKERY_RP,'version':CV} in rm['dependencies']
 assert {'module_name':'@minecraft/server','version':'2.9.0'} in bm['dependencies']

 plate=load(BP/'items/skewer_plate.json')['minecraft:item']
 book=load(BP/'items/skewer_recipe_book.json')['minecraft:item']
 assert plate['description']['identifier']=='kaleidoscope_grilling:skewer_plate'
 assert plate['components']['minecraft:max_stack_size']==1
 assert plate['components']['minecraft:food']['nutrition']==0
 assert plate['components']['minecraft:use_modifiers']['use_duration']==0.8
 assert book['description']['identifier']=='kaleidoscope_grilling:skewer_recipe_book'
 assert book['components']['minecraft:max_stack_size']==1
 assert book['components']['minecraft:food']['nutrition']==0

 block=load(BP/'blocks/skewer_plate_block.json')['minecraft:block']
 assert block['description']['identifier']=='kaleidoscope_grilling:skewer_plate_block'
 assert block['description']['states']['kaleidoscope_grilling:plate_count']==[0,1,2,3,4,5]
 recipe=load(BP/'blocks/skewer_recipe.json')['minecraft:block']
 assert recipe['description']['identifier']=='kaleidoscope_grilling:skewer_recipe'
 assert len(recipe['permutations'])==4

 item_tex=load(RP/'textures/item_texture.json')['texture_data']
 terrain=load(RP/'textures/terrain_texture.json')['texture_data']
 assert item_tex['skewer_plate']['textures']=='textures/items/skewer_plate'
 assert item_tex['skewer_recipe_book']['textures']=='textures/items/skewer_recipe_book'
 assert terrain['kg_a25_plate']['textures']=='textures/blocks/skewer_plate'
 assert terrain['kg_a25_recipe']['textures']=='textures/blocks/skewer_recipe'
 assert blob(RP/'textures/items/skewer_recipe_book.png')=='825261abf54bd2afa042e36196511bda302841b3'
 assert blob(RP/'textures/items/skewer_plate.png')=='f2e6b208b55b9b3d6d4011216355f01517e0210b'
 assert blob(RP/'textures/blocks/skewer_plate.png')=='f2e6b208b55b9b3d6d4011216355f01517e0210b'
 assert blob(RP/'textures/blocks/skewer_recipe.png')=='13d45f089746f0d375b817d628b61b7a2c24dd7c'

 for name in ('a25_plate_recipe_core.js','a25_plate_recipe_runtime.js'):assert (BP/'scripts'/name).is_file(),name
 core=(BP/'scripts/a25_plate_recipe_core.js').read_text(encoding='utf-8')
 for token in ('PLATE_CAPACITY=5','plateRemoveLast','plateHighestNutritionIndex','bookIngredientSlots','planInventoryConsumption'):assert token in core,token
 runtime=(BP/'scripts/a25_plate_recipe_runtime.js').read_text(encoding='utf-8')
 for token in ('PLATE_BLOCK_ID','readPlateBlock','writePlateBlock','breakPlate','craftFromBook','placeRecipeBlock','convertCookeryRecipe','playerBreakBlock'):assert token in runtime,token
 main=(BP/'scripts/main.js').read_text(encoding='utf-8')
 for token in ('PLATE_EATS','completePlateUse','a25PlateRows','a25PlateItem','a25RestoreStack','plateHighestNutritionIndex'):assert token in main,token

 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a24_core.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a25_core.mjs')],check=True)

 parity=load(P/'reports/a25-parity.json')
 assert parity['version']=='A2.5.0' and parity['plate_capacity']==5
 assert parity['plate_lifo_take'] and parity['packed_metadata'] and parity['plate_highest_nutrition_eating']
 assert parity['recipe_book_fixed_and_secret_recording'] and parity['recipe_book_inventory_autocraft'] and parity['wall_recipe_block']

 compiled=[]
 if a.compiled:
  dist=P/'builds/dist'
  for name,source in [('behavior_pack',BP),('resource_pack',RP)]:
   manifest=load(source/'manifest.json')
   matches=[p.parent for p in dist.rglob('manifest.json') if load(p).get('header',{}).get('uuid')==manifest['header']['uuid']]
   assert len(matches)==1,(name,matches);target=matches[0];count=0
   for p in source.rglob('*'):
    if not p.is_file() or p.name.startswith('.'):continue
    q=target/p.relative_to(source);assert q.is_file(),str(q)
    if p.suffix=='.json':assert load(p)==load(q),str(q)
    else:assert p.read_bytes()==q.read_bytes(),str(q)
    count+=1
   compiled.append({'pack':name,'compared_files':count,'matches_source':True})

 result={
  'version':'A2.5.0','plate_capacity':5,'plate_lifo_take':True,'packed_metadata':True,
  'highest_nutrition_eating':True,'recipe_book_fixed_and_secret':True,'inventory_autocraft':True,
  'wall_recipe_block':True,'server_module':'2.9.0','compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a25-dash-verification.json' if a.compiled else 'a25-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
