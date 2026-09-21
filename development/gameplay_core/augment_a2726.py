from __future__ import annotations
import copy,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
VERSION=[2,7,26]
HOLD_OFFSET=[0,-6,0]
HAND_GEO='geometry.kg_a2726.seasoning_bottle_hand'
HAND_GEO_FILE='models/entity/a2726_seasoning_bottle_hand.geo.json'
ANIM_FILE='animations/a2726_seasoning_bottle_hold.animation.json'
FIRST='animation.kaleidoscope_grilling.a2726.seasoning_bottle_hold_first_person'
THIRD='animation.kaleidoscope_grilling.a2726.seasoning_bottle_hold_third_person'
ITEMS=('empty_seasoning_bottle','pending_seasoning','special_seasoning')
VARIANTS=(
 ('seasoning_bottle.geo.json','seasoning_bottle.json','geometry.kg_a21.seasoning_bottle','geometry.kg_a2726.seasoning_bottle_legacy',1),
 ('seasoning_bottles_1.geo.json','seasoning_bottle_1.json','geometry.kg_a22.seasoning_bottles_1','geometry.kg_a2726.seasoning_bottles_1',1),
 ('seasoning_bottles_2.geo.json','seasoning_bottle_2.json','geometry.kg_a22.seasoning_bottles_2','geometry.kg_a2726.seasoning_bottles_2',2),
 ('seasoning_bottles_3.geo.json','seasoning_bottle_3.json','geometry.kg_a22.seasoning_bottles_3','geometry.kg_a2726.seasoning_bottles_3',3),
 ('seasoning_bottles_4.geo.json','seasoning_bottle_4.json','geometry.kg_a22.seasoning_bottles_4','geometry.kg_a2726.seasoning_bottles_4',4),
)

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.26 Seasoning Bottle Render BP'),(rm,'Kaleidoscope Grilling A2.7.26 Seasoning Bottle Render RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json')
 cfg['name']='Kaleidoscope Grilling A2.7.26 Seasoning Bottle Render'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_26_Seasoning_Bottle_Render'
 write(P/'config.json',cfg)

def positive_cubes(geo):
 for bone in geo.get('bones',[]):
  for cube in bone.get('cubes',[]):
   if any(float(x)<=0 for x in cube.get('size',[])):return False
 return True

def patch_block_geometries():
 removed_total=0
 fixed_one=None
 for geo_name,block_name,old_id,new_id,bottles in VARIANTS:
  path=RP/'models/blocks'/geo_name
  doc=load(path);geos=doc['minecraft:geometry']
  if len(geos)!=1:raise RuntimeError(f'{geo_name}: expected one geometry')
  geo=geos[0]
  if geo['description']['identifier']!=old_id:
   raise RuntimeError(f'{geo_name}: unexpected baseline geometry id {geo["description"]["identifier"]}')
  removed=[b for b in geo['bones'] if 'spice_empty' in b.get('name','')]
  if len(removed)!=bottles:
   raise RuntimeError(f'{geo_name}: expected {bottles} spice_empty planes, got {len(removed)}')
  for bone in removed:
   cubes=bone.get('cubes',[])
   if len(cubes)!=1 or cubes[0].get('size',[None,None,None])[1]!=0:
    raise RuntimeError(f'{geo_name}: spice_empty source is not the expected horizontal zero-height plane')
  geo['bones']=[b for b in geo['bones'] if 'spice_empty' not in b.get('name','')]
  geo['description']['identifier']=new_id
  if not positive_cubes(geo):raise RuntimeError(f'{geo_name}: non-positive cube remains after empty-plane cleanup')
  write(path,doc);removed_total+=len(removed)
  if geo_name=='seasoning_bottles_1.geo.json':fixed_one=copy.deepcopy(doc)

  block_path=BP/'blocks'/block_name
  block=load(block_path);components=block['minecraft:block']['components']
  if components.get('minecraft:geometry')!=old_id:
   raise RuntimeError(f'{block_name}: unexpected baseline geometry reference')
  components['minecraft:geometry']=new_id
  mat=components['minecraft:material_instances']['*']
  mat['ambient_occlusion']=0.0
  mat['face_dimming']=False
  write(block_path,block)
 if fixed_one is None:raise RuntimeError('missing fixed one-bottle geometry')
 return removed_total,fixed_one

