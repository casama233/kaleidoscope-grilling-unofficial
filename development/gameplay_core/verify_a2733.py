from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
HAND_ID='geometry.kg_a2733.seasoning_bottle_hand'
RC_ID='controller.render.kg_a2733.seasoning_bottle_hand'
ATLAS_KEY='kg_a2733_seasoning_bottle'
ITEMS=('empty_seasoning_bottle','pending_seasoning','special_seasoning')
PLACED=(
 ('seasoning_bottle.geo.json','seasoning_bottle.json','geometry.kg_a2733.seasoning_bottle_legacy'),
 ('seasoning_bottles_1.geo.json','seasoning_bottle_1.json','geometry.kg_a2733.seasoning_bottles_1'),
 ('seasoning_bottles_2.geo.json','seasoning_bottle_2.json','geometry.kg_a2733.seasoning_bottles_2'),
 ('seasoning_bottles_3.geo.json','seasoning_bottle_3.json','geometry.kg_a2733.seasoning_bottles_3'),
 ('seasoning_bottles_4.geo.json','seasoning_bottle_4.json','geometry.kg_a2733.seasoning_bottles_4'),
)

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def geom(doc,identifier=None):
 rows=doc['minecraft:geometry']
 if identifier is None:
  assert len(rows)==1
  return rows[0]
 rows=[g for g in rows if g.get('description',{}).get('identifier')==identifier]
 assert len(rows)==1,(identifier,[g.get('description',{}).get('identifier') for g in doc['minecraft:geometry']])
 return rows[0]

def suffix_map(g,prefix):
 return {b['name'].replace(prefix,'',1):b for b in g['bones'] if b['name'].startswith(prefix)}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)

 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,33] and rm['header']['version']==[2,7,33]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.33 Seasoning Bottle Corrective BP'

 # Held model: no root animation, exact immersion-lab hand-space shell.
 hand=geom(load(RP/'models/entity/a2733_seasoning_bottle_hand.geo.json'),HAND_ID)
 assert hand['bones'][0]['name']=='root'
 assert hand['bones'][0]['binding']=='q.item_slot_to_bone_name(context.item_slot)'
 assert hand['description']['visible_bounds_width']==3
 assert hand['description']['visible_bounds_height']==3

 proto_doc=load(ROOT/'projects/grilling/integration/immersion_lab/resource_pack/models/entity/hand_props.geo.json')
 proto=geom(proto_doc,'geometry.kg_imm.hand_seasoning')
 hmap=suffix_map(hand,'instance_0_');pmap=suffix_map(proto,'season_instance_0_')
 assert set(hmap)==set(hmap)&set(pmap)
 for name,b in hmap.items():
  assert name in pmap,name
  hc=b.get('cubes',[]);pc=pmap[name].get('cubes',[])
  assert len(hc)==len(pc),(name,len(hc),len(pc))
  for x,y in zip(hc,pc):
   assert x['origin']==y['origin'],(name,x['origin'],y['origin'])
   assert x['size']==y['size'],(name,x['size'],y['size'])

 rc=load(RP/'render_controllers/a2733_seasoning_bottle_hand.render_controllers.json')
 assert rc['render_controllers'][RC_ID]=={
  'geometry':'Geometry.default',
  'materials':[{'*':'Material.default'}],
  'textures':['Texture.default']
 }

 for item in ITEMS:
  desc=load(RP/'attachables'/f'{item}.attachable.json')['minecraft:attachable']['description']
  assert desc['identifier']==f'kaleidoscope_grilling:{item}'
  assert desc['geometry']=={'default':HAND_ID}
  assert desc['textures']=={'default':'textures/blocks/seasoning_bottle'}
  assert desc['materials']=={'default':'entity_alphablend'}
  assert 'animations' not in desc
  assert 'scripts' not in desc
  assert desc['render_controllers']==[RC_ID]

 # Placed blocks: explicit custom geometry + fresh atlas key only, never full-block.
 terrain=load(RP/'textures/terrain_texture.json')
 assert terrain['texture_data'][ATLAS_KEY]=={'textures':'textures/blocks/seasoning_bottle'}
 assert (RP/'textures/blocks/seasoning_bottle.png').is_file()

 total_cubes=0
 for geo_name,block_name,identifier in PLACED:
  g=geom(load(RP/'models/blocks'/geo_name))
  assert g['description']['identifier']==identifier
  assert not any(b.get('binding') for b in g['bones'])
  cubes=[c for b in g['bones'] for c in b.get('cubes',[])]
  assert cubes,geo_name
  assert all(len(c.get('size',[]))==3 and all(float(v)>0 for v in c['size']) for c in cubes),geo_name
  total_cubes+=len(cubes)

  comp=load(BP/'blocks'/block_name)['minecraft:block']['components']
  assert comp['minecraft:geometry']=={'identifier':identifier}
  assert comp['minecraft:geometry']['identifier']!='minecraft:geometry.full_block'
  mat=comp['minecraft:material_instances']['*']
  assert mat=={
   'texture':ATLAS_KEY,
   'render_method':'blend',
   'ambient_occlusion':0.0,
   'face_dimming':False
  }

 # Historical A2.7.26 transform resource may remain, but nothing points at it.
 for item in ITEMS:
  raw=(RP/'attachables'/f'{item}.attachable.json').read_text(encoding='utf-8')
  assert 'a2726_seasoning_bottle_hold' not in raw
  assert 'geometry.kg_a2726.seasoning_bottle_hand' not in raw

 report=load(P/'reports/a2733-seasoning-bottle-corrective.json')
 assert report['version']=='A2.7.33'
 assert report['held']['bound_root_animation_removed'] is True
 assert report['held']['verified_against']=='geometry.kg_imm.hand_seasoning'
 assert report['placed']['variants']==5
 assert report['placed']['fresh_terrain_texture_key']==ATLAS_KEY
 assert report['placed']['no_full_block_geometry'] is True
 assert report['gameplay_logic_changed'] is False
 assert report['minecraft_tested'] is False and report['bds_tested'] is False

 # Preserve current A2.7.32 runtime architecture.
 main=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert "import './a2732_standalone_food_effect_runtime.js';" in main
 assert "import './a2731_farmland_crop_host_runtime.js';" in main
 assert "import './a2727_cookery_host_recipes_runtime.js';" in main

 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

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
  'version':'A2.7.33',
  'held_items':3,
  'held_root_animation_removed':True,
  'held_geometry_verified_against_immersion_lab':True,
  'placed_variants':5,
  'fresh_geometry_identifiers':True,
  'fresh_terrain_texture_key':True,
  'positive_placed_cubes':total_cubes,
  'no_full_block_geometry':True,
  'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2733-dash-verification.json' if a.compiled else 'a2733-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))

if __name__=='__main__':
 main()
