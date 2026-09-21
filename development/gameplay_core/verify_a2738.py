from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess,re

ROOT=Path(__file__).resolve().parents[2];P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
SHARED='a2738_oil_contract_core.js'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,38] and rm['header']['version']==[2,7,38]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.38 Shared Oil Contract BP'
 assert (BP/'scripts'/SHARED).read_bytes()==(DEV/SHARED).read_bytes()

 a24=(BP/'scripts/a24_skewering_core.js').read_text(encoding='utf-8')
 c34=(BP/'scripts/a2734_cookery_oil_pot_core.js').read_text(encoding='utf-8')
 c36=(BP/'scripts/a2736_typed_oil_pot_block_core.js').read_text(encoding='utf-8')
 r36=(BP/'scripts/a2736_typed_oil_pot_block_runtime.js').read_text(encoding='utf-8')
 c37=(BP/'scripts/a2737_offhand_oil_fill_core.js').read_text(encoding='utf-8')
 r37=(BP/'scripts/a2737_offhand_oil_fill_runtime.js').read_text(encoding='utf-8')

 assert "from './a2738_oil_contract_core.js';" in a24
 for forbidden in ('export const FAT_CAPACITY=256;','export const FLUID_CAPACITY=64;','export const OIL_BUCKET_POINTS=8;'):
  assert forbidden not in a24,forbidden

 assert "from './a2738_oil_contract_core.js';" in c34
 for forbidden in ('export const HOST_FAT_CAPACITY=256;','export const GRILLING_FLUID_CAPACITY=64;','const GRILLING_TYPES=','function normalizeOilType','function oilCapacity'):
  assert forbidden not in c34,forbidden

 assert 'GRILLING_OIL_BUCKET_POINTS' in c36
 assert 'export const OIL_BUCKET_POINTS=8;' not in c36

 assert "import {OIL_TYPES} from './a23_oil_world.js';" in r36
 assert "oilTypeForBucketId(itemId,OIL_TYPES)" in r36
 assert 'BUCKET_TO_TYPE' not in r36
 for forbidden in (
  'kaleidoscope_grilling:canola_oil_bucket',
  'kaleidoscope_grilling:secret_chili_oil_bucket',
  'kaleidoscope_grilling:premium_chili_oil_bucket',
 ):
  assert forbidden not in r36,forbidden
 assert 'Math.min(64,count)/64' not in r36

 assert "GRILLING_OIL_BUCKET_POINTS,oilTypeForBucketId" in c37
 assert 'export const ITEM_FILL_POINTS=8;' not in c37
 assert not re.search(r'function\s+oilTypeForBucketId\s*\(',c37)

 assert '/64' not in r37
 assert "plan.nextCount+'/'+plan.capacity" in r37

 subprocess.run(['node',str(DEV/'test_a2738_shared_core.mjs')],check=True)
 subprocess.run(['node',str(DEV/'test_a2738_integrated.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2738-shared-oil-contract.json')
 assert report['version']=='A2.7.38'
 assert report['shared_contract']['host_fat_capacity']==256
 assert report['shared_contract']['typed_fluid_capacity']==64
 assert report['shared_contract']['bucket_points']==8
 assert report['reuse']['a2736_private_bucket_registry_removed'] is True
 assert report['java_display_audit']['duplicate_host_block_created'] is False
 assert report['java_display_audit']['visual_state_deferred_to_shared_host_visual_adapter'] is True
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
  'version':'A2.7.38','shared_oil_contract':True,'host_fat_capacity':256,
  'typed_fluid_capacity':64,'bucket_points':8,'a2736_private_bucket_registry_removed':True,
  'duplicate_host_block_created':False,'visual_adapter_deferred':True,'hud_adapter_deferred':True,
  'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2738-dash-verification.json' if a.compiled else 'a2738-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
