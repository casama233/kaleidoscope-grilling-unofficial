from __future__ import annotations
from pathlib import Path
import argparse,json

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
GROUP_KEY='kaleidoscope_grilling:itemGroup.main'
HIDDEN={
 'unfinished_skewer','secret_skewer','pending_seasoning','skewer_plate',
 'canola_oil_brush','secret_chili_oil_brush','premium_chili_oil_brush',
}

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def lang(path):
 out={}
 for line in path.read_text(encoding='utf-8').splitlines():
  if '=' in line:
   k,v=line.split('=',1);out[k]=v
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,23] and rm['header']['version']==[2,7,23]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.23 Creative Catalog BP'
 for item_id in HIDDEN:
  d=load(BP/'items'/f'{item_id}.json')['minecraft:item']['description']
  assert d['menu_category']=={'category':'none'},item_id
 catalog=load(BP/'item_catalog/crafting_item_catalog.json')
 assert catalog['format_version']=='1.21.60'
 cats=catalog['minecraft:crafting_items_catalog']['categories'];assert len(cats)==1
 assert cats[0]['category_name']=='items' and len(cats[0]['groups'])==1
 group=cats[0]['groups'][0]
 assert group['group_identifier']=={'icon':'kaleidoscope_grilling:grill','name':GROUP_KEY}
 ids=group['items'];assert len(ids)==len(set(ids))==76
 assert ids[:3]==['kaleidoscope_grilling:grill','kaleidoscope_grilling:oil_press','kaleidoscope_grilling:big_vat']
 assert all(('kaleidoscope_grilling:'+x) not in ids for x in HIDDEN)
 all_items={p.stem for p in (BP/'items').glob('*.json')}
 catalog_items={x.split(':',1)[1] for x in ids if x.startswith('kaleidoscope_grilling:') and x.split(':',1)[1] in all_items}
 assert catalog_items==all_items-HIDDEN
 zhc=lang(RP/'texts/zh_CN.lang');zht=lang(RP/'texts/zh_TW.lang');en=lang(RP/'texts/en_US.lang')
 assert zhc[GROUP_KEY]=='森罗物语：烟火' and zht[GROUP_KEY]=='森羅物語：煙火' and en[GROUP_KEY]=='Kaleidoscope Grilling'
 assert zhc['item.kaleidoscope_grilling:pending_seasoning.name']=='待摇晃的调料'
 assert zhc['item.kaleidoscope_grilling:secret_skewer.name']=='秘制烤串'
 report=load(P/'reports/a2723-creative-catalog.json')
 assert report['version']=='A2.7.23' and report['bedrock_equivalent']['catalog_entry_count']==76
 assert set(report['hidden_internal_items'])==HIDDEN
 assert report['java_order_preserved_for_existing_static_content'] is True
 assert report['minecraft_tested'] is False and report['bds_tested'] is False
 if a.compiled:
  dist=P/'builds/dist'
  for source in (BP,RP):
   manifest=load(source/'manifest.json')
   matches=[x.parent for x in dist.rglob('manifest.json') if load(x).get('header',{}).get('uuid')==manifest['header']['uuid']]
   assert len(matches)==1,(source,matches);target=matches[0]
   for p in source.rglob('*'):
    if not p.is_file() or p.name.startswith('.'):continue
    q=target/p.relative_to(source);assert q.is_file(),str(q)
    if p.suffix=='.json':assert load(p)==load(q),str(q)
    else:assert p.read_bytes()==q.read_bytes(),str(q)
 print(json.dumps({'version':'A2.7.23','creative_catalog':True,'hidden_internal_items':sorted(HIDDEN),'compiled':a.compiled,'minecraft_tested':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
