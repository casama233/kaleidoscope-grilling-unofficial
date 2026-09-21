from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
GUIDE=ROOT/'projects/grilling/integration/cookery106';BP=GUIDE/'behavior_pack';RP=GUIDE/'resource_pack'
PREFIX='// Generated A1.15 complete-language-file Cookery guide extension.\nexport const GUIDE_PAYLOAD = '
CN_BAD='鱈鮭熱帶頭團'
TW_BAD='烧馒猪儿鸡鱼鱿须黄连调制摇盘谱饼红萝块葱凉图龙绿发后里这头种与为开关处过复气区对应该显条数类别样时间满还从实体储备传页简选择进词义虫面罗语烟'

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def lang(p):
 out={};order=[]
 for line in p.read_text(encoding='utf-8-sig').splitlines():
  if '=' not in line:continue
  k,v=line.split('=',1);assert k not in out,k;out[k]=v;order.append(k)
 return out,order
def payload():
 s=(BP/'scripts/payload.js').read_text(encoding='utf-8').strip();assert s.startswith(PREFIX) and s.endswith(';');return json.loads(s[len(PREFIX):-1])

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[0,1,15] and rm['header']['version']==[0,1,15]
 assert load(RP/'texts/languages.json')==['zh_CN','zh_TW','en_US']
 ls={loc:lang(RP/f'texts/{loc}.lang') for loc in ('zh_CN','zh_TW','en_US')}
 assert all(len(data)==108 for data,_ in ls.values())
 assert ls['zh_CN'][1]==ls['zh_TW'][1]==ls['en_US'][1]
 assert set(ls['zh_CN'][0])==set(ls['zh_TW'][0])==set(ls['en_US'][0])
 body=[k for k in ls['zh_CN'][0] if k.startswith('guide.kg.body.')]
 assert len(body)==66
 assert ls['zh_TW'][0]['guide.kg.name.guide_recipe_bun_slice']=='饅頭片串'
 assert ls['zh_CN'][0]['guide.kg.name.guide_recipe_bun_slice']=='馒头片串'
 assert ls['en_US'][0]['guide.kg.name.guide_recipe_bun_slice']=='Bun Slice Skewer'

 mech=load(GUIDE/'a115-localized-mechanics.json');assert mech['locales']==['zh_CN','zh_TW','en_US'] and len(mech['entries'])==33
 for id_,row in mech['entries'].items():
  assert set(row)=={'zh_CN','zh_TW','en_US'}
  for loc in row:
   slug=id_.split(':',1)[1]
   for i,line in enumerate(row[loc],1):assert ls[loc][0][f'guide.kg.body.{slug}.{i}']==line
 cn='\n'.join(x for row in mech['entries'].values() for x in row['zh_CN'])
 tw='\n'.join(x for row in mech['entries'].values() for x in row['zh_TW'])
 assert not sorted({ch for ch in CN_BAD if ch in cn}),[(ch,[x for x in cn.splitlines() if ch in x][:3]) for ch in CN_BAD if ch in cn]
 assert not sorted({ch for ch in TW_BAD if ch in tw}),[(ch,[x for x in tw.splitlines() if ch in x][:3]) for ch in TW_BAD if ch in tw]
 assert '材料顺序：鳕鱼 / 鲑鱼 / 热带鱼 / 河豚' in cn
 assert '材料顺序：生馒头片 → 生馒头片 → 生馒头片' in cn
 assert '材料顺序：生小肉块 → 骨头 → 生小肉块' in cn
 assert '材料顺序：生面团 → 生面团' in cn

 p=payload();assert p['version']=='0.1.15' and len(p['entries'])==33
 assert p['names']['zh_TW']['kg_a1:guide_recipe_bun_slice']=='饅頭片串'
 byid={x['id']:x for x in p['entries']}
 for id_,row in mech['entries'].items():assert byid[id_]['mechanics']==row['zh_TW']
 publisher=(BP/'scripts/publisher.js').read_text(encoding='utf-8');assert "export const REVISION = 'a1_15_0';" in publisher
 report=load(GUIDE/'a115-localization-report.json')
 assert report['language_key_count']=={'zh_CN':108,'zh_TW':108,'en_US':108}
 assert report['body_keys_per_locale']==66 and report['runtime_labels_follow_host_language'] is True
 assert report['runtime_body_locale_switch_on_stock_cookery_1_0_6'] is False and report['host_modified'] is False
 for pth in (BP/'scripts/payload.js',BP/'scripts/publisher.js',BP/'scripts/main.js'):subprocess.run(['node','--check',str(pth)],check=True)

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
 out=GUIDE/('a115-dash-verification.json' if a.compiled else 'a115-structure-verification.json')
 out.write_text(json.dumps({'version':'A1.15','language_files':3,'keys_per_locale':108,'body_keys_per_locale':66,'localized_entries':33,'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))
if __name__=='__main__':main()
