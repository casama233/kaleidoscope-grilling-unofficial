from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
PLAN=DEV/'a2755_fortress_loot_plan.json'

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def blob(path):
 data=path.read_bytes();return hashlib.sha1(b'blob '+str(len(data)).encode()+bytes([0])+data).hexdigest()
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
 assert bm['header']['version']==[2,7,55] and rm['header']['version']==[2,7,55]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.55 Fortress Houttuynia Loot BP'
 assert plan['mojang_baseline']['version']=='1.26.50.4'
 assert plan['vanilla_table']['sha']=='071c1feeaccec0f2e9ee39074d76c5862681aa3c'

 snap=BP/'loot_tables/kaleidoscope_grilling/vanilla/chests/nether_bridge.json'
 assert snap.is_file() and blob(snap)==plan['vanilla_table']['sha'],blob(snap)
 original=load(snap)
 assert 'loot_tables/chests/nether_bridge.json' not in refs(original)

 bonus=load(BP/'loot_tables/kaleidoscope_grilling/fortress_houttuynia_bonus.json')
 assert bonus=={'pools':[{
  'rolls':{'min':1,'max':2},
  'conditions':[{'condition':'random_chance','chance':0.65}],
  'entries':[{
   'type':'item','name':'kaleidoscope_grilling:houttuynia','weight':1,
   'functions':[{'function':'set_count','count':{'min':1,'max':3}}]
  }]
 }]}

 wrapper=load(BP/'loot_tables/chests/nether_bridge.json')
 assert wrapper=={'pools':[
  {'rolls':1,'entries':[{'type':'loot_table','name':'loot_tables/kaleidoscope_grilling/vanilla/chests/nether_bridge.json'}]},
  {'rolls':1,'entries':[{'type':'loot_table','name':'loot_tables/kaleidoscope_grilling/fortress_houttuynia_bonus.json'}]}
 ]}

 # Preserve A2.7.54 village overlays and previous world systems.
 village=list((BP/'loot_tables/chests/village').glob('*.json'))
 assert len(village)==15
 assert (BP/'loot_tables/kaleidoscope_grilling/village_pepper_bonus.json').is_file()
 assert (BP/'scripts/a2753_advancement_runtime.js').is_file()
 assert (BP/'features/pepper_tree_worldgen.json').is_file()

 # Pure data slice: no A2.7.55 runtime.
 assert 'a2755' not in (BP/'scripts/main.js').read_text(encoding='utf-8')
 assert not list((BP/'scripts').glob('a2755*.js'))

 subprocess.run(['node',str(DEV/'test_a2755_core.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2755-fortress-houttuynia-loot.json')
 assert report['version']=='A2.7.55'
 assert report['java_handler']=='FortressHouttuyniaHandler'
 assert report['wrapper_strategy_reused'] is True
 assert report['vanilla_snapshot_byte_pinned'] is True
 assert report['chance']==0.65
 assert report['rolls']=={'min':1,'max':2}
 assert report['count']=={'min':1,'max':3}
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
  'version':'A2.7.55','fortress_houttuynia_loot':True,
  'mojang_baseline':'1.26.50.4','wrapper_strategy_reused':True,
  'chance':0.65,'rolls':{'min':1,'max':2},'count':{'min':1,'max':3},
  'new_script_runtime':False,'loot_override_compatibility_risk':True,
  'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2755-dash-verification.json' if a.compiled else 'a2755-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))
if __name__=='__main__':main()
