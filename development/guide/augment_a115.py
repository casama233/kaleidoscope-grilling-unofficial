from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
GUIDE=ROOT/'projects/grilling/integration/cookery106';BP=GUIDE/'behavior_pack';RP=GUIDE/'resource_pack'
VERSION=[0,1,15];PAYLOAD_VERSION='0.1.15';REVISION='a1_15_0'
OLD_PREFIX='// Generated A1.14 localized Cookery guide extension.\nexport const GUIDE_PAYLOAD = '
NEW_PREFIX='// Generated A1.15 complete-language-file Cookery guide extension.\nexport const GUIDE_PAYLOAD = '

CN_FIX=str.maketrans({'鱈':'鳕','鮭':'鲑','熱':'热','帶':'带','頭':'头','團':'团'})
TW_FIX=str.maketrans({'头':'頭'})

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write_json(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def read_lang(p):
 out={};order=[]
 for line in p.read_text(encoding='utf-8-sig').splitlines():
  if '=' not in line:continue
  k,v=line.split('=',1)
  if k in out:raise RuntimeError('duplicate language key '+k)
  out[k]=v;order.append(k)
 return out,order
def write_lang(p,d,order):p.parent.mkdir(parents=True,exist_ok=True);p.write_text('\n'.join(k+'='+d[k] for k in order)+'\n',encoding='utf-8')
def read_payload():
 s=(BP/'scripts/payload.js').read_text(encoding='utf-8').strip()
 if not s.startswith(OLD_PREFIX) or not s.endswith(';'):raise RuntimeError('A1.14 payload prefix drift')
 return json.loads(s[len(OLD_PREFIX):-1])

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name,desc in ((bm,'Grilling Guide A1.15 — COMPLETE LANGUAGE FILES BP','Localized Grilling chapter with complete zh_CN/zh_TW/en_US language-source files.'),(rm,'Grilling Guide A1.15 — COMPLETE LANGUAGE FILES RP','Complete guide UI, entry-name, and body language files for zh_CN/zh_TW/en_US.')):
  doc['header']['version']=VERSION;doc['header']['name']=name;doc['header']['description']=desc
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write_json(BP/'manifest.json',bm);write_json(RP/'manifest.json',rm)
 cfg=load(GUIDE/'config.json');cfg['name']='Grilling Guide — Cookery 1.0.6 complete languages A1.15';cfg['description']='Complete zh_CN / zh_TW / en_US guide language sources; one entry inside the existing Cookery guidebook.';cfg['compiler']['plugins'][0][1]['packName']='KG_Grilling_Guide_A115_Languages';write_json(GUIDE/'config.json',cfg)

def fix_mechanics():
 old=load(GUIDE/'a114-localized-mechanics.json')
 if old['locales']!=['zh_CN','zh_TW','en_US'] or len(old['entries'])!=33:raise RuntimeError('A1.14 mechanics baseline drift')
 entries={}
 for id_,row in old['entries'].items():
  entries[id_]={
   'zh_CN':[x.translate(CN_FIX) for x in row['zh_CN']],
   'zh_TW':[x.translate(TW_FIX) for x in row['zh_TW']],
   'en_US':list(row['en_US']),
  }
 return {'schema':2,'locales':['zh_CN','zh_TW','en_US'],'entries':entries}

def patch_payload(mechanics):
 payload=read_payload();payload['version']=PAYLOAD_VERSION
 for k,v in list(payload['names']['zh_TW'].items()):payload['names']['zh_TW'][k]=v.translate(TW_FIX)
 byid={e['id']:e for e in payload['entries']}
 if set(byid)!=set(mechanics['entries']):raise RuntimeError('payload/mechanics entry set drift')
 for id_,row in mechanics['entries'].items():byid[id_]['mechanics']=row['zh_TW']
 (BP/'scripts/payload.js').write_text(NEW_PREFIX+json.dumps(payload,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
 pub=BP/'scripts/publisher.js';s=pub.read_text(encoding='utf-8')
 if s.count("export const REVISION = 'a1_14_0';")!=1:raise RuntimeError('A1.14 publisher revision drift')
 pub.write_text(s.replace("export const REVISION = 'a1_14_0';",f"export const REVISION = '{REVISION}';"),encoding='utf-8')
 return payload

def patch_language_files(mechanics):
 locales=('zh_CN','zh_TW','en_US');counts={}
 for loc in locales:
  path=RP/f'texts/{loc}.lang';data,order=read_lang(path)
  if len(data)!=42:raise RuntimeError(f'{loc}: expected A1.14 42 keys, got {len(data)}')
  if loc=='zh_TW':
   data={k:v.translate(TW_FIX) for k,v in data.items()}
  body_keys=[]
  for id_,row in mechanics['entries'].items():
   slug=id_.split(':',1)[1]
   for i,line in enumerate(row[loc],1):
    key=f'guide.kg.body.{slug}.{i}'
    if key in data:raise RuntimeError('duplicate generated guide body key '+key)
    data[key]=line;body_keys.append(key)
  if len(body_keys)!=66:raise RuntimeError(f'{loc}: expected 66 body lines, got {len(body_keys)}')
  write_lang(path,data,order+body_keys);counts[loc]=len(data)
 write_json(RP/'texts/languages.json',list(locales))
 return counts

def main():
 if load(BP/'manifest.json')['header']['version']!=[0,1,14] or load(RP/'manifest.json')['header']['version']!=[0,1,14]:
  raise RuntimeError('A1.15 must augment published A1.14')
 patch_versions();mechanics=fix_mechanics();payload=patch_payload(mechanics);counts=patch_language_files(mechanics)
 write_json(GUIDE/'a115-localized-mechanics.json',mechanics)
 write_json(GUIDE/'a115-localization-report.json',{
  'version':'A1.15','language_files':['zh_CN','zh_TW','en_US'],
  'language_key_count':counts,'ui_and_name_keys':42,'body_keys_per_locale':66,
  'entry_count':33,'localized_body_entries':33,
  'fixed_zh_cn_mixed_script':['鳕鱼','鲑鱼','热带鱼','馒头片','骨头','面团'],
  'fixed_zh_tw_mixed_script':['饅頭片串'],
  'runtime_labels_follow_host_language':True,
  'runtime_body_locale_switch_on_stock_cookery_1_0_6':False,
  'runtime_body_fallback_locale':'zh_TW',
  'host_limitation':'Cookery 1.0.6 Guidebook Extension API v1 rejects standard locale keys in mechanicsByLocale while the UI reads standard locale keys. Full body translations are now stored in normal RP .lang files, but the stock host cannot safely select those bodies per player without a host-side API fix.',
  'standalone_book_item':False,'host_modified':False,'minecraft_tested':False,'bds_tested':False,
 })
 print('A1.15 complete language files generated')
if __name__=='__main__':main()
