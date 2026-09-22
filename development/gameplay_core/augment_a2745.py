from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,45]
NEW_FILES=('a2745_skewer_recipe_hud_core.js','a2745_skewer_recipe_hud_provider.js')
LANG={
 'en_US.lang':[
  'jade.kaleidoscope_grilling.skewer_recipe.record=Recorded skewer:',
  'jade.kaleidoscope_grilling.skewer_recipe.ingredients=Required ingredients:',
  'tooltip.kaleidoscope_grilling.recipe_book.wall_usage=Use a stick on a wall-mounted recipe to skewer quickly',
 ],
 'zh_CN.lang':[
  'jade.kaleidoscope_grilling.skewer_recipe.record=记录串类：',
  'jade.kaleidoscope_grilling.skewer_recipe.ingredients=所需食材：',
  'tooltip.kaleidoscope_grilling.recipe_book.wall_usage=可以直接用木棍右键挂墙串谱，快速串签',
 ],
 'zh_TW.lang':[
  'jade.kaleidoscope_grilling.skewer_recipe.record=記錄串類：',
  'jade.kaleidoscope_grilling.skewer_recipe.ingredients=所需食材：',
  'tooltip.kaleidoscope_grilling.recipe_book.wall_usage=可以直接用木棍右鍵掛牆串譜，快速串籤',
 ],
}

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.45 Skewer Recipe HUD Provider BP'),(rm,'Kaleidoscope Grilling A2.7.45 Skewer Recipe HUD Provider RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.45 Skewer Recipe HUD Provider'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_45_Skewer_Recipe_HUD_Provider'
 write(P/'config.json',cfg)

def patch_recipe_runtime():
 p=BP/'scripts/a25_plate_recipe_runtime.js';s=p.read_text(encoding='utf-8')
 anchor='export function a25ReadPlateBlock(block){return readPlateBlock(block)}\n'
 add=anchor+"""export function a25ReadRecipeBlockSnapshot(block){
 const row=readRecipeBlock(block),book=restoreStack(row);if(!book)return null;
 const record=readBookRecord(book);if(!record||typeof record.resultId!=='string'||!record.resultId)return null;
 const slots=bookIngredientSlots(record);
 return {resultId:record.resultId,ingredientSlots:Array.isArray(slots)?slots.map(slot=>[...slot]):[]};
}
"""
 if s.count(anchor)!=1:raise RuntimeError('A2.7.45 plate/recipe export anchor drift')
 if 'a25ReadRecipeBlockSnapshot' in s:raise RuntimeError('A2.7.45 recipe snapshot already exported')
 p.write_text(s.replace(anchor,add,1),encoding='utf-8')

def patch_scripts():
 scripts=BP/'scripts'
 for name in NEW_FILES:shutil.copy2(DEV/name,scripts/name)
 main=scripts/'main.js';s=main.read_text(encoding='utf-8')
 anchor="import './a2744_skewer_plate_hud_provider.js';\n"
 add=anchor+"import './a2745_skewer_recipe_hud_provider.js';\n"
 if s.count(anchor)!=1:raise RuntimeError('A2.7.45 main provider anchor drift')
 if 'a2745_skewer_recipe_hud_provider.js' in s:raise RuntimeError('A2.7.45 provider already active')
 main.write_text(s.replace(anchor,add,1),encoding='utf-8')

def patch_lang():
 for name,lines in LANG.items():
  p=RP/'texts'/name;s=p.read_text(encoding='utf-8');rows=s.splitlines()
  for line in lines:
   key=line.split('=',1)[0]
   if any(row.startswith(key+'=') for row in rows):raise RuntimeError(f'{name}: duplicate localization key {key}')
  if s and not s.endswith('\n'):s+='\n'
  p.write_text(s+'\n'.join(lines)+'\n',encoding='utf-8')

def report():
 write(P/'reports/a2745-skewer-recipe-hud-provider.json',{
  'version':'A2.7.45',
  'scope':'attach wall-mounted Skewer Recipe Java Jade data to shared crosshair HUD using A2.5 recipe state',
  'java_contract':{
   'jade':['record','recorded_item','ingredients','wall_usage'],
   'provider':'SkewerRecipeProvider',
   'entity':'SkewerRecipeBlockEntity'
  },
  'reuse':{
   'shared_crosshair_runtime':'a2739_crosshair_hud_runtime.js',
   'recipe_snapshot':'a25ReadRecipeBlockSnapshot',
   'existing_chain':['readRecipeBlock','restoreStack','readBookRecord','bookIngredientSlots'],
   'single_poll_loop':True,
   'duplicate_recipe_state_parser':False,
   'direct_dynamic_property_access':False
  },
  'ui_adaptation':{
   'java_item_icons':True,
   'bedrock_item_icons':False,
   'localized_item_names':True,
   'ingredient_signature':True
  },
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,44]:raise RuntimeError('A2.7.45 must augment published A2.7.44')
 patch_recipe_runtime();patch_scripts();patch_lang();patch_versions();report()
 print('A2.7.45 Skewer Recipe HUD provider complete')

if __name__=='__main__':main()
