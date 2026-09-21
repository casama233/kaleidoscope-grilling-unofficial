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
 'a23_oil_world.js',
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
 assert bm['header']['version']==[2,7,34] and rm['header']['version']==[2,7,34]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.34 Cookery Oil Contract Fix BP'

 core=BP/'scripts/a2734_cookery_oil_pot_core.js'
 adapter=BP/'scripts/a2734_cookery_oil_pot_adapter.js'
 assert core.read_bytes()==(DEV/'a2734_cookery_oil_pot_core.js').read_bytes()
 assert adapter.read_bytes()==(DEV/'a2734_cookery_oil_pot_adapter.js').read_bytes()

 texts={}
 for name in CONSUMERS:
  texts[name]=(BP/'scripts'/name).read_text(encoding='utf-8')
  assert "from './a2734_cookery_oil_pot_adapter.js';" in texts[name],name
  for token in FORBIDDEN:
   assert token not in texts[name],(name,token)

 assert "from './a2730_cookery_oil_pot_adapter.js';" not in texts['main.js']
 assert "from './a2730_cookery_oil_pot_adapter.js';" not in texts['a26_oil_machine_runtime.js']
 assert "from './a2730_cookery_oil_pot_adapter.js';" not in texts['a2722_cold_houttuynia_runtime.js']

 oil_world=texts['a23_oil_world.js']
 assert 'planCookeryTypedOilAddition(held,type,OIL_BUCKET_POINTS)' in oil_world
 assert 'cookeryType(' not in oil_world and 'cookeryCount(' not in oil_world
 assert 'FLUID_CAPACITY' not in oil_world

 adapter_text=adapter.read_text(encoding='utf-8')
 assert 'legacyPlacementFallback=false' in adapter_text
 assert 'readCookeryOilPotForPlacement' in adapter_text
 assert 'planCookeryTypedOilAddition' in adapter_text

 core_text=core.read_text(encoding='utf-8')
 assert "if(!hasRaw)return legacyPlacementFallback?cap:0;" in core_text
 assert "reason:'native_fat'" in core_text
 assert 'HOST_FAT_CAPACITY=256' in core_text
 assert 'GRILLING_FLUID_CAPACITY=64' in core_text

 # Historical A2.7.30 adapter remains for slice rebuildability but is not active.
 assert (BP/'scripts/a2730_cookery_oil_pot_adapter.js').is_file()
 assert (BP/'scripts/a2730_cookery_oil_pot_core.js').is_file()

 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2734_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2734_adapter.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2734-oil-contract-fix.json')
 assert report['version']=='A2.7.34'
 assert report['audit_finding']['a2730_claimed_active_consumers']==3
 assert report['audit_finding']['actual_active_consumers_before_a2734']==4
 assert report['audit_finding']['missed_consumer']=='a23_oil_world.js'
 assert report['cookery_bedrock_1_0_6']['normal_item_read_missing_count']==0
 assert report['cookery_bedrock_1_0_6']['legacy_filled_item_placement_missing_count']==256
 assert report['java_1_1_1']['get_count_missing_component']==0
 assert report['after']['active_consumers']==4
 assert report['after']['consumer_direct_host_key_access']==0
 assert report['after']['native_fat_retyping_blocked'] is True
 assert len(report['remaining_infrastructure_duplicates'])>=3
 assert report['minecraft_tested'] is False and report['bds_tested'] is False

 # Preserve recent architecture/render fixes.
 main_text=texts['main.js']
 assert "import './a2732_standalone_food_effect_runtime.js';" in main_text
 assert "import './a2731_farmland_crop_host_runtime.js';" in main_text
 hand=load(RP/'attachables/special_seasoning.attachable.json')['minecraft:attachable']['description']
 assert hand['geometry']=={'default':'geometry.kg_a2733.seasoning_bottle_hand'}

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
  'version':'A2.7.34',
  'cookery_oil_contract_fix':True,
  'active_consumers':4,
  'consumer_direct_host_key_access':0,
  'normal_missing_count':0,
  'legacy_placement_missing_count':256,
  'native_fat_retyping_blocked':True,
  'a2733_seasoning_corrective_preserved':True,
  'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2734-dash-verification.json' if a.compiled else 'a2734-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))

if __name__=='__main__':
 main()
