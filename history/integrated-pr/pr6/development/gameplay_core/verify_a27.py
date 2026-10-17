from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,subprocess
import augment_a27 as a27

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
COOKERY_BP='10f37ae2-9ccf-435f-b34b-0eec8191cd94';COOKERY_RP='c89dc8df-c3fc-4bc8-8bd0-527abba76681';CV=[1,0,6]

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def git_blob(p):
 v=p.read_bytes();return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');args=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,0] and rm['header']['version']==[2,7,0]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7 Gameplay BP'
 assert rm['header']['name']=='Kaleidoscope Grilling A2.7 Gameplay RP'
 assert {'uuid':COOKERY_BP,'version':CV} in bm['dependencies'] and {'uuid':COOKERY_RP,'version':CV} in rm['dependencies']
 assert {'module_name':'@minecraft/server','version':'2.9.0'} in bm['dependencies']

 for id in a27.ITEMS:
  item=load(BP/f'items/{id}.json')['minecraft:item']
  assert item['description']['identifier']==f'kaleidoscope_grilling:{id}',id
  assert git_blob(RP/f'textures/items/{id}.png')==a27.TEXTURES[id],id
  assert load(RP/'textures/item_texture.json')['texture_data'][id]['textures']==f'textures/items/{id}'
 for id,(nutrition,saturation,max_stack,always) in a27.FOOD.items():
  c=load(BP/f'items/{id}.json')['minecraft:item']['components']
  assert c['minecraft:max_stack_size']==max_stack,id
  f=c['minecraft:food'];assert f['nutrition']==nutrition and abs(f['saturation_modifier']-saturation)<1e-9 and f['can_always_eat']==always,id
 powder=load(BP/'items/sweet_potato_powder.json')['minecraft:item']['components']
 assert powder['minecraft:use_modifiers']['use_duration']==1.5 and powder['minecraft:use_animation']['value']=='bow'

 mainjs=(BP/'scripts/main.js').read_text(encoding='utf-8');assert "import './a27_food_runtime.js';" in mainjs
 rt=(BP/'scripts/a27_food_runtime.js').read_text(encoding='utf-8')
 for token in ("A27_EFFECTS","sweet_potato_powder","itemCompleteUse","kaleidoscope_grilling:a21_fx"):assert token in rt,token
 core=(BP/'scripts/a27_content_core.js').read_text(encoding='utf-8')
 for token in ("wedding_candy","ticks:300","ticks:1200","compatibilityFallback:17"):assert token in core,token

 catalog=load(P/'reports/a27-recipe-catalog.json')
 assert len(catalog['mapped'])==25
 assert len([x for x in catalog['mapped'] if x['mode']=='crafting_table_fallback'])==17
 assert len([x for x in catalog['mapped'] if x['mode']!='crafting_table_fallback'])==8
 assert catalog['dynamic_deferred'][0]['recipe']=='cold_houttuynia'
 assert catalog['optional_deferred'][0]['recipe']=='sour_spicy_noodles'
 for x in catalog['mapped']:
  assert x['result']

 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a27_core.mjs')],check=True)

 parity=load(P/'reports/a27-parity.json')
 assert parity['version']=='A2.7.0' and parity['items_added']==27 and parity['food_items_added']==15
 assert parity['sweet_potato_powder_knead_ticks']==30
 assert parity['recipe_reconciliation']['workstation_survival_fallbacks']==17

 compiled=[]
 if args.compiled:
  dist=P/'builds/dist'
  for name,source in [('behavior_pack',BP),('resource_pack',RP)]:
   manifest=load(source/'manifest.json')
   matches=[p.parent for p in dist.rglob('manifest.json') if load(p).get('header',{}).get('uuid')==manifest['header']['uuid']]
   assert len(matches)==1,(name,matches);target=matches[0];count=0
   for p in source.rglob('*'):
    if not p.is_file() or p.name.startswith('.'):continue
    q=target/p.relative_to(source);assert q.is_file(),str(q)
    if p.suffix=='.json':assert load(p)==load(q),str(q)
    else:assert p.read_bytes()==q.read_bytes(),str(q)
    count+=1
   compiled.append({'pack':name,'compared_files':count,'matches_source':True})

 result={'version':'A2.7.0','items':27,'foods':15,'recipe_mappings':25,'fallbacks':17,
  'compiled':args.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False}
 out=P/'reports'/('a27-dash-verification.json' if args.compiled else 'a27-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
