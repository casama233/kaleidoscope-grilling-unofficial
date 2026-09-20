from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
COOKERY_BP='10f37ae2-9ccf-435f-b34b-0eec8191cd94';COOKERY_RP='c89dc8df-c3fc-4bc8-8bd0-527abba76681';COOKERY_VER=[1,0,6]

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 report=load(P/'reports/build.json');a21=load(P/'reports/a21-build.json')
 assert report['version']=='A2.1.0' and a21['version']=='A2.1.0'
 assert report['cookable_fixed_skewers']==19 and report['formal_skewer_items']==41
 assert report['cookery_oil_pot_direct'] is True and report['cookery_oil_property']=='kc_oil_count'
 assert report['seasoning_max_uses']==16 and report['seasoning_capacity']==8 and report['pending_shake_ticks']==80
 assert report['hot_time_source']=='world.getAbsoluteTime()' and report['hot_bucket_ticks']==100 and report['hot_saturation_percent']==125
 assert report['held_3d_attachables']==39
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,1,0] and rm['header']['version']==[2,1,0]
 assert {'uuid':COOKERY_BP,'version':COOKERY_VER} in bm['dependencies']
 assert {'uuid':COOKERY_RP,'version':COOKERY_VER} in rm['dependencies']
 assert {'module_name':'@minecraft/server','version':'2.9.0'} in bm['dependencies']
 items=list((BP/'items').glob('*.json'));assert len(items)==53,len(items)
 for item in ('green_chili_powder','sichuan_pepper','onion_powder','houttuynia_powder','totem_powder','dragon_egg_powder','pending_seasoning'):
  assert (BP/'items'/f'{item}.json').is_file();assert (RP/'textures/items'/f'{item}.png').is_file()
 empty=load(BP/'items/empty_seasoning_bottle.json')['minecraft:item']['components']
 assert empty['minecraft:block_placer']['block']=='kaleidoscope_grilling:seasoning_bottle'
 pending=load(BP/'items/pending_seasoning.json')['minecraft:item']['components']
 assert pending['minecraft:use_modifiers']['use_duration']==4.0 and pending['minecraft:use_animation']=={'value':'none'}
 bottle=load(BP/'blocks/seasoning_bottle.json')['minecraft:block'];assert bottle['description']['identifier']=='kaleidoscope_grilling:seasoning_bottle'
 assert bottle['components']['minecraft:geometry']=='geometry.kg_a21.seasoning_bottle'
 attaches=list((RP/'attachables').glob('*.attachable.json'));assert len(attaches)==39,len(attaches)
 for p in attaches:
  d=load(p)['minecraft:attachable']['description'];assert d['identifier'].startswith('kaleidoscope_grilling:');assert d['geometry']['default'].startswith('geometry.kg_a21.')
 geos=list((RP/'models/entity/a21').glob('*.geo.json'));assert len(geos)==39
 runtime=(BP/'scripts/main.js').read_text()
 for token in ["kaleidoscope_cookery:oil_pot_filled","kc_oil_count","world.getAbsoluteTime()","seasonings","heavy_metal_poisoning","projectile_dodge","ordinary_skewer","hot_until","entityHitEntity"]:
  assert token in runtime,token
 core=(BP/'scripts/core_logic.js').read_text();assert 'seasonings:[]' in core and 'MAX_SEASONING_INGREDIENTS=8' in core
 shake=load(RP/'animations/a21_shake.animation.json')['animations'];assert set(shake)=={'animation.kg_a21.player.shake.main','animation.kg_a21.player.shake.off'}
 for p in BP.glob('scripts/*.js'):subprocess.run(['node','--check',str(p)],check=True)
 compiled=[]
 if a.compiled:
  dist=P/'builds/dist'
  for name,source in [('behavior_pack',BP),('resource_pack',RP)]:
   manifest=load(source/'manifest.json');matches=[p.parent for p in dist.rglob('manifest.json') if load(p).get('header',{}).get('uuid')==manifest['header']['uuid']]
   assert len(matches)==1,(name,matches);target=matches[0];count=0
   for p in source.rglob('*'):
    if not p.is_file() or p.name.startswith('.'):continue
    q=target/p.relative_to(source);assert q.is_file(),str(q)
    if p.suffix=='.json':assert load(p)==load(q),str(q)
    else:assert p.read_bytes()==q.read_bytes(),str(q)
    count+=1
   compiled.append({'pack':name,'compared_files':count,'matches_source':True})
 result={'version':'A2.1.0','formal_items':len(items),'formal_foods':41,'cookable_fixed_skewers':19,'cookery_oil_direct':True,'seasoning_bottle_block':True,'held_3d_attachables':len(attaches),'server_module':'2.9.0','compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False}
 out=P/'reports'/('a21-dash-verification.json' if a.compiled else 'a21-structure-verification.json');out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(out.read_text())

if __name__=='__main__':main()
