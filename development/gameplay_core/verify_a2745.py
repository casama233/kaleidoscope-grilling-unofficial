from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
NEW=('a2745_skewer_recipe_hud_core.js','a2745_skewer_recipe_hud_provider.js')
LANG_KEYS=(
 'jade.kaleidoscope_grilling.skewer_recipe.record',
 'jade.kaleidoscope_grilling.skewer_recipe.ingredients',
 'tooltip.kaleidoscope_grilling.recipe_book.wall_usage',
)

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,45] and rm['header']['version']==[2,7,45]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.45 Skewer Recipe HUD Provider BP'
 for name in NEW:assert (BP/'scripts'/name).read_bytes()==(DEV/name).read_bytes(),name

 recipe=(BP/'scripts/a25_plate_recipe_runtime.js').read_text(encoding='utf-8')
 assert recipe.count('function readRecipeBlock(block)')==1
 assert recipe.count('function readBookRecord(book)')==1
 assert recipe.count('function restoreStack(row)')==1
 assert recipe.count('bookIngredientSlots(record)')>=2
 assert recipe.count('export function a25ReadRecipeBlockSnapshot(block)')==1
 snapshot=recipe.split('export function a25ReadRecipeBlockSnapshot(block)',1)[1].split('export function a25PlateRows',1)[0]
 for token in ('readRecipeBlock(block)','restoreStack(row)','readBookRecord(book)','bookIngredientSlots(record)'):
  assert token in snapshot,token

 main_text=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert main_text.count("import './a2745_skewer_recipe_hud_provider.js';")==1

 provider=(BP/'scripts/a2745_skewer_recipe_hud_provider.js').read_text(encoding='utf-8')
 for token in ('registerCrosshairHudProvider','a25ReadRecipeBlockSnapshot','skewerRecipeHudView','RECIPE_BLOCK_ID'):
  assert token in provider,token
 for forbidden in ('runInterval','getBlockFromViewDirection','getDynamicProperty','setDynamicProperty','BOOK_RECORD_KEY','readRecipeBlock'):
  assert forbidden not in provider,forbidden

 hud=(BP/'scripts/a2745_skewer_recipe_hud_core.js').read_text(encoding='utf-8')
 for token in ('itemTranslationKey','jade.kaleidoscope_grilling.skewer_recipe.record','jade.kaleidoscope_grilling.skewer_recipe.ingredients','tooltip.kaleidoscope_grilling.recipe_book.wall_usage'):
  assert token in hud,token
 for forbidden in ('getDynamicProperty','setDynamicProperty','BOOK_RECORD_KEY'):
  assert forbidden not in hud,forbidden

 shared=(BP/'scripts/a2739_crosshair_hud_runtime.js').read_text(encoding='utf-8')
 assert shared.count('system.runInterval(')==1
 assert 'registerCrosshairHudProvider' in shared

 for lang in ('en_US.lang','zh_CN.lang','zh_TW.lang'):
  rows=(RP/'texts'/lang).read_text(encoding='utf-8').splitlines()
  for key in LANG_KEYS:assert sum(1 for row in rows if row.startswith(key+'='))==1,(lang,key)

 subprocess.run(['node',str(DEV/'test_a2745_core.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2745-skewer-recipe-hud-provider.json')
 assert report['version']=='A2.7.45'
 assert report['reuse']['single_poll_loop'] is True
 assert report['reuse']['duplicate_recipe_state_parser'] is False
 assert report['reuse']['direct_dynamic_property_access'] is False
 assert report['reuse']['existing_chain']==['readRecipeBlock','restoreStack','readBookRecord','bookIngredientSlots']
 assert report['ui_adaptation']['java_item_icons'] is True
 assert report['ui_adaptation']['bedrock_item_icons'] is False
 assert report['ui_adaptation']['localized_item_names'] is True
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
  'version':'A2.7.45','skewer_recipe_hud_provider':True,'shared_crosshair_runtime':True,
  'existing_recipe_chain_reused':True,'single_poll_loop':True,'duplicate_recipe_state_parser':False,
  'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2745-dash-verification.json' if a.compiled else 'a2745-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
