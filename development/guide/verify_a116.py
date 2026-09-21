from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess,re

ROOT=Path(__file__).resolve().parents[2]
GUIDE=ROOT/'projects/grilling/integration/cookery106';BP=GUIDE/'behavior_pack';RP=GUIDE/'resource_pack'
PREFIX='// Generated A1.16 per-player localized Cookery guide extension.\nexport const GUIDE_PAYLOAD = '
LOCALES=['zh_CN','zh_TW','en_US']

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def payload():
 s=(BP/'scripts/payload.js').read_text(encoding='utf-8').strip()
 assert s.startswith(PREFIX) and s.endswith(';')
 return json.loads(s[len(PREFIX):-1])
def lang(p):
 out={}
 for line in p.read_text(encoding='utf-8-sig').splitlines():
  if '=' in line:k,v=line.split('=',1);assert k not in out;out[k]=v
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[0,1,16] and rm['header']['version']==[0,1,16]
 assert load(RP/'texts/languages.json')==LOCALES
 ls={x:lang(RP/f'texts/{x}.lang') for x in LOCALES}
 assert all(len(x)==108 for x in ls.values()) and set(ls['zh_CN'])==set(ls['zh_TW'])==set(ls['en_US'])

 mech=load(GUIDE/'a115-localized-mechanics.json')
 p=payload();assert p['version']=='0.1.16' and len(p['entries'])==33
 byid={e['id']:e for e in p['entries']};assert set(byid)==set(mech['entries'])
 for id_,localized in mech['entries'].items():
  entry=byid[id_]
  assert set(entry['mechanicsByLocale'])==set(LOCALES),id_
  for loc in LOCALES:
   assert entry['mechanicsByLocale'][loc]==localized[loc],(id_,loc)
  assert entry['mechanics']==localized['zh_TW'],id_
 assert all(re.fullmatch(r'[a-z]{2}_[A-Z]{2}',loc) for loc in LOCALES)

 publisher=(BP/'scripts/publisher.js').read_text(encoding='utf-8')
 assert "export const REVISION = 'a1_16_0';" in publisher
 for f in (BP/'scripts/payload.js',BP/'scripts/publisher.js',BP/'scripts/main.js'):subprocess.run(['node','--check',str(f)],check=True)
 report=load(GUIDE/'a116-localization-report.json')
 assert report['mechanics_by_locale_entries']==33
 assert report['stock_cookery_1_0_6_body_switch'] is False
 assert report['compat_cookery_1_0_6_body_switch'] is True
 assert report['per_player_language_key']=='kc:guidebook_language'
 assert report['standalone_book_item'] is False

 compiled=[]
 if a.compiled:
  dist=GUIDE/'builds/dist'
  for name,source in [('behavior_pack',BP),('resource_pack',RP)]:
   manifest=load(source/'manifest.json')
   matches=[x.parent for x in dist.rglob('manifest.json') if load(x).get('header',{}).get('uuid')==manifest['header']['uuid']]
   assert len(matches)==1,(name,matches);target=matches[0];count=0
   for f in source.rglob('*'):
    if not f.is_file() or f.name.startswith('.'):continue
    q=target/f.relative_to(source);assert q.is_file(),str(q)
    if f.suffix=='.json':assert load(f)==load(q),str(q)
    else:assert f.read_bytes()==q.read_bytes(),str(q)
    count+=1
   compiled.append({'pack':name,'compared_files':count,'matches_source':True})
 out=GUIDE/('a116-dash-verification.json' if a.compiled else 'a116-structure-verification.json')
 out.write_text(json.dumps({'version':'A1.16','entries':33,'localized_body_locales':LOCALES,'mechanics_by_locale_entries':33,'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))
if __name__=='__main__':main()
