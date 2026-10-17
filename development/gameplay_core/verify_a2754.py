from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
PLAN=DEV/'a2754_village_loot_plan.json'

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def blob(path):
 data=path.read_bytes()
 return hashlib.sha1(b'blob '+str(len(data)).encode()+bytes([0])+data).hexdigest()
def refs(node):
 out=[]
 if isinstance(node,dict):
  if node.get('type')=='loot_table' and isinstance(node.get('name'),str):out.append(node['name'])
  for v in node.values():out.extend(refs(v))
 elif isinstance(node,list):
  for v in node:out.extend(refs(v))
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 plan=load(PLAN)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,54] and rm['header']['version']==[2,7,54]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.54 Village Pepper Loot BP'

 assert plan['version']=='A2.7.54'
 assert plan['mojang_baseline']=={
  'repo':'Mojang/bedrock-samples',
  'commit':'46ba6ea985fb5a92d79a9419198f10dda14c199d',
  'version':'1.26.50.4'
 }
 assert len(plan['village_tables'])==15
 assert all(name!='village_bundle.json' for name,_ in plan['village_tables'])

 bonus=load(BP/'loot_tables/kaleidoscope_grilling/village_pepper_bonus.json')
 assert len(bonus['pools'])==2
 pepper,sapling=bonus['pools']
 assert pepper['rolls']==1 and pepper['conditions']==[{'condition':'random_chance','chance':0.4}]
 assert pepper['entries']==[{
  'type':'item','name':'kaleidoscope_grilling:sichuan_pepper','weight':1,
  'functions':[{'function':'set_count','count':{'min':3,'max':10}}]
 }]
 assert sapling['rolls']==1 and sapling['conditions']==[{'condition':'random_chance','chance':0.2}]
 assert sapling['entries']==[{'type':'item','name':'kaleidoscope_grilling:pepper_sapling','weight':1}]

 live=BP/'loot_tables/chests/village'
 snapshots=BP/'loot_tables/kaleidoscope_grilling/vanilla/village'
 assert not (live/'village_bundle.json').exists()
 expected_names={name for name,_ in plan['village_tables']}
 assert {p.name for p in live.glob('*.json')}==expected_names
 assert {p.name for p in snapshots.glob('*.json')}==expected_names

 for name,sha in plan['village_tables']:
  snap=snapshots/name;wrap=live/name
  assert snap.is_file() and blob(snap)==sha,(name,blob(snap),sha)
  original=load(snap)
  own='loot_tables/chests/village/'+name
  assert own not in refs(original),(name,refs(original))
  wrapper=load(wrap)
  assert wrapper=={
   'pools':[
    {'rolls':1,'entries':[{
     'type':'loot_table','name':'loot_tables/kaleidoscope_grilling/vanilla/village/'+name
    }]},
    {'rolls':1,'entries':[{
     'type':'loot_table','name':'loot_tables/kaleidoscope_grilling/village_pepper_bonus.json'
    }]}
   ]
  },name

 # No runtime wheel was created for a data-driven loot concern.
 main_text=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert 'a2754' not in main_text
 for p in (BP/'scripts').glob('a2754*.js'):raise AssertionError(p)

 # Preserve preceding worldgen + advancement + cuisine content.
 for path in (
  BP/'features/pepper_tree_worldgen.json',
  BP/'feature_rules/pepper_tree_worldgen_rule.json',
  BP/'scripts/a2753_advancement_runtime.js',
  BP/'items/potato_beef_stew.json'
 ):assert path.is_file(),path

 subprocess.run(['node',str(DEV/'test_a2754_core.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2754-village-pepper-loot.json')
 assert report['version']=='A2.7.54'
 assert report['village_chest_tables']==15
 assert report['mojang_bedrock_samples_commit']=='46ba6ea985fb5a92d79a9419198f10dda14c199d'
 assert report['mojang_bedrock_samples_version']=='1.26.50.4'
 assert report['wrapper_strategy'] is True
 assert report['vanilla_snapshots_byte_pinned'] is True
 assert report['shared_bonus_table'] is True
 assert report['village_bundle_overridden'] is False
 assert (report['pepper_chance'],report['pepper_min'],report['pepper_max'])==(0.4,3,10)
 assert (report['sapling_chance'],report['sapling_count'])==(0.2,1)
 assert report['new_script_runtime'] is False
 assert report['vanilla_loot_table_override'] is True
 assert report['loot_override_compatibility_risk'] is True
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
  'version':'A2.7.54',
  'village_pepper_loot':True,
  'village_tables':15,
  'mojang_baseline':'1.26.50.4',
  'wrapper_strategy':True,
  'shared_bonus_table':True,
  'village_bundle_overridden':False,
  'new_script_runtime':False,
  'loot_override_compatibility_risk':True,
  'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2754-dash-verification.json' if a.compiled else 'a2754-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
