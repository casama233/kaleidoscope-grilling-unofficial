from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,56] and rm['header']['version']==[2,7,56]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.56 P0 Official API Hardening BP'

 dst=BP/'scripts/a2750_food_state_adapter.js';src=DEV/'a2756_refactored_a2750_food_state_adapter.js'
 assert dst.read_bytes()==src.read_bytes()
 s=dst.read_text(encoding='utf-8')
 body=s.split('export function applyFoodMetadata',1)[1].split('}',1)[0]
 assert body.index('setHotFood(stack,hotTicks)')<body.index('setFoodSeasonings(stack,seasoning)')
 assert 'HotFood lore is therefore committed first' in s

 cuisine=(BP/'scripts/a2750_cookery_cuisine_runtime.js').read_text(encoding='utf-8')
 assert 'applyFoodMetadata(custom,plan)' in cuisine
 assert 'kc_station:' not in cuisine
 assert 'itemCompleteUse.subscribe' not in cuisine

 # Preserve all cuisine content added through A2.7.52.
 for path in (
  BP/'items/houttuynia_stir_fried_pork.json',BP/'items/green_pepper_squid_tentacles.json',
  BP/'items/braised_chicken_wings.json',BP/'items/potato_beef_stew.json',
  BP/'items/red_sweet_potato_porridge.json',BP/'items/sour_spicy_noodles.json',
  BP/'scripts/a2752_stockpot_food_core.js'
 ):assert path.is_file(),path

 # Preserve later acquisition / advancement slices from the A2.7.55 baseline.
 for path in (
  BP/'scripts/a2753_advancement_runtime.js',
  BP/'loot_tables/kaleidoscope_grilling/village_pepper_bonus.json',
  BP/'loot_tables/kaleidoscope_grilling/fortress_houttuynia_bonus.json'
 ):assert path.is_file(),path

 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)
 report=load(P/'reports/a2756-p0-official-api-hardening.json')
 assert report['version']=='A2.7.56'
 assert report['bug']['fixed_order']==['hot_lore_and_dynamic_property','seasoning_dynamic_property']
 assert report['architecture_audit']['cookery_private_kc_station_access'] is False
 assert report['architecture_audit']['duplicate_wok_or_stockpot'] is False
 assert report['p0_regression_guard']['wok_foods']==3 and report['p0_regression_guard']['stockpot_foods']==3
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
 out=P/'reports'/('a2756-dash-verification.json' if a.compiled else 'a2756-structure-verification.json')
 out.write_text(json.dumps({'version':'A2.7.56','official_api_hardening':True,'hot_before_seasoning':True,'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False},indent=2)+'\n',encoding='utf-8')
 print(out.read_text())
if __name__=='__main__':main()
