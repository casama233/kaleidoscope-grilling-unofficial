from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
FORBIDDEN=('烧','馒','猪','儿','鸡','鱼','鱿','须','黄','连','调','制','摇','盘','谱','饼','红','萝','块','葱','凉','图','龙','绿')
TW_EXPECT={
 'item.kaleidoscope_grilling:grilled_chicken_skin_skewer.name':'烤雞皮串',
 'item.kaleidoscope_grilling:raw_squid_tentacle_skewer.name':'生魷魚鬚串',
 'item.kaleidoscope_grilling:grilled_gluten_skewer.name':'烤麵筋串',
 'item.kaleidoscope_grilling:raw_potato_slice_skewer.name':'生馬鈴薯片串',
 'item.kaleidoscope_grilling:sweet_potato.name':'番薯',
 'item.kaleidoscope_grilling:totem_powder.name':'不死圖騰粉',
 'tile.kaleidoscope_grilling:grill.name':'燒烤架',
 'kaleidoscope_grilling:itemGroup.main':'森羅物語：煙火',
}
CN_EXPECT={
 'item.kaleidoscope_grilling:green_chili_powder.name':'绿辣椒粉',
 'item.kaleidoscope_grilling:houttuynia_powder.name':'折耳根粉',
 'item.kaleidoscope_grilling:totem_powder.name':'不死图腾粉',
 'tile.kaleidoscope_grilling:houttuynia_crop.name':'折耳根',
}

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
 assert bm['header']['version']==[2,7,27] and rm['header']['version']==[2,7,27]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.27 Localization BP'
 assert load(RP/'texts/languages.json')==['zh_CN','zh_TW','en_US']
 cn,co=lang(RP/'texts/zh_CN.lang');tw,to=lang(RP/'texts/zh_TW.lang');en,eo=lang(RP/'texts/en_US.lang')
 assert len(cn)==len(tw)==len(en)==96
 assert co==to==eo and set(cn)==set(tw)==set(en)
 for k,v in CN_EXPECT.items():assert cn[k]==v,(k,cn[k])
 for k,v in TW_EXPECT.items():assert tw[k]==v,(k,tw[k])
 # Values in the Traditional file must not regress to the obvious Simplified forms seen in A1.13.
 corpus='\n'.join(tw.values())
 for ch in FORBIDDEN:assert ch not in corpus,(ch,[v for v in tw.values() if ch in v][:5])
 assert '馬鈴薯' in corpus and '番薯' in corpus and '不死圖騰粉' in corpus
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)
 report=load(P/'reports/a2727-localization.json')
 assert report['language_keys']==96 and report['equal_key_sets'] is True and report['gameplay_logic_changed'] is False

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
 out=P/'reports'/('a2727-dash-verification.json' if a.compiled else 'a2727-structure-verification.json')
 out.write_text(json.dumps({'version':'A2.7.27','languages':['zh_CN','zh_TW','en_US'],'keys':96,'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))
if __name__=='__main__':main()
