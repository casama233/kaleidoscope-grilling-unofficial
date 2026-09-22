from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
NEW=('a2741_oil_press_hud_core.js','a2741_oil_press_hud_provider.js')
LANG_KEYS=(
 'hud.kaleidoscope_grilling.press.title',
 'hud.kaleidoscope_grilling.press.cakes',
 'hud.kaleidoscope_grilling.press.progress',
 'hud.kaleidoscope_grilling.press.vat.none',
 'hud.kaleidoscope_grilling.press.vat.found',
 'hud.kaleidoscope_grilling.press.vat.wrong',
 'hud.kaleidoscope_grilling.press.vat.full',
)

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,41] and rm['header']['version']==[2,7,41]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.41 Oil Press HUD Provider BP'
 for name in NEW:assert (BP/'scripts'/name).read_bytes()==(DEV/name).read_bytes(),name

 oil=(BP/'scripts/a26_oil_machine_runtime.js').read_text(encoding='utf-8')
 assert oil.count('function scanVat(press)')==1
 assert oil.count('export function a26ReadPress(block){return readPress(block)}')==1
 assert oil.count('export function a26ReadVat(block){return readVat(block)}')==1
 assert oil.count('export function a26ProbePressContainer(block){return scanVat(block)}')==1

 main_text=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert main_text.count("import './a2741_oil_press_hud_provider.js';")==1

 provider=(BP/'scripts/a2741_oil_press_hud_provider.js').read_text(encoding='utf-8')
 for token in ('registerCrosshairHudProvider','a26ReadPress','a26ReadVat','a26ProbePressContainer','oilPressHudView','OIL_PRESS_ID'):
  assert token in provider,token
 for forbidden in ('runInterval','getBlockFromViewDirection','nearbyOffsets','getDynamicProperty','setDynamicProperty'):
  assert forbidden not in provider,forbidden

 hud=(BP/'scripts/a2741_oil_press_hud_core.js').read_text(encoding='utf-8')
 for token in ('PRESS_MAX_CAKES','PRESS_REQUIRED_PROGRESS','VAT_CAPACITY_BUCKETS','normalizePress','normalizeVat'):
  assert token in hud,token
 for key in LANG_KEYS:assert key in hud,key

 shared=(BP/'scripts/a2739_crosshair_hud_runtime.js').read_text(encoding='utf-8')
 assert shared.count('system.runInterval(')==1
 assert 'registerCrosshairHudProvider' in shared

 for lang in ('en_US.lang','zh_CN.lang','zh_TW.lang'):
  rows=(RP/'texts'/lang).read_text(encoding='utf-8').splitlines()
  for key in LANG_KEYS:assert sum(1 for row in rows if row.startswith(key+'='))==1,(lang,key)

 subprocess.run(['node',str(DEV/'test_a2741_core.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2741-oil-press-hud-provider.json')
 assert report['version']=='A2.7.41'
 assert report['reuse']['single_poll_loop'] is True
 assert report['reuse']['duplicate_nearby_scan'] is False
 assert report['reuse']['duplicate_press_state_parser'] is False
 assert report['parity_boundary']['big_vat'] is True
 assert report['parity_boundary']['generic_fluid_handler'] is False
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
  'version':'A2.7.41','oil_press_hud_provider':True,'shared_crosshair_runtime':True,
  'existing_press_vat_probe_reused':True,'single_poll_loop':True,'duplicate_nearby_scan':False,
  'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2741-dash-verification.json' if a.compiled else 'a2741-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
