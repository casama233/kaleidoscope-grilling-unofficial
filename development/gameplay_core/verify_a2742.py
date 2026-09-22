from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
NEW=('a2742_big_vat_hud_core.js','a2742_big_vat_hud_provider.js')
REFACTORED_GRILL='a2742_refactored_a2740_grill_hud_core.js'
LANG_KEYS=(
 'hud.kaleidoscope_grilling.vat.title',
 'hud.kaleidoscope_grilling.vat.content.empty',
 'hud.kaleidoscope_grilling.vat.content.water',
 'hud.kaleidoscope_grilling.vat.content.lava',
 'hud.kaleidoscope_grilling.vat.content.canola',
 'hud.kaleidoscope_grilling.vat.content.secret_chili',
 'hud.kaleidoscope_grilling.vat.content.premium_chili',
 'hud.kaleidoscope_grilling.vat.capacity',
 'hud.kaleidoscope_grilling.vat.accepts',
 'jade.kaleidoscope_grilling.grill.ready',
)

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,42] and rm['header']['version']==[2,7,42]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.42 Big Vat HUD Provider BP'
 for name in NEW:assert (BP/'scripts'/name).read_bytes()==(DEV/name).read_bytes(),name
 assert (BP/'scripts/a2740_grill_hud_core.js').read_bytes()==(DEV/REFACTORED_GRILL).read_bytes()

 oil=(BP/'scripts/a26_oil_machine_runtime.js').read_text(encoding='utf-8')
 assert oil.count('export function a26ReadVat(block){return readVat(block)}')==1

 main_text=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert main_text.count("import './a2742_big_vat_hud_provider.js';")==1

 provider=(BP/'scripts/a2742_big_vat_hud_provider.js').read_text(encoding='utf-8')
 for token in ('registerCrosshairHudProvider','a26ReadVat','bigVatHudView','BIG_VAT_ID'):
  assert token in provider,token
 for forbidden in ('runInterval','getBlockFromViewDirection','getDynamicProperty','setDynamicProperty','normalizeVat'):
  assert forbidden not in provider,forbidden

 hud=(BP/'scripts/a2742_big_vat_hud_core.js').read_text(encoding='utf-8')
 for token in ('VAT_CAPACITY_BUCKETS','normalizeVat','bigVatContentKey','hud.kaleidoscope_grilling.vat.content.'):
  assert token in hud,token
 assert 'getDynamicProperty' not in hud and 'setDynamicProperty' not in hud

 grill=(BP/'scripts/a2740_grill_hud_core.js').read_text(encoding='utf-8')
 assert "?'jade.kaleidoscope_grilling.grill.ready'" in grill
 assert "status==='jade.kaleidoscope_grilling.grill.ready'" in grill
 assert "return {translate:'message.kaleidoscope_grilling.grill_ready_to_take'}" in grill

 shared=(BP/'scripts/a2739_crosshair_hud_runtime.js').read_text(encoding='utf-8')
 assert shared.count('system.runInterval(')==1
 assert 'registerCrosshairHudProvider' in shared

 for lang in ('en_US.lang','zh_CN.lang','zh_TW.lang'):
  rows=(RP/'texts'/lang).read_text(encoding='utf-8').splitlines()
  for key in LANG_KEYS:assert sum(1 for row in rows if row.startswith(key+'='))==1,(lang,key)

 subprocess.run(['node',str(DEV/'test_a2742_core.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2742-big-vat-hud-provider.json')
 assert report['version']=='A2.7.42'
 assert report['java_contract']['capacity_buckets']==8
 assert report['reuse']['single_poll_loop'] is True
 assert report['reuse']['duplicate_vat_state_parser'] is False
 assert report['reuse']['direct_dynamic_property_access'] is False
 assert report['grill_ready_contract_repaired'] is True
 assert report['bedrock_fluid_types']==['water','lava','canola','secret_chili','premium_chili']
 assert report['parity_boundary']['java_generic_registered_fluids'] is True
 assert report['parity_boundary']['bedrock_generic_fluid_api'] is False
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
  'version':'A2.7.42','big_vat_hud_provider':True,'shared_crosshair_runtime':True,
  'existing_vat_reader_reused':True,'single_poll_loop':True,'duplicate_vat_state_parser':False,
  'grill_ready_contract_repaired':True,
  'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2742-dash-verification.json' if a.compiled else 'a2742-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
