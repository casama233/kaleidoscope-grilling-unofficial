from __future__ import annotations
from pathlib import Path
import argparse,json,re,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
NEW=(
 'a2743_seasoning_contract_core.js',
 'a2743_seasoning_block_adapter.js',
 'a2743_seasoning_hud_core.js',
 'a2743_seasoning_hud_provider.js',
)
LANG_KEYS=(
 'hud.kaleidoscope_grilling.seasoning.title',
 'hud.kaleidoscope_grilling.seasoning.capacity',
 'hud.kaleidoscope_grilling.seasoning.effects',
 'hud.kaleidoscope_grilling.seasoning.no_effect',
 'hud.kaleidoscope_grilling.seasoning.base.green_chili',
 'hud.kaleidoscope_grilling.seasoning.base.sichuan_pepper',
 'hud.kaleidoscope_grilling.seasoning.base.onion',
 'hud.kaleidoscope_grilling.seasoning.speed',
 'hud.kaleidoscope_grilling.seasoning.strength',
 'hud.kaleidoscope_grilling.seasoning.duration',
 'hud.kaleidoscope_grilling.seasoning.totem',
 'hud.kaleidoscope_grilling.seasoning.vitality',
 'hud.kaleidoscope_grilling.seasoning.numbness',
 'hud.kaleidoscope_grilling.seasoning.numbness_pending',
 'jade.kaleidoscope_grilling.seasoning.capacity',
 'jade.kaleidoscope_grilling.seasoning.uses',
)

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,43] and rm['header']['version']==[2,7,43]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.43 Seasoning Bottle HUD BP'
 for name in NEW:assert (BP/'scripts'/name).read_bytes()==(DEV/name).read_bytes(),name

 contract=(BP/'scripts/a2743_seasoning_contract_core.js').read_text(encoding='utf-8')
 for token in (
  'SEASONING_CAPACITY=8','SEASONING_MAX_BOTTLES=4','SEASONING_MAX_USES=16',
  'SEASONING_VARIANT_MAX=7','BASE_SEASONINGS','SEASONING_KINDS',
  'hasSeasoningBase','seasoningEffectRows','remainingSeasoningUses'
 ):
  assert token in contract,token
 for item,kind in (
  ('minecraft:redstone','speed'),('minecraft:gunpowder','strength'),
  ('kaleidoscope_grilling:houttuynia_powder','duration'),
  ('kaleidoscope_grilling:totem_powder','totem'),
  ('kaleidoscope_grilling:dragon_egg_powder','vitality'),
  ('kaleidoscope_grilling:sichuan_pepper','numbness')
 ):
  assert f"'{item}':'{kind}'" in contract,(item,kind)

 adapter=(BP/'scripts/a2743_seasoning_block_adapter.js').read_text(encoding='utf-8')
 for token in ('seasoningBlockKey','readPlacedSeasoningStack','writePlacedSeasoningStack','topPlacedSeasoningBottle','world.getDynamicProperty','world.setDynamicProperty'):
  assert token in adapter,token

 main_text=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert "from './a2743_seasoning_contract_core.js';" in main_text
 assert "from './a2743_seasoning_block_adapter.js';" in main_text
 assert main_text.count("import './a2743_seasoning_hud_provider.js';")==1
 for forbidden in (
  'const SEASONING_BLOCKS=',
  "const PENDING_SEASONING='kaleidoscope_grilling:pending_seasoning'",
  "const SEASON_LIST_KEY='kaleidoscope_grilling:seasonings'",
  'function isSeasoningBlock(',
  'function seasoningBlockKey(',
  'function readBottleStack(',
  'function writeBottleStack(',
  'function hasSeasoningBase(',
  'function parseList(',
  'Math.min(16,Number(stack?.getDynamicProperty(SEASON_USES_KEY)',
  'Math.min(7,Number(stack.getDynamicProperty(SEASON_VARIANT_KEY)',
  'Math.min(4,count)',
  'top.ingredients.length>=8',
  'Math.floor(Math.random()*8)',
 ):
  assert forbidden not in main_text,forbidden
 for required in (
  'SEASONING_MAX_USES',
  'SEASONING_VARIANT_MAX',
  'SEASONING_MAX_BOTTLES',
  'SEASONING_CAPACITY',
  'normalizeSeasoningList',
  'hasSeasoningBase',
  'SEASONING_KINDS',
 ):
  assert required in main_text,required

 provider=(BP/'scripts/a2743_seasoning_hud_provider.js').read_text(encoding='utf-8')
 for token in ('registerCrosshairHudProvider','isSeasoningBlockId','topPlacedSeasoningBottle','seasoningHudView'):
  assert token in provider,token
 for forbidden in ('runInterval','getBlockFromViewDirection','getDynamicProperty','setDynamicProperty','world.'):
  assert forbidden not in provider,forbidden

 hud=(BP/'scripts/a2743_seasoning_hud_core.js').read_text(encoding='utf-8')
 for token in ('SEASONING_CAPACITY','SEASONING_MAX_USES','remainingSeasoningUses','seasoningEffectRows','BASE_SEASONINGS'):
  assert token in hud,token
 assert 'SEASONING_VARIANT_MAX' not in hud
 assert "statusMessage" not in hud

 shared=(BP/'scripts/a2739_crosshair_hud_runtime.js').read_text(encoding='utf-8')
 assert shared.count('system.runInterval(')==1
 assert 'registerCrosshairHudProvider' in shared

 for lang in ('en_US.lang','zh_CN.lang','zh_TW.lang'):
  rows=(RP/'texts'/lang).read_text(encoding='utf-8').splitlines()
  for key in LANG_KEYS:assert sum(1 for row in rows if row.startswith(key+'='))==1,(lang,key)

 subprocess.run(['node',str(DEV/'test_a2743_core.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2743-seasoning-hud.json')
 assert report['version']=='A2.7.43'
 assert report['java_contract']['capacity']==8
 assert report['java_contract']['max_bottles']==4
 assert report['java_contract']['max_uses']==16
 assert report['java_contract']['variant_range']==[0,7]
 assert report['java_contract']['numbness_threshold']==4
 assert report['reuse']['main_reuses_contract'] is True
 assert report['reuse']['main_reuses_block_adapter'] is True
 assert report['reuse']['provider_direct_dynamic_property_access'] is False
 assert report['reuse']['single_poll_loop'] is True
 assert report['hud']['top_bottle_semantics'] is True
 assert report['hud']['effect_preview'] is True
 assert report['hud']['variant_in_signature'] is True
 assert report['hud']['variant_displayed'] is False
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
  'version':'A2.7.43','seasoning_hud_provider':True,
  'shared_crosshair_runtime':True,'shared_seasoning_contract':True,
  'shared_seasoning_block_adapter':True,'single_poll_loop':True,
  'main_reuses_contract':True,'main_reuses_block_adapter':True,
  'effect_preview':True,'numbness_threshold':4,
  'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2743-dash-verification.json' if a.compiled else 'a2743-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
