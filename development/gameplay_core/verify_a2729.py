from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
SIMPLIFIED_RESIDUAL='烧馒猪儿鸡鱼鱿须黄连调制摇盘谱饼红萝块葱凉图龙绿边层发后里这头种与为开关处过复气区对应该显条数类别样时间满还从实体储备传页简选择进词义虫面罗语烟'

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def lang(p):
 out={};order=[]
 for line in p.read_text(encoding='utf-8-sig').splitlines():
  if '=' not in line:continue
  k,v=line.split('=',1);assert k not in out,k;out[k]=v;order.append(k)
 return out,order

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,29] and rm['header']['version']==[2,7,29]
 assert load(RP/'texts/languages.json')==['zh_CN','zh_TW','en_US']
 cn,co=lang(RP/'texts/zh_CN.lang');tw,to=lang(RP/'texts/zh_TW.lang');en,eo=lang(RP/'texts/en_US.lang')
 assert len(cn)==len(tw)==len(en)==96 and co==to==eo and set(cn)==set(tw)==set(en)
 assert tw['item.kaleidoscope_grilling:grilled_bun_slice_skewer.name']=='烤饅頭片串'
 assert tw['item.kaleidoscope_grilling:raw_bun_slice_skewer.name']=='生饅頭片串'
 assert tw['item.kaleidoscope_grilling:raw_mantou_slice.name']=='生饅頭片'
 assert tw['kaleidoscope_grilling:itemGroup.main']=='森羅物語：煙火'
 corpus='\n'.join(tw.values())
 hits=sorted({ch for ch in SIMPLIFIED_RESIDUAL if ch in corpus})
 assert not hits,hits
 report=load(P/'reports/a2729-language-hotfix.json');assert report['fixed_occurrences']==3 and report['gameplay_logic_changed'] is False
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)
 compiled=[]
 if a.compiled:
  dist=P/'builds/dist'
  for name,source in [('behavior_pack',BP),('resource_pack',RP)]:
   manifest=load(source/'manifest.json');matches=[x.parent for x in dist.rglob('manifest.json') if load(x).get('header',{}).get('uuid')==manifest['header']['uuid']];assert len(matches)==1,(name,matches);target=matches[0];count=0
   for f in source.rglob('*'):
    if not f.is_file() or f.name.startswith('.'):continue
    q=target/f.relative_to(source);assert q.is_file(),str(q)
    if f.suffix=='.json':assert load(f)==load(q),str(q)
    else:assert f.read_bytes()==q.read_bytes(),str(q)
    count+=1
   compiled.append({'pack':name,'compared_files':count,'matches_source':True})
 out=P/'reports'/('a2729-dash-verification.json' if a.compiled else 'a2729-structure-verification.json')
 out.write_text(json.dumps({'version':'A2.7.29','languages':['zh_CN','zh_TW','en_US'],'keys':96,'traditional_residuals':0,'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))
if __name__=='__main__':main()
