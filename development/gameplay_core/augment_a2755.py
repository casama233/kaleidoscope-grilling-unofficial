from __future__ import annotations
import hashlib,json,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,55]
PLAN=DEV/'a2755_fortress_loot_plan.json'

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def git_blob(data):
 return hashlib.sha1(b'blob '+str(len(data)).encode()+bytes([0])+data).hexdigest()
def fetch(plan):
 path=plan['vanilla_table']['path'];sha=plan['vanilla_table']['sha'];commit=plan['mojang_baseline']['commit']
 url=f'https://raw.githubusercontent.com/Mojang/bedrock-samples/{commit}/'+path
 req=urllib.request.Request(url,headers={'User-Agent':'Grilling-A2.7.55/1'})
 with urllib.request.urlopen(req,timeout=90) as r:data=r.read()
 actual=git_blob(data)
 if actual!=sha:raise RuntimeError(f'nether_bridge loot drift: {actual} != {sha}')
 json.loads(data.decode('utf-8-sig'));return data

def bonus(plan):
 b=plan['bonus']
 return {'pools':[{
  'rolls':b['rolls'],
  'conditions':[{'condition':'random_chance','chance':b['chance']}],
  'entries':[{
   'type':'item','name':b['item'],'weight':1,
   'functions':[{'function':'set_count','count':b['count']}]
  }]
 }]}

def wrapper():
 return {'pools':[
  {'rolls':1,'entries':[{'type':'loot_table','name':'loot_tables/kaleidoscope_grilling/vanilla/chests/nether_bridge.json'}]},
  {'rolls':1,'entries':[{'type':'loot_table','name':'loot_tables/kaleidoscope_grilling/fortress_houttuynia_bonus.json'}]}
 ]}

def patch_loot():
 plan=load(PLAN);data=fetch(plan)
 snap=BP/'loot_tables/kaleidoscope_grilling/vanilla/chests/nether_bridge.json'
 snap.parent.mkdir(parents=True,exist_ok=True);snap.write_bytes(data)
 write(BP/'loot_tables/kaleidoscope_grilling/fortress_houttuynia_bonus.json',bonus(plan))
 write(BP/'loot_tables/chests/nether_bridge.json',wrapper())

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in (
  (bm,'Kaleidoscope Grilling A2.7.55 Fortress Houttuynia Loot BP'),
  (rm,'Kaleidoscope Grilling A2.7.55 Fortress Houttuynia Loot RP'),
 ):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.55 Fortress Houttuynia Loot'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_55_Fortress_Houttuynia_Loot'
 write(P/'config.json',cfg)

def report():
 plan=load(PLAN);b=plan['bonus']
 write(P/'reports/a2755-fortress-houttuynia-loot.json',{
  'version':'A2.7.55','java_handler':'FortressHouttuyniaHandler',
  'mojang_bedrock_samples_commit':plan['mojang_baseline']['commit'],
  'mojang_bedrock_samples_version':plan['mojang_baseline']['version'],
  'wrapper_strategy_reused':True,'vanilla_snapshot_byte_pinned':True,
  'chance':b['chance'],'rolls':b['rolls'],'count':b['count'],
  'new_script_runtime':False,'vanilla_loot_table_override':True,
  'loot_override_compatibility_risk':True,
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,54]:
  raise RuntimeError('A2.7.55 must augment published A2.7.54')
 patch_loot();patch_versions();report()
 print('A2.7.55 Fortress Houttuynia Loot complete')
if __name__=='__main__':main()
