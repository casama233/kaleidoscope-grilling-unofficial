"""Repair pose dispatch for every held model; normalize skewer binding chains.
Geometry binding can query a bone name, but pose selection uses equipment slots,
independent of the holder's bone spelling. Plant faces already have both normals.
"""
from pathlib import Path
from copy import deepcopy
import json, subprocess
ROOT=Path(__file__).resolve().parents[2]
BASE='36331df07a8b23ea5c2b5d859b50353bdcd4031d'
RP=ROOT/'projects/grilling/gameplay_core/resource_pack';BP=ROOT/'projects/grilling/gameplay_core/behavior_pack'
PLANTS=['pepper_leaves','pepper_leaves_fruiting_bridge','pepper_sapling','canola_crop','houttuynia_crop','onion_crop','sweet_potato_crop']
def source(p):return json.loads(subprocess.check_output(['git','show',f'{BASE}:{p.relative_to(ROOT).as_posix()}'],cwd=ROOT))
def write(p,d):
 p.parent.mkdir(exist_ok=True,parents=True)
 text=json.dumps(d,ensure_ascii=False,indent=2)+'\n'
 if p.name=='player_binding.animation.json':text=text.replace('\n','\r\n')
 p.write_bytes(text.encode())
def conditions():
 return [{name:f"c.is_first_person == {1 if name.startswith('fp') else 0} && c.item_slot == '{'main_hand' if name.endswith('right') else 'off_hand'}'"} for name in ('fp_right','fp_left','tp_right','tp_left')]
def flatten(g):
 g=deepcopy(g);cubes=[]
 for b in g['bones']:
  assert not any(b.get('rotation',[])),b['name']
  assert b.get('pivot')==[0,24,0],b['name']
  cubes.extend(deepcopy(b.get('cubes',[])))
 g['description']['identifier']=g['description']['identifier'].replace('kg_a283.','kg_a287.')
 g['bones']=[{'name':'grip','pivot':[0,24,0],'binding':'q.item_slot_to_bone_name(context.item_slot)','cubes':cubes}]
 return g

def main():
 for p in (RP/'attachables').glob('*.json'):
  d=source(p);a=d['minecraft:attachable']['description'];a['scripts']['animate']=conditions()
  if p.name.endswith('_skewer.attachable.json'):
   for key,ref in a['geometry'].items():
    old=RP/('models/entity/a283_hand/'+ref.removeprefix('geometry.kg_a283.')+'.geo.json');geo=source(old)
    geo['minecraft:geometry']=[flatten(g) for g in geo['minecraft:geometry']]
    ref=geo['minecraft:geometry'][0]['description']['identifier'];a['geometry'][key]=ref
    write(RP/('models/entity/a287_hand/'+ref.removeprefix('geometry.kg_a287.')+'.geo.json'),geo)
   a['animations']={key:'animation.kg_a287.skewer_'+key for key in a['animations']}
  write(p,d)
 d=source(RP/'animations/a2764_skewer_java_display.animation.json');animations={}
 for key,a in d['animations'].items():
  a['bones']={'grip':a['bones']['display']};animations['animation.kg_a287.skewer_'+key.split('skewer_')[1]]=a
 write(RP/'animations/a287_skewer_held.animation.json',{'format_version':'1.8.0','animations':animations})
 for name in PLANTS:
  p=BP/f'blocks/{name}.json';d=source(p);b=d['minecraft:block']
  for c in [b['components']]+[x['components'] for x in b.get('permutations',[])]:
   for mat in c.get('minecraft:material_instances',{}).values():
    if isinstance(mat,dict) and mat.get('render_method')=='alpha_test':mat['render_method']='alpha_test_single_sided'
  write(p,d)
 # Camera-space translation belongs exclusively to first-person rendering.
 # Keep authored first-person paths; third-person arms rotate about their real joints.
 p=RP/'animations/player_binding.animation.json';d=source(p)
 for key,a in d['animations'].items():
  if not any(key.startswith('animation.kg_imm.player.'+kind+'.') for kind in ('reach','brush','season')):continue
  for name,bone in a.get('bones',{}).items():
   if name.lower() not in ('rightarm','leftarm'):continue
   pos=bone.get('position')
   if not pos:continue
   def camera_only(v):
    if isinstance(v,str) and 'variable.is_first_person ?' in v:
     return v.split(' : ')[0]+' : 0.0'
    return f'variable.is_first_person ? {v} : 0.0' if v else 0
   if isinstance(pos,dict):bone['position']={t:[camera_only(v) for v in values] for t,values in pos.items()}
   else:bone['position']=[camera_only(v) for v in pos]
 write(p,d)
if __name__=='__main__':main()
