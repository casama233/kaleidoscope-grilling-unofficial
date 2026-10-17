from __future__ import annotations
import copy,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core'
BP=P/'behavior_pack'
RP=P/'resource_pack'
VERSION=[2,7,33]

HAND_ID='geometry.kg_a2733.seasoning_bottle_hand'
HAND_FILE=RP/'models/entity/a2733_seasoning_bottle_hand.geo.json'
RC_ID='controller.render.kg_a2733.seasoning_bottle_hand'
RC_FILE=RP/'render_controllers/a2733_seasoning_bottle_hand.render_controllers.json'
ATLAS_KEY='kg_a2733_seasoning_bottle'
ITEMS=('empty_seasoning_bottle','pending_seasoning','special_seasoning')
PLACED=(
 ('seasoning_bottle.geo.json','seasoning_bottle.json','geometry.kg_a2726.seasoning_bottle_legacy','geometry.kg_a2733.seasoning_bottle_legacy'),
 ('seasoning_bottles_1.geo.json','seasoning_bottle_1.json','geometry.kg_a2726.seasoning_bottles_1','geometry.kg_a2733.seasoning_bottles_1'),
 ('seasoning_bottles_2.geo.json','seasoning_bottle_2.json','geometry.kg_a2726.seasoning_bottles_2','geometry.kg_a2733.seasoning_bottles_2'),
 ('seasoning_bottles_3.geo.json','seasoning_bottle_3.json','geometry.kg_a2726.seasoning_bottles_3','geometry.kg_a2733.seasoning_bottles_3'),
 ('seasoning_bottles_4.geo.json','seasoning_bottle_4.json','geometry.kg_a2726.seasoning_bottles_4','geometry.kg_a2733.seasoning_bottles_4'),
)

def load(path):
 return json.loads(path.read_text(encoding='utf-8-sig'))

def write(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in (
  (bm,'Kaleidoscope Grilling A2.7.33 Seasoning Bottle Corrective BP'),
  (rm,'Kaleidoscope Grilling A2.7.33 Seasoning Bottle Corrective RP'),
 ):
  doc['header']['version']=VERSION
  doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)

 cfg=load(P/'config.json')
 cfg['name']='Kaleidoscope Grilling A2.7.33 Seasoning Bottle Corrective'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_33_Seasoning_Bottle_Corrective'
 write(P/'config.json',cfg)

def shifted_hand_geometry():
 # Start from the already-clean A2.7.26 single-bottle shell.
 src=load(RP/'models/blocks/seasoning_bottles_1.geo.json')
 geo=copy.deepcopy(src['minecraft:geometry'][0])
 if geo['description']['identifier']!='geometry.kg_a2726.seasoning_bottles_1':
  raise RuntimeError('A2.7.33 hand source geometry drift')
 geo['description']['identifier']=HAND_ID
 geo['description']['visible_bounds_width']=3
 geo['description']['visible_bounds_height']=3
 geo['description']['visible_bounds_offset']=[0,1,0]

 root=geo['bones'][0]
 if root.get('name')!='root':
  raise RuntimeError('A2.7.33 hand source root drift')
 root['binding']='q.item_slot_to_bone_name(context.item_slot)'

 # The repository's independent immersion-lab hand prototype places the
 # seasoning shell six model units below block-space. Bake that into geometry
 # rather than animating the bound root; animating the bound root was the
 # A2.7.26 mistake that could pull the model toward the player's legs.
 for bone in geo['bones'][1:]:
  if bone.get('parent')!='root':
   raise RuntimeError('A2.7.33 expected direct shell children of root')
  if 'pivot' in bone:
   bone['pivot'][1]-=6
  for cube in bone.get('cubes',[]):
   cube['origin'][1]-=6
   if 'pivot' in cube:
    cube['pivot'][1]-=6

 # Prove baked shell is exactly the same spatial convention as immersion-lab.
 proto=load(ROOT/'projects/grilling/integration/immersion_lab/resource_pack/models/entity/hand_props.geo.json')
 rows=[g for g in proto['minecraft:geometry'] if g.get('description',{}).get('identifier')=='geometry.kg_imm.hand_seasoning']
 if len(rows)!=1:raise RuntimeError('missing immersion-lab hand seasoning reference')
 ref=rows[0]
 by_suffix={}
 for b in ref['bones']:
  if b['name'].startswith('season_instance_0_'):
   by_suffix[b['name'].replace('season_instance_0_','',1)]=b
 for b in geo['bones'][1:]:
  suffix=b['name'].replace('instance_0_','',1)
  if suffix not in by_suffix:raise RuntimeError('immersion-lab hand shell missing '+suffix)
  a=b.get('cubes',[]);z=by_suffix[suffix].get('cubes',[])
  if len(a)!=len(z):raise RuntimeError('immersion-lab cube count drift '+suffix)
  for ca,cz in zip(a,z):
   if ca['origin']!=cz['origin'] or ca['size']!=cz['size']:
    raise RuntimeError('immersion-lab hand-space mismatch '+suffix)
 return {'format_version':'1.16.0','minecraft:geometry':[geo]}

