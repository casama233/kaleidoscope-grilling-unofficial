from __future__ import annotations
from pathlib import Path
import argparse,json,re,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
NEW=(
 'a2740_grill_state_adapter.js',
 'a2740_grill_hud_core.js',
 'a2740_grill_hud_provider.js',
)
LANG_KEYS=(
 'hud.kaleidoscope_grilling.grill.title',
 'hud.kaleidoscope_grilling.grill.timer',
 'hud.kaleidoscope_grilling.grill.flips',
 'hud.kaleidoscope_grilling.grill.seasoning.added',
 'hud.kaleidoscope_grilling.grill.seasoning.none',
 'message.kaleidoscope_grilling.grill_ready_to_take',
 'jade.kaleidoscope_grilling.grill.need_heat',
 'jade.kaleidoscope_grilling.grill.empty',
 'jade.kaleidoscope_grilling.grill.need_oil',
 'jade.kaleidoscope_grilling.grill.flipping',
 'jade.kaleidoscope_grilling.grill.need_flip',
 'jade.kaleidoscope_grilling.grill.need_seasoning',
 'jade.kaleidoscope_grilling.grill.ready',
 'jade.kaleidoscope_grilling.grill.burning',
)

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,40] and rm['header']['version']==[2,7,40]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.40 Grill HUD Provider BP'

 for name in NEW:
  assert (BP/'scripts'/name).read_bytes()==(DEV/name).read_bytes(),name

 core=(BP/'scripts/core_logic.js').read_text(encoding='utf-8')
 assert 'export const REQUIRED_FLIPS=4;' in core
 assert 's.flips<=REQUIRED_FLIPS' in core
 assert 'phase:flips>=REQUIRED_FLIPS?2:1' in core
 assert 's.flips<=4' not in core
 assert 'phase:flips>=4?2:1' not in core

 main_text=(BP/'scripts/main.js').read_text(encoding='utf-8')
 state_import="import {grillStateKey as stateKey,readGrillState as readState,occupiedGrillSlots as occupied} from './a2740_grill_state_adapter.js';"
 assert state_import in main_text
 assert main_text.count("import './a2740_grill_hud_provider.js';")==1
 for forbidden in (
  r'function\s+stateKey\s*\(',
  r'function\s+readState\s*\(',
  r'function\s+occupied\s*\(',
 ):
  assert not re.search(forbidden,main_text),forbidden
 assert 'world.setDynamicProperty(stateKey(block),JSON.stringify(state))' in main_text
 assert 'world.setDynamicProperty(stateKey(block))' in main_text

 adapter=(BP/'scripts/a2740_grill_state_adapter.js').read_text(encoding='utf-8')
 for token in ('grillStateKey','readGrillState','occupiedGrillSlots','world.getDynamicProperty','normalizeState','initialState'):
  assert token in adapter,token
 assert 'setDynamicProperty' not in adapter

 provider=(BP/'scripts/a2740_grill_hud_provider.js').read_text(encoding='utf-8')
 for token in ('registerCrosshairHudProvider','readGrillState','occupiedGrillSlots','grillHudView','GRILL_ID'):
  assert token in provider,token
 for forbidden in ('runInterval','getBlockFromViewDirection','getDynamicProperty','setDynamicProperty'):
  assert forbidden not in provider,forbidden

 hud=(BP/'scripts/a2740_grill_hud_core.js').read_text(encoding='utf-8')
 assert "from './core_logic.js';" in hud
 assert 'GRILL_HUD_TIMER_STEP=20' in hud
 assert 'REQUIRED_FLIPS' in hud
 assert 'FINISHED_TICKS' in hud and 'BURNT_TICKS' in hud
 assert "status==='jade.kaleidoscope_grilling.grill.flipping'||status==='jade.kaleidoscope_grilling.grill.need_flip'" in hud
 assert "status==='jade.kaleidoscope_grilling.grill.ready'" in hud
 assert "?'jade.kaleidoscope_grilling.grill.ready'" in hud

 shared=(BP/'scripts/a2739_crosshair_hud_runtime.js').read_text(encoding='utf-8')
 assert shared.count('system.runInterval(')==1
 assert 'registerCrosshairHudProvider' in shared

 for lang in ('en_US.lang','zh_CN.lang','zh_TW.lang'):
  rows=(RP/'texts'/lang).read_text(encoding='utf-8').splitlines()
  for key in LANG_KEYS:
   assert sum(1 for row in rows if row.startswith(key+'='))==1,(lang,key)

 subprocess.run(['node',str(DEV/'test_a2740_core.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2740-grill-hud-provider.json')
 assert report['version']=='A2.7.40'
 assert report['java_contract']['finished_ticks']==800
 assert report['java_contract']['burnt_ticks']==400
 assert report['java_contract']['required_flips']==4
 assert report['reuse']['single_poll_loop'] is True
 assert report['reuse']['duplicate_state_machine'] is False
 assert report['bedrock_adaptation']['timer_sample_ticks']==20
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
  'version':'A2.7.40','grill_hud_provider':True,'shared_crosshair_runtime':True,
  'shared_grill_state_adapter':True,'required_flips_shared':True,
  'timer_sample_ticks':20,'single_poll_loop':True,'duplicate_state_machine':False,
  'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2740-dash-verification.json' if a.compiled else 'a2740-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
