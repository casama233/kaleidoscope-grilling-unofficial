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
def dump(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
def build():
 client=deepcopy(json.loads((RP/'entity/grill_food_visual.entity.json').read_text()))
 d=client['minecraft:client_entity']['description'];d['identifier']=NS+'plate_food_visual'
 # Secret decode expressions and geometry/controller references are shared.
 # Plate rendering has no cooking flip clock, hop, equipment or attachables.
 d['scripts'].pop('initialize',None)
 d['scripts']['pre_animation']=[s for s in d['scripts']['pre_animation'] if s.startswith('v.kg_secret_')]
 d['scripts']['animate']=['pose'];d['animations']={'pose':'animation.kg_station.plate_food'}
 server=deepcopy(json.loads((BP/'entities/grill_food_visual.json').read_text()))
 d=server['minecraft:entity']['description'];d['identifier']=NS+'plate_food_visual'
 for name in ('flips','hop'):d['properties'].pop(NS+name)
 # A visual helper must preserve arbitrary authored slot yaw from its facing.
 # Keep body/head aligned without cardinal quantization or a polling loop.
 # Official component minimum is1.21.90; this entity format is1.26.0.
 server['minecraft:entity']['components']['minecraft:body_rotation_always_follows_head']={}
 return {
 RP/'entity/plate_food_visual.entity.json':dump(client),
 BP/'entities/plate_food_visual.json':dump(server),
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