def patch_hand():
 write(HAND_FILE,shifted_hand_geometry())
 write(RC_FILE,{
  'format_version':'1.8.0',
  'render_controllers':{
   RC_ID:{
    'geometry':'Geometry.default',
    'materials':[{'*':'Material.default'}],
    'textures':['Texture.default']
   }
  }
 })
 for item in ITEMS:
  path=RP/'attachables'/f'{item}.attachable.json'
  doc=load(path);desc=doc['minecraft:attachable']['description']
  if desc['identifier']!=f'kaleidoscope_grilling:{item}':
   raise RuntimeError('attachable identifier drift '+item)
  desc['geometry']={'default':HAND_ID}
  desc['textures']={'default':'textures/blocks/seasoning_bottle'}
  desc['materials']={'default':'entity_alphablend'}
  # A2.7.26 moved the bound root with a hold animation. Remove that transform
  # entirely and use the baked, independently verified hand-space shell.
  desc.pop('animations',None)
  desc.pop('scripts',None)
  desc['render_controllers']=[RC_ID]
  write(path,doc)

def positive_geometry(doc):
 geos=doc.get('minecraft:geometry',[])
 if len(geos)!=1:return False
 for bone in geos[0].get('bones',[]):
  if bone.get('binding'):return False
  for cube in bone.get('cubes',[]):
   if len(cube.get('size',[]))!=3 or any(float(v)<=0 for v in cube['size']):return False
 return True

def patch_placed():
 terrain_path=RP/'textures/terrain_texture.json'
 terrain=load(terrain_path)
 terrain.setdefault('texture_data',{})[ATLAS_KEY]={'textures':'textures/blocks/seasoning_bottle'}
 write(terrain_path,terrain)

 for geo_name,block_name,old_id,new_id in PLACED:
  gpath=RP/'models/blocks'/geo_name
  gdoc=load(gpath)
  if len(gdoc.get('minecraft:geometry',[]))!=1:
   raise RuntimeError('placed geometry count drift '+geo_name)
  geo=gdoc['minecraft:geometry'][0]
  if geo['description']['identifier']!=old_id:
   raise RuntimeError('placed geometry identifier drift '+geo_name)
  if not positive_geometry(gdoc):
   raise RuntimeError('placed shell contains invalid/non-positive/bound geometry '+geo_name)
  geo['description']['identifier']=new_id
  write(gpath,gdoc)

  bpath=BP/'blocks'/block_name
  bdoc=load(bpath);comp=bdoc['minecraft:block']['components']
  current=comp.get('minecraft:geometry')
  current_id=current.get('identifier') if isinstance(current,dict) else current
  if current_id!=old_id:
   raise RuntimeError('placed block geometry reference drift '+block_name)
  # Use the explicit current representation instead of relying on a legacy
  # shorthand string. There is intentionally no full_block fallback component.
  comp['minecraft:geometry']={'identifier':new_id}
  mat=comp['minecraft:material_instances']['*']
  mat['texture']=ATLAS_KEY
  mat['render_method']='blend'
  mat['ambient_occlusion']=0.0
  mat['face_dimming']=False
  write(bpath,bdoc)

def report():
 write(P/'reports/a2733-seasoning-bottle-corrective.json',{
  'version':'A2.7.33',
  'scope':'correct user-reported seasoning bottle held transform and harden placed geometry/material reference chain',
  'held':{
   'items':[f'kaleidoscope_grilling:{x}' for x in ITEMS],
   'geometry':HAND_ID,
   'render_controller':RC_ID,
   'bound_root_animation_removed':True,
   'hand_space_baked_from_block_shell':True,
   'verified_against':'geometry.kg_imm.hand_seasoning',
   'baked_y_offset':-6
  },
  'placed':{
   'variants':5,
   'fresh_geometry_identifier_prefix':'geometry.kg_a2733.',
   'geometry_component_representation':'explicit identifier object',
   'fresh_terrain_texture_key':ATLAS_KEY,
   'texture':'textures/blocks/seasoning_bottle',
   'no_full_block_geometry':True,
   'all_shell_cube_sizes_positive':True,
   'render_method':'blend'
  },
  'gameplay_logic_changed':False,
  'old_a2726_hold_animation_retained_unreferenced_for_historical_rebuilds':True,
  'minecraft_tested':False,
  'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,32]:
  raise RuntimeError('A2.7.33 must augment verified A2.7.32')
 patch_versions();patch_hand();patch_placed();report()
 print('A2.7.33 seasoning bottle corrective render patch complete')

if __name__=='__main__':
 main()
