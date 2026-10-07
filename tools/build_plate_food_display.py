"""Plate-only render bindings; reuse canonical source meshes and food palettes.

This authoring tool changes canonical assets, never package/deployment bytes.
It does not infer a native armor-stand equipped-item matrix.
"""
from copy import deepcopy
from pathlib import Path
import argparse,json
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT/'projects/grilling/gameplay_core'
BP,RP=PROJECT/'behavior_pack',PROJECT/'resource_pack'
NS='kaleidoscope_grilling:'
ORDINARY_MODEL=115
ORDINARY_GEOMETRY='geometry.kg_station.plate.ordinary_skewer'
PLATE_CONTROLLER='controller.render.kg_station.plate_food'
def dump(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
def ordinary_world_geometry():
 # Preserve the canonical full19-cube shell/UVs. This is the same binding,
 # display-parent removal and one-pixel Y normalization as build_grill_display.
 geo=deepcopy(json.loads((RP/'models/entity/a22_bites/ordinary_skewer_stage0.geo.json').read_text())['minecraft:geometry'][0])
 assert sum(len(b.get('cubes',[]))for b in geo['bones'])==19,'Ordinary full model drift'
 geo['description'].update(identifier=ORDINARY_GEOMETRY,visible_bounds_width=2,visible_bounds_height=2,visible_bounds_offset=[0,.3,0])
 bones=[]
 for bone in geo['bones']:
  if bone['name']=='display':continue
  bone.pop('binding',None)
  if bone['name']!='root':
   if bone.get('parent')=='display':bone['parent']='root'
   if 'pivot'in bone:bone['pivot'][1]-=1
   for cube in bone.get('cubes',[]):
    cube['origin'][1]-=1
    if 'pivot'in cube:cube['pivot'][1]-=1
  bones.append(bone)
 geo['bones']=bones
 return geo
def build():
 client=deepcopy(json.loads((RP/'entity/grill_food_visual.entity.json').read_text()))
 d=client['minecraft:client_entity']['description'];d['identifier']=NS+'plate_food_visual'
 # Secret decode expressions and geometry/controller references are shared.
 # Plate rendering has no cooking flip clock, hop, equipment or attachables.
 d['scripts'].pop('initialize',None)
 d['scripts']['pre_animation']=[s for s in d['scripts']['pre_animation'] if s.startswith('v.kg_secret_')]
 d['scripts']['animate']=['pose'];d['animations']={'pose':'animation.kg_station.plate_food'}
 d['geometry']['s115']=ORDINARY_GEOMETRY
 d['textures']['s115']='textures/a22_bites/ordinary_skewer_stage0'
 # The plate's extra model must never expand the grill's model arrays/range.
 base=d['render_controllers'][0]
 assert set(base)=={'controller.render.kg_station.grill'}
 d['render_controllers'][0]={PLATE_CONTROLLER:base['controller.render.kg_station.grill']}
 controllers=json.loads((RP/'render_controllers/grill_food_visual.render_controllers.json').read_text())
 controller=deepcopy(controllers['render_controllers']['controller.render.kg_station.grill'])
 assert len(controller['arrays']['geometries']['Array.models'])==ORDINARY_MODEL
 assert len(controller['arrays']['textures']['Array.stages'])==ORDINARY_MODEL
 controller['arrays']['geometries']['Array.models'].append('Geometry.s115')
 controller['arrays']['textures']['Array.stages'].append('Texture.s115')
 server=deepcopy(json.loads((BP/'entities/grill_food_visual.json').read_text()))
 d=server['minecraft:entity']['description'];d['identifier']=NS+'plate_food_visual'
 for name in ('flips','hop'):d['properties'].pop(NS+name)
 d['properties'][NS+'model']['range']=[0,ORDINARY_MODEL]
 # A visual helper must preserve arbitrary authored slot yaw from its facing.
 # Keep body/head aligned without cardinal quantization or a polling loop.
 # Official component minimum is1.21.90; this entity format is1.26.0.
 server['minecraft:entity']['components']['minecraft:body_rotation_always_follows_head']={}
 return {
 RP/'entity/plate_food_visual.entity.json':dump(client),
 BP/'entities/plate_food_visual.json':dump(server),
 RP/'models/entity/plate_food_display.geo.json':dump({'format_version':'1.16.0','minecraft:geometry':[ordinary_world_geometry()]}),
 RP/'render_controllers/plate_food_visual.render_controllers.json':dump({'format_version':'1.8.0','render_controllers':{PLATE_CONTROLLER:controller}}),
 # Existing world meshes already lie horizontally. The author plate's .8
 # renderer scale times its 1.5 FIXED model scale gives 1.2. Source FIXED
 # translation/centering requires post-scale [0,-1.8,+1.8] pixels; fixed
 # world meshes already lowered authored Y one pixel, so add1.2 back.
 RP/'animations/plate_food_visual.animation.json':dump({'format_version':'1.8.0','animations':{
  'animation.kg_station.plate_food':{'loop':True,'bones':{'root':{'scale':1.2,'position':[0,"q.property('kaleidoscope_grilling:model') == 114 ? -1.8 : -0.6",1.8]}}}}})
 }
def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
 for path,data in build().items():
  if a.check:assert path.read_bytes()==data,'Plate render bindings drift: '+str(path.relative_to(ROOT))
  else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
 print('Plate full-skewer bindings '+('check'if a.check else 'build')+' PASS; native/client acceptance separate')
if __name__=='__main__':main()
