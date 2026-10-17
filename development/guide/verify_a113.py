from __future__ import annotations
import argparse,hashlib,json,re,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
GUIDE=ROOT/'projects/grilling/integration/cookery106';BP=GUIDE/'behavior_pack';RP=GUIDE/'resource_pack'
GAME=ROOT/'projects/grilling/gameplay_core'
UI=RP/'textures/ui/kg_grilling'
EXPECTED_ICONS={
 'guide_grill':'blocks/grill.png','guide_plate':'items/skewer_plate.png','guide_crops':'items/canola_seeds.png',
 'guide_threading':'items/raw_beef_skewer.png','guide_oil':'blocks/oil_press.png','guide_recipe_book':'items/skewer_recipe_book.png',
 'guide_seasoning':'items/special_seasoning.png','guide_houttuynia_powder':'items/houttuynia_powder.png',
 'guide_totem_powder':'items/totem_powder.png','guide_dragon_egg_powder':'items/dragon_egg_powder.png',
 'guide_sichuan_pepper':'items/sichuan_pepper.png',
}

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def payload():
 s=(BP/'scripts/payload.js').read_text(encoding='utf-8').strip()
 prefix='// Generated A1.13 player-facing Cookery guide extension.\nexport const GUIDE_PAYLOAD = '
 assert s.startswith(prefix) and s.endswith(';')
 return json.loads(s[len(prefix):-1])

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[0,1,13] and rm['header']['version']==[0,1,13]
 assert 'PLAYER GUIDE' in bm['header']['name'] and 'PLAYER GUIDE' in rm['header']['name']
 p=payload()
 assert p['api']==1 and p['id']=='kg_a1:grilling' and p['version']=='0.1.13'
 assert p['text']['zh_CN']['title']=='森罗物语：烟火'
 assert p['text']['zh_TW']['title']=='森羅物語：煙火'
 assert [x['id'] for x in p['categories']]==['how_to','recipes','seasonings']
 assert len({x['icon'] for x in p['categories']})==3
 assert p['text']['zh_CN']['how_to']=='玩法与取得方式'
 assert p['text']['zh_TW']['how_to']=='玩法與取得方式'
 assert p['text']['zh_CN']['recipes']=='烤串食谱'
 assert p['text']['zh_TW']['recipes']=='烤串食譜'

 entries=p['entries'];assert len(entries)==33
 assert sum(x['category']=='how_to' for x in entries)==6
 assert sum(x['category']=='recipes' for x in entries)==20
 assert sum(x['category']=='seasonings' for x in entries)==7
 how=[x for x in entries if x['category']=='how_to']
 assert len({x['icon'] for x in how})==6
 assert p['names']['zh_CN']['kg_a1:guide_grill']=='烧烤架'
 assert p['names']['zh_CN']['kg_a1:guide_oil']=='榨油器与大缸'
 assert p['names']['zh_CN']['kg_a1:guide_recipe_book']=='串谱与快速制作'
 assert p['names']['zh_TW']['kg_a1:guide_plate']=='串盤與保存'
 assert p['names']['zh_TW']['kg_a1:guide_threading']=='手工穿串'

 bad=('素材預覽','素材预览','來源參考','来源参考','source reference','Static model reference','not implemented','開發中','开发中','Source result','Ordered slots')
 corpus=json.dumps(p,ensure_ascii=False)
 for word in bad:assert word not in corpus,word
 assert 'kg_a1:guide_recipe_beef' in p['names']['zh_CN']
 assert all(not re.search(r'kaleidoscope_(?:grilling|cookery):',line) for e in entries for line in e.get('mechanics',[]))

 for name,rel in EXPECTED_ICONS.items():
  src=GAME/'resource_pack/textures'/rel;dst=UI/f'{name}.png'
  assert src.is_file() and dst.is_file() and sha(src)==sha(dst),(name,src,dst)

 publisher=(BP/'scripts/publisher.js').read_text(encoding='utf-8')
 assert "export const REVISION = 'a1_13_0';" in publisher
 assert "export const SOURCE = 'kg_grilling';" in publisher
 assert 'kaleidoscope_cookery:guidebook_begin' in publisher
 subprocess.run(['node','--check',str(BP/'scripts/payload.js')],check=True)
 subprocess.run(['node','--check',str(BP/'scripts/publisher.js')],check=True)
 subprocess.run(['node','--check',str(BP/'scripts/main.js')],check=True)

 report=load(GUIDE/'a113-guide-report.json')
 assert report['entry_count']==33 and report['recipe_entries']==20
 assert report['distinct_category_icons']==3
 assert report['standalone_book_item'] is False and report['host_modified'] is False
 assert report['minecraft_tested'] is False and report['bds_tested'] is False

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

 result={'version':'A1.13','player_facing_guide':True,'entries':33,'recipes':20,'how_to':6,'seasonings':7,
         'distinct_how_to_icons':6,'compiled':a.compiled,'compiled_packs':compiled,
         'minecraft_tested':False,'bds_tested':False}
 out=GUIDE/('a113-dash-verification.json' if a.compiled else 'a113-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))
if __name__=='__main__':main()
