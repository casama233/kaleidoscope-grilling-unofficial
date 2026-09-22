from __future__ import annotations
import hashlib,json,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,54]
PLAN_PATH=DEV/'a2754_village_loot_plan.json'

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def git_blob(data):
 return hashlib.sha1(b'blob '+str(len(data)).encode()+bytes([0])+data).hexdigest()

def fetch_vanilla(commit,name,expected):
 url=f'https://raw.githubusercontent.com/Mojang/bedrock-samples/{commit}/behavior_pack/loot_tables/chests/village/{name}'
 req=urllib.request.Request(url,headers={'User-Agent':'Grilling-A2.7.54/1'})
 with urllib.request.urlopen(req,timeout=90) as r:data=r.read()
 actual=git_blob(data)
 if actual!=expected:raise RuntimeError(f'Mojang village loot drift {name}: {actual} != {expected}')
 json.loads(data.decode('utf-8-sig'))
 return data

def bonus_table(plan):
 p=plan['bonus']['pepper'];s=plan['bonus']['sapling']
 return {
  'pools':[
   {
    'rolls':1,
    'conditions':[{'condition':'random_chance','chance':p['chance']}],
    'entries':[{
     'type':'item','name':p['item'],'weight':1,
     'functions':[{'function':'set_count','count':{'min':p['min'],'max':p['max']}}]
    }]
   },
   {
    'rolls':1,
    'conditions':[{'condition':'random_chance','chance':s['chance']}],
    'entries':[{'type':'item','name':s['item'],'weight':1}]
   }
  ]
 }

def wrapper(name):
 return {
  'pools':[
   {
    'rolls':1,
    'entries':[{
     'type':'loot_table',
     'name':'loot_tables/kaleidoscope_grilling/vanilla/village/'+name
    }]
   },
   {
    'rolls':1,
    'entries':[{
     'type':'loot_table',
     'name':'loot_tables/kaleidoscope_grilling/village_pepper_bonus.json'
    }]
   }
  ]
 }

def patch_loot():
 plan=load(PLAN_PATH);commit=plan['mojang_baseline']['commit']
 live=BP/'loot_tables/chests/village'
 snapshots=BP/'loot_tables/kaleidoscope_grilling/vanilla/village'
 for name,sha in plan['village_tables']:
  if name=='village_bundle.json':raise RuntimeError('A2.7.54 must not override village_bundle')
  data=fetch_vanilla(commit,name,sha)
  dst=snapshots/name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
  write(live/name,wrapper(name))
 write(BP/'loot_tables/kaleidoscope_grilling/village_pepper_bonus.json',bonus_table(plan))

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in (
  (bm,'Kaleidoscope Grilling A2.7.54 Village Pepper Loot BP'),
  (rm,'Kaleidoscope Grilling A2.7.54 Village Pepper Loot RP'),
 ):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json')
 cfg['name']='Kaleidoscope Grilling A2.7.54 Village Pepper Loot'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_54_Village_Pepper_Loot'
 write(P/'config.json',cfg)

def report():
 plan=load(PLAN_PATH)
 write(P/'reports/a2754-village-pepper-loot.json',{
  'version':'A2.7.54',
  'java_handler':'VillagePepperLootHandler',
  'village_chest_tables':len(plan['village_tables']),
  'mojang_bedrock_samples_commit':plan['mojang_baseline']['commit'],
  'mojang_bedrock_samples_version':plan['mojang_baseline']['version'],
  'wrapper_strategy':True,
  'vanilla_snapshots_byte_pinned':True,
  'shared_bonus_table':True,
  'village_bundle_overridden':False,
  'pepper_chance':0.4,'pepper_min':3,'pepper_max':10,
  'sapling_chance':0.2,'sapling_count':1,
  'new_script_runtime':False,
  'vanilla_loot_table_override':True,
  'loot_override_compatibility_risk':True,
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,53]:
  raise RuntimeError('A2.7.54 must augment published A2.7.53')
 patch_loot();patch_versions();report()
 print('A2.7.54 Village Pepper Loot complete')

if __name__=='__main__':main()
