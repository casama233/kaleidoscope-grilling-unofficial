from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
GUIDE=ROOT/'projects/grilling/integration/cookery106'
BP=GUIDE/'behavior_pack';RP=GUIDE/'resource_pack'
VERSION=[0,1,16];PAYLOAD_VERSION='0.1.16';REVISION='a1_16_0'
OLD_PREFIX='// Generated A1.15 complete-language-file Cookery guide extension.\nexport const GUIDE_PAYLOAD = '
NEW_PREFIX='// Generated A1.16 per-player localized Cookery guide extension.\nexport const GUIDE_PAYLOAD = '

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write_json(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def read_payload():
 s=(BP/'scripts/payload.js').read_text(encoding='utf-8').strip()
 if not s.startswith(OLD_PREFIX) or not s.endswith(';'):
  raise RuntimeError('A1.15 payload prefix drift')
 return json.loads(s[len(OLD_PREFIX):-1])

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name,desc in (
  (bm,'Grilling Guide A1.16 — PER-PLAYER LOCALIZED BODY BP','Grilling guide extension with zh_CN/zh_TW/en_US per-player body localization for the Cookery 1.0.6 locale-compat host.'),
  (rm,'Grilling Guide A1.16 — PER-PLAYER LOCALIZED BODY RP','Complete zh_CN/zh_TW/en_US guide language files and icons for the Cookery guidebook.'),
 ):
  doc['header']['version']=VERSION;doc['header']['name']=name;doc['header']['description']=desc
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write_json(BP/'manifest.json',bm);write_json(RP/'manifest.json',rm)
 cfg=load(GUIDE/'config.json')
 cfg['name']='Grilling Guide — Cookery 1.0.6 per-player localized body A1.16'
 cfg['description']='One Grilling entry inside Cookery; complete per-player zh_CN / zh_TW / en_US body localization when used with the pinned Cookery 1.0.6 locale-compat host.'
 cfg['compiler']['plugins'][0][1]['packName']='KG_Grilling_Guide_A116_Per_Player_Locale'
 write_json(GUIDE/'config.json',cfg)

def patch_payload():
 payload=read_payload()
 mechanics=load(GUIDE/'a115-localized-mechanics.json')
 if mechanics.get('locales')!=['zh_CN','zh_TW','en_US'] or len(mechanics.get('entries',{}))!=33:
  raise RuntimeError('A1.15 mechanics catalog drift')
 payload['version']=PAYLOAD_VERSION
 byid={e['id']:e for e in payload['entries']}
 if set(byid)!=set(mechanics['entries']):
  raise RuntimeError('payload/mechanics entry set drift')
 for id_,localized in mechanics['entries'].items():
  if set(localized)!=set(mechanics['locales']):raise RuntimeError('locale set drift '+id_)
  byid[id_]['mechanicsByLocale']={loc:list(localized[loc]) for loc in mechanics['locales']}
  byid[id_]['mechanics']=list(localized['zh_TW'])  # safe fallback for stock 1.0.6
 (BP/'scripts/payload.js').write_text(NEW_PREFIX+json.dumps(payload,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
 pub=BP/'scripts/publisher.js';s=pub.read_text(encoding='utf-8')
 if s.count("export const REVISION = 'a1_15_0';")!=1:raise RuntimeError('A1.15 publisher revision drift')
 pub.write_text(s.replace("export const REVISION = 'a1_15_0';",f"export const REVISION = '{REVISION}';"),encoding='utf-8')
 return payload

def report(payload):
 write_json(GUIDE/'a116-localization-report.json',{
  'version':'A1.16','payload_version':PAYLOAD_VERSION,'revision':REVISION,
  'entry_count':len(payload['entries']),'mechanics_by_locale_entries':sum('mechanicsByLocale' in e for e in payload['entries']),
  'locales':['zh_CN','zh_TW','en_US'],'fallback_locale':'zh_TW',
  'stock_cookery_1_0_6_body_switch':False,
  'compat_cookery_1_0_6_body_switch':True,
  'compat_host_artifact':'Kaleidoscope_Cookery_v1.0.6_Grilling_Guide_Locale_Compat.mcaddon',
  'per_player_language_key':'kc:guidebook_language',
  'standalone_book_item':False,'host_private_files_overwritten_by_child_addon':False,
  'minecraft_tested':False,'bds_tested':False,
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[0,1,15] or load(RP/'manifest.json')['header']['version']!=[0,1,15]:
  raise RuntimeError('A1.16 must augment published A1.15')
 patch_versions();payload=patch_payload();report(payload)
 print('A1.16 per-player localized guide payload complete')
if __name__=='__main__':main()