def animation_doc():
 hold={'loop':True,'bones':{'root':{'position':HOLD_OFFSET}}}
 return {'format_version':'1.8.0','animations':{FIRST:hold,THIRD:hold}}

def attachable_doc(identifier):
 return {
  'format_version':'1.26.0',
  'minecraft:attachable':{'description':{
   'identifier':f'kaleidoscope_grilling:{identifier}',
   'materials':{'default':'entity_alphablend'},
   'textures':{'default':'textures/blocks/seasoning_bottle'},
   'geometry':{'default':HAND_GEO},
   'animations':{'hold_first_person':FIRST,'hold_third_person':THIRD},
   'scripts':{'animate':[
    {'hold_first_person':'context.is_first_person == 1.0'},
    {'hold_third_person':'context.is_first_person == 0.0'},
   ]},
   'render_controllers':['controller.render.item_default'],
  }}
 }

def add_hand_render(fixed_one):
 hand=copy.deepcopy(fixed_one)
 geo=hand['minecraft:geometry'][0]
 geo['description']['identifier']=HAND_GEO
 root=geo['bones'][0]
 if root.get('name')!='root':raise RuntimeError('one-bottle geometry root bone changed')
 root['binding']='q.item_slot_to_bone_name(context.item_slot)'
 write(RP/HAND_GEO_FILE,hand)
 write(RP/ANIM_FILE,animation_doc())
 for item in ITEMS:write(RP/'attachables'/f'{item}.attachable.json',attachable_doc(item))

def report(removed_total):
 write(P/'reports/a2726-seasoning-bottle-render.json',{
  'version':'A2.7.26',
  'scope':'seasoning bottle held and placed render hotfix',
  'observed_from_user_runtime':{
   'held':'seasoning bottle/shaker item rendered edge-on as a thin 2D hand-equipped icon',
   'placed':'one-bottle placement rendered as a full textured cube instead of the authored bottle shape',
  },
  'held_fix':{
   'attachable_items':[f'kaleidoscope_grilling:{x}' for x in ITEMS],
   'shared_geometry':HAND_GEO_FILE,
   'shared_animation':ANIM_FILE,
   'root_binding':'q.item_slot_to_bone_name(context.item_slot)',
   'first_person_offset':HOLD_OFFSET,
   'third_person_offset':HOLD_OFFSET,
   'offset_provenance':'integration immersion-lab seasoning hand geometry differs from the converted one-bottle block shell by exactly [0,-6,0]',
  },
  'placed_fix':{
   'geometry_variants':5,
   'new_identifier_prefix':'geometry.kg_a2726.seasoning_bottle',
   'removed_spice_empty_planes':removed_total,
   'reason':'the Java empty-content placeholder is a zero-height plane authored with six faces; the gameplay conversion preserved it as a zero-size cube. The hotfix removes that non-visible placeholder from empty bottle shells and forces fresh geometry identifiers so the runtime cannot keep using the previous converted resource.',
   'java_ambient_occlusion':False,
   'bedrock_ambient_occlusion':0.0,
   'face_dimming':False,
  },
  'logic_unchanged':True,
  'known_visual_gap':'pending/special seasoning now use the correct bottle shell while held, but Java remaining/variant-dependent fill appearance is still a later dynamic-render parity task.',
  'minecraft_tested':False,'bds_tested':False,
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,25]:
  raise RuntimeError('A2.7.26 must augment verified A2.7.25')
 patch_versions()
 removed,fixed_one=patch_block_geometries()
 add_hand_render(fixed_one)
 report(removed)
 print(f'A2.7.26 seasoning bottle render hotfix complete; removed {removed} empty planes')
if __name__=='__main__':main()
