from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
OFFSET=[0,-6,0]
HAND_GEO='geometry.kg_a2726.seasoning_bottle_hand'
HAND_GEO_FILE=RP/'models/entity/a2726_seasoning_bottle_hand.geo.json'
ANIM_FILE=RP/'animations/a2726_seasoning_bottle_hold.animation.json'
FIRST='animation.kaleidoscope_grilling.a2726.seasoning_bottle_hold_first_person'
THIRD='animation.kaleidoscope_grilling.a2726.seasoning_bottle_hold_third_person'
ITEMS=('empty_seasoning_bottle','pending_seasoning','special_seasoning')
VARIANTS=(
 ('seasoning_bottle.geo.json','seasoning_bottle.json','geometry.kg_a2726.seasoning_bottle_legacy',1),
 ('seasoning_bottles_1.geo.json','seasoning_bottle_1.json','geometry.kg_a2726.seasoning_bottles_1',1),
 ('seasoning_bottles_2.geo.json','seasoning_bottle_2.json','geometry.kg_a2726.seasoning_bottles_2',2),
 ('seasoning_bottles_3.geo.json','seasoning_bottle_3.json','geometry.kg_a2726.seasoning_bottles_3',3),
 ('seasoning_bottles_4.geo.json','seasoning_bottle_4.json','geometry.kg_a2726.seasoning_bottles_4',4),
)

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def geometry(doc,identifier=None):
 geos=doc['minecraft:geometry']
 if identifier is None:
  assert len(geos)==1
  return geos[0]
 rows=[g for g in geos if g.get('description',{}).get('identifier')==identifier]
 assert len(rows)==1,(identifier,[g.get('description',{}).get('identifier') for g in geos])
 return rows[0]
def bone(doc,suffix,identifier=None):
 rows=[b for b in geometry(doc,identifier)['bones'] if b['name'].endswith(suffix)]
 assert len(rows)==1,(suffix,[b['name'] for b in geometry(doc,identifier)['bones']])
 return rows[0]
def sub(a,b):return [round(a[i]-b[i],6) for i in range(3)]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,26] and rm['header']['version']==[2,7,26]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.26 Seasoning Bottle Render BP'

 total_cubes=0
 for geo_name,block_name,geo_id,bottles in VARIANTS:
  doc=load(RP/'models/blocks'/geo_name);geo=geometry(doc)
  assert geo['description']['identifier']==geo_id
  assert not [b for b in geo['bones'] if 'spice_empty' in b.get('name','')],geo_name
  cubes=[c for b in geo['bones'] for c in b.get('cubes',[])]
  assert len(cubes)==9*bottles,(geo_name,len(cubes),9*bottles)
  assert all(len(c.get('size',[]))==3 and all(float(x)>0 for x in c['size']) for c in cubes),geo_name
  total_cubes+=len(cubes)
  block=load(BP/'blocks'/block_name)['minecraft:block']['components']
  assert block['minecraft:geometry']==geo_id
  mat=block['minecraft:material_instances']['*']
  assert mat['ambient_occlusion']==0.0 and mat['face_dimming'] is False

 hand=load(HAND_GEO_FILE);hgeo=geometry(hand,HAND_GEO)
 root=hgeo['bones'][0]
 assert root['name']=='root' and root['binding']=='q.item_slot_to_bone_name(context.item_slot)'
 assert not [b for b in hgeo['bones'] if 'spice_empty' in b.get('name','')]
 assert len([c for b in hgeo['bones'] for c in b.get('cubes',[])])==9

 # Spatial proof from the independent A1.16 immersion-lab hand prototype:
 # its seasoning shell is the same source bottle translated by exactly [0,-6,0].
 proto=load(ROOT/'projects/grilling/integration/immersion_lab/resource_pack/models/entity/hand_props.geo.json')
 base=load(RP/'models/blocks/seasoning_bottles_1.geo.json')
 for suffix in ('glass_body_0','glass_shoulder_1','wood_stopper_7','front_label_8'):
  h=bone(base,suffix)['cubes'][0]
  p=bone(proto,'season_instance_0_'+suffix,'geometry.kg_imm.hand_seasoning')['cubes'][0]
  assert sub(p['origin'],h['origin'])==OFFSET,(suffix,p['origin'],h['origin'])

 anim=load(ANIM_FILE);assert anim['format_version']=='1.8.0'
 for key in (FIRST,THIRD):
  row=anim['animations'][key]
  assert row['loop'] is True and row['bones']['root']=={'position':OFFSET}

 for item in ITEMS:
  item_doc=load(BP/'items'/f'{item}.json')['minecraft:item']
  assert item_doc['components']['minecraft:hand_equipped'] is True
  desc=load(RP/'attachables'/f'{item}.attachable.json')['minecraft:attachable']['description']
  assert desc['identifier']==f'kaleidoscope_grilling:{item}'
  assert desc['materials']=={'default':'entity_alphablend'}
  assert desc['textures']=={'default':'textures/blocks/seasoning_bottle'}
  assert desc['geometry']=={'default':HAND_GEO}
  assert desc['animations']=={'hold_first_person':FIRST,'hold_third_person':THIRD}
  assert desc['scripts']['animate']==[
   {'hold_first_person':'context.is_first_person == 1.0'},
   {'hold_third_person':'context.is_first_person == 0.0'},
  ]
  assert desc['render_controllers']==['controller.render.item_default']

 report=load(P/'reports/a2726-seasoning-bottle-render.json')
 assert report['version']=='A2.7.26'
 assert report['placed_fix']['geometry_variants']==5
 assert report['placed_fix']['removed_spice_empty_planes']==11
 assert report['held_fix']['first_person_offset']==OFFSET
 assert report['held_fix']['third_person_offset']==OFFSET
 assert report['logic_unchanged'] is True
 assert report['minecraft_tested'] is False and report['bds_tested'] is False

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
  'version':'A2.7.26','seasoning_geometry_variants':5,'positive_shell_cubes':total_cubes,
  'held_attachables':len(ITEMS),'hand_offset':OFFSET,'removed_empty_planes':11,
  'logic_unchanged':True,'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2726-dash-verification.json' if a.compiled else 'a2726-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))
if __name__=='__main__':main()
