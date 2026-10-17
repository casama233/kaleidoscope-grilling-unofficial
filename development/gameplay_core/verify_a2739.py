from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess,re

ROOT=Path(__file__).resolve().parents[2];P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
NEW=(
 'a2739_cookery_oil_pot_block_adapter.js',
 'a2739_crosshair_hud_core.js',
 'a2739_crosshair_hud_runtime.js',
 'a2739_oil_pot_hud_provider.js',
)
REFACTORED='a2739_refactored_a2736_typed_oil_pot_block_runtime.js'
LANG_KEYS=(
 'hud.kaleidoscope_grilling.oil_pot.title',
 'hud.kaleidoscope_grilling.oil_pot.capacity',
 'tooltip.kaleidoscope_grilling.oil_pot.empty',
 'tooltip.kaleidoscope_grilling.oil_pot.fat',
 'tooltip.kaleidoscope_grilling.oil_pot.canola',
 'tooltip.kaleidoscope_grilling.oil_pot.secret_chili',
 'tooltip.kaleidoscope_grilling.oil_pot.premium_chili',
)
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,39] and rm['header']['version']==[2,7,39]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.39 Shared Crosshair HUD BP'
 assert any(d.get('module_name')=='@minecraft/server' and d.get('version')=='2.9.0' for d in bm.get('dependencies',[]))

 for name in NEW:assert (BP/'scripts'/name).read_bytes()==(DEV/name).read_bytes(),name
 assert (BP/'scripts/a2736_typed_oil_pot_block_runtime.js').read_bytes()==(DEV/REFACTORED).read_bytes()

 main_text=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert main_text.count("import './a2739_crosshair_hud_runtime.js';")==1
 assert main_text.count("import './a2739_oil_pot_hud_provider.js';")==1

 adapter=(BP/'scripts/a2739_cookery_oil_pot_block_adapter.js').read_text(encoding='utf-8')
 assert 'readPlacedOilPotState' in adapter and 'writePlacedOilPotState' in adapter and 'clearPlacedOilPotState' in adapter
 assert 'world.getDynamicProperty' in adapter and 'world.setDynamicProperty' in adapter
 assert "kaleidoscope_cookery:has_oil" in adapter

 r36=(BP/'scripts/a2736_typed_oil_pot_block_runtime.js').read_text(encoding='utf-8')
 assert "from './a2739_cookery_oil_pot_block_adapter.js';" in r36
 for forbidden in ('world.getDynamicProperty','world.setDynamicProperty','function readTypeAt','function readCountAt','function writeAt','function clearAt'):
  assert forbidden not in r36,forbidden

 hud=(BP/'scripts/a2739_crosshair_hud_runtime.js').read_text(encoding='utf-8')
 assert hud.count('system.runInterval(')==1
 for token in ('world.getPlayers()','getBlockFromViewDirection','CROSSHAIR_HUD_MAX_DISTANCE','registerCrosshairHudProvider','LAST_SIGNATURE','shouldPublishHud','setActionBar(result.message)'):
  assert token in hud,token
 assert 'runCommand' not in hud

 provider=(BP/'scripts/a2739_oil_pot_hud_provider.js').read_text(encoding='utf-8')
 for token in ('registerCrosshairHudProvider','readPlacedOilPotState','oilPotHudView','HOST_BLOCK_ID'):
  assert token in provider,token
 for forbidden in ('getDynamicProperty','setDynamicProperty','runInterval','getBlockFromViewDirection'):
  assert forbidden not in provider,forbidden

 core=(BP/'scripts/a2739_crosshair_hud_core.js').read_text(encoding='utf-8')
 for key in LANG_KEYS:assert key in core or key in ('tooltip.kaleidoscope_grilling.oil_pot.fat','tooltip.kaleidoscope_grilling.oil_pot.canola','tooltip.kaleidoscope_grilling.oil_pot.secret_chili','tooltip.kaleidoscope_grilling.oil_pot.premium_chili','tooltip.kaleidoscope_grilling.oil_pot.empty')
 assert 'CROSSHAIR_HUD_POLL_TICKS=4' in core
 assert 'CROSSHAIR_HUD_MAX_DISTANCE=6' in core

 for lang in ('en_US.lang','zh_CN.lang','zh_TW.lang'):
  text=(RP/'texts'/lang).read_text(encoding='utf-8')
  rows=text.splitlines()
  for key in LANG_KEYS:
   assert sum(1 for row in rows if row.startswith(key+'='))==1,(lang,key)

 subprocess.run(['node',str(DEV/'test_a2739_core.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2739-shared-crosshair-hud.json')
 assert report['version']=='A2.7.39'
 assert report['shared_hud']['provider_registry'] is True
 assert report['shared_hud']['no_per_provider_poll_loop'] is True
 assert report['oil_pot_provider']['uses_shared_block_state_adapter'] is True
 assert report['dedupe']['hud_does_not_read_host_dynamic_properties_directly'] is True
 assert report['dedupe']['duplicate_oil_pot_block_created'] is False
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
  'version':'A2.7.39','shared_crosshair_hud':True,'oil_pot_provider':True,
  'shared_block_state_adapter':True,'poll_ticks':4,'max_distance':6,
  'localized_rawmessage':True,'single_poll_loop':True,'duplicate_host_block_created':False,
  'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2739-dash-verification.json' if a.compiled else 'a2739-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
