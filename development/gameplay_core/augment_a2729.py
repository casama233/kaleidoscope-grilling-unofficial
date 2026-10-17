from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
VERSION=[2,7,29]

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write_json(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def read_lang(p):
 rows=[];seen=set()
 for line in p.read_text(encoding='utf-8-sig').splitlines():
  if '=' not in line:continue
  k,v=line.split('=',1)
  if k in seen:raise RuntimeError('duplicate language key '+k)
  seen.add(k);rows.append([k,v])
 return rows
def write_lang(p,rows):p.write_text('\n'.join(k+'='+v for k,v in rows)+'\n',encoding='utf-8')

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.29 Language Hotfix BP'),(rm,'Kaleidoscope Grilling A2.7.29 Language Hotfix RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write_json(BP/'manifest.json',bm);write_json(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.29 Language Hotfix';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_29_Language_Hotfix';write_json(P/'config.json',cfg)

def patch_tw():
 path=RP/'texts/zh_TW.lang';rows=read_lang(path)
 before=sum(v.count('头') for _,v in rows)
 if before!=3:raise RuntimeError(f'A2.7.29 expected 3 remaining simplified 头 characters, got {before}')
 rows=[[k,v.replace('头','頭')] for k,v in rows]
 write_lang(path,rows)
 return before

def report(n):
 write_json(P/'reports/a2729-language-hotfix.json',{
  'version':'A2.7.29','scope':'Traditional Chinese residual-character hotfix only',
  'fixed_character':'头 → 頭','fixed_occurrences':n,
  'affected_terms':['烤饅頭片串','生饅頭片串','生饅頭片'],
  'languages':['zh_CN','zh_TW','en_US'],'language_key_count':96,
  'gameplay_logic_changed':False,'minecraft_tested':False,'bds_tested':False,
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,28]:
  raise RuntimeError('A2.7.29 must augment published A2.7.28')
 patch_versions();n=patch_tw();report(n);print('A2.7.29 language hotfix complete')
if __name__=='__main__':main()
