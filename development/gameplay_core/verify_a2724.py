from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,subprocess
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
TEX_SHA='57936897efae12b743a539f0bf1dac54d45dda39'
RED_ID='kaleidoscope_grilling:red_chili_powder'
HIDDEN={
 'unfinished_skewer','secret_skewer','pending_seasoning','skewer_plate',
 'canola_oil_brush','secret_chili_oil_brush','premium_chili_oil_brush',
}
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def blob(path):
 v=path.read_bytes();return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,24] and rm['header']['version']==[2,7,24]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.24 Red Chili Processing BP'

 item=load(BP/'items/red_chili_powder.json')['minecraft:item'];c=item['components']
 assert item['description']['identifier']==RED_ID
 assert item['description']['menu_category']=={'category':'items'}
 assert c['minecraft:max_stack_size']==64 and 'minecraft:food' not in c
 tex=RP/'textures/items/red_chili_powder.png';assert tex.is_file() and blob(tex)==TEX_SHA
 with Image.open(tex) as im:assert im.size==(16,16)
 assert load(RP/'textures/item_texture.json')['texture_data']['red_chili_powder']['textures']=='textures/items/red_chili_powder'

 catalog=load(BP/'item_catalog/crafting_item_catalog.json')
 group=catalog['minecraft:crafting_items_catalog']['categories'][0]['groups'][0]
 ids=group['items'];assert len(ids)==len(set(ids))==77
 i=ids.index(RED_ID)
 assert ids[i-1]=='kaleidoscope_grilling:canola_powder'
 assert ids[i+1]=='kaleidoscope_grilling:onion'
 all_items={p.stem for p in (BP/'items').glob('*.json')}
 catalog_items={x.split(':',1)[1] for x in ids if x.startswith('kaleidoscope_grilling:') and x.split(':',1)[1] in all_items}
 assert catalog_items==all_items-HIDDEN

 core=BP/'scripts/a2724_red_chili_processing_core.js';runtime=BP/'scripts/a2724_red_chili_processing_runtime.js'
 assert core.read_bytes()==(DEV/'a2724_red_chili_processing_core.js').read_bytes()
 assert runtime.read_bytes()==(DEV/'a2724_red_chili_processing_runtime.js').read_bytes()
 main=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert main.count("import './a2724_red_chili_processing_runtime.js';")==1
 assert 'api_ping' not in runtime.read_text(encoding='utf-8') and 'KC_PING_EVENT' not in runtime.read_text(encoding='utf-8')

 oil=load(BP/'recipes/secret_chili_oil.json')['minecraft:recipe_shapeless']
 assert oil['description']['identifier']=='kaleidoscope_grilling:secret_chili_oil'
 assert oil['tags']==['crafting_table']
 assert oil['ingredients']==[
  {'item':'kaleidoscope_grilling:canola_oil_bucket'},
  {'item':RED_ID},{'item':RED_ID},{'item':RED_ID}
 ]
 assert oil['result']=={'item':'kaleidoscope_grilling:secret_chili_oil_bucket','count':1}

 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2724_core.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2724-parity.json')
 assert report['version']=='A2.7.24'
 assert report['creative_catalog']['catalog_entry_count']==77
 assert report['creative_catalog']['java_registration_order_neighbors']==[
  'kaleidoscope_grilling:canola_powder',RED_ID,'kaleidoscope_grilling:onion']
 assert report['millstone']['input']=='kaleidoscope_cookery:red_chili'
 assert report['secret_chili_oil']['ingredients'][RED_ID]==3
 assert report['survival_chain']['secret_chili_oil_survival_entry_complete'] is True
 assert report['minecraft_tested'] is False and report['bds_tested'] is False

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

 result={
  'version':'A2.7.24','red_chili_powder_item':True,'cookery_millstone_registered':True,
  'secret_chili_oil_native_recipe':True,'powder_per_bucket':3,'creative_catalog_entries':77,
  'secret_chili_oil_survival_entry_complete':True,'additional_api_ping':False,
  'a2723_creative_catalog_preserved':True,'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2724-dash-verification.json' if a.compiled else 'a2724-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))
if __name__=='__main__':main()
