from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess
ROOT=Path(__file__).resolve().parents[2]
GUIDE=ROOT/'projects/grilling/integration/cookery106';BP=GUIDE/'behavior_pack';RP=GUIDE/'resource_pack'

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def lang(p):
 out={}
 for line in p.read_text(encoding='utf-8-sig').splitlines():
  if '=' in line:k,v=line.split('=',1);assert k not in out;out[k]=v
 return out
def payload():
 s=(BP/'scripts/payload.js').read_text(encoding='utf-8').strip();pre='// Generated A1.14 localized Cookery guide extension.\nexport const GUIDE_PAYLOAD = ';assert s.startswith(pre) and s.endswith(';');return json.loads(s[len(pre):-1])

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json');assert bm['header']['version']==[0,1,14] and rm['header']['version']==[0,1,14]
 assert load(RP/'texts/languages.json')==['zh_CN','zh_TW','en_US']
 ls={x:lang(RP/f'texts/{x}.lang') for x in ('zh_CN','zh_TW','en_US')}
 assert all(len(v)==42 for v in ls.values())  # 9 UI strings + 33 entry names
 assert set(ls['zh_CN'])==set(ls['zh_TW'])==set(ls['en_US'])
 assert ls['zh_CN']['guide.kg.title']=='森罗物语：烟火'
 assert ls['zh_TW']['guide.kg.title']=='森羅物語：煙火'
 assert ls['en_US']['guide.kg.title']=='Kaleidoscope Grilling'
 assert ls['zh_TW']['guide.kg.name.guide_recipe_chicken_skin']=='雞皮串'
 assert ls['zh_TW']['guide.kg.name.guide_recipe_squid_tentacle']=='魷魚鬚串'
 assert ls['zh_TW']['guide.kg.name.guide_recipe_potato_slice']=='馬鈴薯片串'
 p=payload();assert p['version']=='0.1.14' and len(p['entries'])==33
 for loc in ('zh_CN','zh_TW','en_US'):
  assert len(p['names'][loc])==33
  assert p['text'][loc]['title']==ls[loc]['guide.kg.title']
 assert p['names']['zh_TW']['kg_a1:guide_recipe_chicken_skin']=='雞皮串'
 assert p['names']['zh_TW']['kg_a1:guide_recipe_squid_tentacle']=='魷魚鬚串'
 mechanics=load(GUIDE/'a114-localized-mechanics.json');assert mechanics['locales']==['zh_CN','zh_TW','en_US'] and len(mechanics['entries'])==33
 for id_,rows in mechanics['entries'].items():
  assert set(rows)=={'zh_CN','zh_TW','en_US'}
  assert all(rows[x] for x in rows)
 # Runtime payload intentionally retains a safe zh_TW mechanics fallback on stock Cookery 1.0.6.
 byid={x['id']:x for x in p['entries']}
 for id_,rows in mechanics['entries'].items():assert byid[id_]['mechanics']==rows['zh_TW']
 publisher=(BP/'scripts/publisher.js').read_text(encoding='utf-8');assert "export const REVISION = 'a1_14_0';" in publisher
 subprocess.run(['node','--check',str(BP/'scripts/payload.js')],check=True);subprocess.run(['node','--check',str(BP/'scripts/publisher.js')],check=True);subprocess.run(['node','--check',str(BP/'scripts/main.js')],check=True)
 report=load(GUIDE/'a114-localization-report.json');assert report['runtime_labels_follow_host_language'] is True and report['runtime_body_locale_switch_on_stock_cookery_1_0_6'] is False and report['host_modified'] is False
 compiled=[]
 if a.compiled:
  dist=GUIDE/'builds/dist'
  for name,source in [('behavior_pack',BP),('resource_pack',RP)]:
   manifest=load(source/'manifest.json');matches=[x.parent for x in dist.rglob('manifest.json') if load(x).get('header',{}).get('uuid')==manifest['header']['uuid']];assert len(matches)==1,(name,matches);target=matches[0];count=0
   for f in source.rglob('*'):
    if not f.is_file() or f.name.startswith('.'):continue
    q=target/f.relative_to(source);assert q.is_file(),str(q)
    if f.suffix=='.json':assert load(f)==load(q),str(q)
    else:assert f.read_bytes()==q.read_bytes(),str(q)
    count+=1
   compiled.append({'pack':name,'compared_files':count,'matches_source':True})
 out=GUIDE/('a114-dash-verification.json' if a.compiled else 'a114-structure-verification.json');out.write_text(json.dumps({'version':'A1.14','language_files':3,'localized_entries':33,'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))
if __name__=='__main__':main()
