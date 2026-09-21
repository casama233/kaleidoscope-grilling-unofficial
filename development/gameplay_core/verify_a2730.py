from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core'
BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent

CONSUMERS=(
 'main.js',
 'a26_oil_machine_runtime.js',
 'a2722_cold_houttuynia_runtime.js',
)
FORBIDDEN=(
 'kc_oil_count',
 'kaleidoscope_grilling:oil_type',
 'kaleidoscope_cookery:oil_pot_filled',
 'kaleidoscope_cookery:oil_pot',
)

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)

 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,30] and rm['header']['version']==[2,7,30]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.30 Cookery Oil Pot Adapter BP'

 core=BP/'scripts/a2730_cookery_oil_pot_core.js'
 adapter=BP/'scripts/a2730_cookery_oil_pot_adapter.js'
 assert core.read_bytes()==(DEV/'a2730_cookery_oil_pot_core.js').read_bytes()
 assert adapter.read_bytes()==(DEV/'a2730_cookery_oil_pot_adapter.js').read_bytes()

 core_text=core.read_text(encoding='utf-8')
 adapter_text=adapter.read_text(encoding='utf-8')
 for token in (
  "COOKERY_EMPTY_ID='kaleidoscope_cookery:oil_pot'",
  "COOKERY_FILLED_ID='kaleidoscope_cookery:oil_pot_filled'",
  "HOST_COUNT_KEY='kc_oil_count'",
  "GRILLING_TYPE_KEY='kaleidoscope_grilling:oil_type'",
  'HOST_FAT_CAPACITY=256','GRILLING_FLUID_CAPACITY=64',
 ):
  assert token in core_text,token
 for token in ('readCookeryOilPot','buildCookeryOilPot','planCookeryOilPotConsumption'):
  assert token in adapter_text,token

 main_text=(BP/'scripts/main.js').read_text(encoding='utf-8')
 a26_text=(BP/'scripts/a26_oil_machine_runtime.js').read_text(encoding='utf-8')
 cold_text=(BP/'scripts/a2722_cold_houttuynia_runtime.js').read_text(encoding='utf-8')

 for text in (main_text,a26_text,cold_text):
  assert "from './a2730_cookery_oil_pot_adapter.js';" in text

 assert 'planCookeryOilPotConsumption(stack,needed)' in main_text
 assert 'readCookeryOilPot(item)' in a26_text
 assert 'buildCookeryOilPot(plan.type,plan.nextCount,item)' in a26_text
 assert 'readCookeryOilPot(o)' in cold_text
 assert 'buildCookeryOilPot(type,plan.nextOilCount,o)' in cold_text

 for name,text in zip(CONSUMERS,(main_text,a26_text,cold_text)):
  for token in FORBIDDEN:
   assert token not in text,(name,token)

 assert "import './a2727_cookery_host_recipes_runtime.js';" in main_text
 assert load(RP/'texts/languages.json')==['zh_CN','zh_TW','en_US']
 tw=(RP/'texts/zh_TW.lang').read_text(encoding='utf-8-sig')
 assert '森羅物語：煙火' in tw and '烤饅頭片串' in tw

 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2730_core.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2730-oil-pot-adapter.json')
 assert report['version']=='A2.7.30'
 assert report['before']['independent_oil_pot_readers']==3
 assert report['after']['shared_adapter_modules']==1
 assert report['after']['consumer_direct_host_key_access']==0
 assert report['behavior']['untyped_host_fat_capacity']==256
 assert report['behavior']['typed_grilling_oil_capacity']==64
 assert report['behavior']['zero_remaining_returns_empty_host_pot'] is True
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
  'version':'A2.7.30','cookery_oil_pot_adapter':True,'active_consumers':3,
  'consumer_direct_host_key_access':0,'untyped_capacity':256,'typed_capacity':64,
  'a2727_host_recipe_reuse_preserved':True,'a2729_language_hotfix_preserved':True,
  'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2730-dash-verification.json' if a.compiled else 'a2730-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))

if __name__=='__main__':
 main()
