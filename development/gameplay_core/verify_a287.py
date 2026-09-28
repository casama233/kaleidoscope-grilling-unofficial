"""All held binding paths and pose dispatch. Does not simulate a Minecraft client."""
from pathlib import Path
import ast,json,re
import a287_binding_repair as repair
from verify_a285 import survival_gate
from verify_a284 import eating_gate
from verify_a283 import main as previous_gate
RP=repair.RP;BP=repair.BP
def load(p):return json.loads(p.read_text())
def expression(expr,first,slot,bone):
 # Only the simple boolean Molang subset used by held pose dispatch is accepted.
 expr=expr.replace('q.item_slot_to_bone_name(context.item_slot)',repr(bone))
 for prefix in ('context','c'):
  expr=expr.replace(prefix+'.is_first_person',str(int(first))).replace(prefix+'.item_slot',repr(slot))
 expr=expr.replace('&&',' and ').replace('||',' or ')
 tree=ast.parse(expr,mode='eval')
 assert all(isinstance(n,(ast.Expression,ast.BoolOp,ast.And,ast.Or,ast.Compare,ast.Eq,ast.NotEq,ast.Constant,ast.Load)) for n in ast.walk(tree)),expr
 return bool(eval(compile(tree,'<pose-condition>','eval'),{'__builtins__':{}},{}))
def binding_assets():
 idx={};animations={};rows=[];refs=set();cases=0
 for p in (RP/'models').rglob('*.geo.json'):
  for g in load(p)['minecraft:geometry']:
   ref=g['description']['identifier'];assert ref not in idx,ref;idx[ref]=g
 for p in (RP/'animations').glob('*.json'):
  for key,a in load(p).get('animations',{}).items():assert key not in animations,key;animations[key]=a
 for p in sorted((RP/'attachables').glob('*.json')):
  d=load(p)['minecraft:attachable']['description'];selected=[]
  for first in (0,1):
   for slot,hand in [('main_hand','right'),('off_hand','left')]:
    for bone in (hand+'item',hand+'Item','custom_'+hand+'_grip'):
     matches=[key for row in d['scripts']['animate'] for key,expr in row.items() if expression(expr,first,slot,bone)]
     expected=('fp_' if first else 'tp_')+hand
     assert matches==[expected],(p,first,slot,bone,matches)
     cases+=1
    selected.append(expected)
  for ref in d['geometry'].values():
   refs.add(ref);g=idx[ref];assert len(g['bones'])==1,ref
   b=g['bones'][0];assert b['name']=='grip' and b['pivot']==[0,24,0]
   assert b['binding']=='q.item_slot_to_bone_name(context.item_slot)' and 'parent' not in b
   assert b.get('cubes')
   for anim in d['animations'].values():assert set(animations[anim]['bones'])=={'grip'},anim
   # Flattening must retain every source cube, including its UV and local rotation.
   if ref.startswith('geometry.kg_a287.'):
    oldref=ref.replace('kg_a287.','kg_a283.');old=idx[oldref]
    assert b['cubes']==[c for bone in old['bones'] for c in bone.get('cubes',[])],ref
  if p.name.endswith('_skewer.attachable.json'):
   old=repair.source(p);old=old['minecraft:attachable']['description']
   assert d['scripts']['pre_animation']==old['scripts']['pre_animation']
   assert d['render_controllers']==old['render_controllers'] and d['textures']==old['textures']
   assert set(d['geometry'])==set(old['geometry'])
  rows.append({'item':d['identifier'],'geometries':list(d['geometry'].values()),'poses':selected,'bound_bone':'grip'})
 assert len(rows)==107 and cases==1284,(len(rows),cases)
 # Regression reproduction: old dispatch can select zero poses for a normalized bone name.
 old=repair.source(RP/'attachables/empty_seasoning_bottle.attachable.json')['minecraft:attachable']['description']
 assert not any(expression(expr,0,'main_hand','rightitem') for row in old['scripts']['animate'] for expr in row.values())
 # World entities and native block items must never inherit a player hand binding.
 entities=0;native=0
 for p in (RP/'entity').glob('*.json'):
  d=load(p).get('minecraft:client_entity',{}).get('description',{})
  for ref in d.get('geometry',{}).values():
   if ref in idx:assert not any('binding' in b for b in idx[ref]['bones']),(p,ref)
  entities+=1
 for p in (BP/'blocks').glob('*.json'):
  c=load(p)['minecraft:block']['components'];v=c.get('minecraft:item_visual')
  if v:
   ref=v['geometry'];ref=ref.get('identifier') if isinstance(ref,dict) else ref
   assert not any('binding' in b for b in idx[ref]['bones']),ref;native+=1
 assert native==3
 return idx,refs,{'attachables':len(rows),'pose_cases':cases,'native_item_visuals':native,'client_entities':entities,'items':rows}
def plant_gate():
 count=0;plant_refs=set()
 idx={g['description']['identifier']:g for p in (RP/'models').rglob('*.geo.json') for g in load(p)['minecraft:geometry']}
 for name in repair.PLANTS:
  b=load(BP/f'blocks/{name}.json')['minecraft:block'];before=repair.source(BP/f'blocks/{name}.json')['minecraft:block']
  for c in [b['components']]+[p['components'] for p in b.get('permutations',[])]:
   ref=c.get('minecraft:geometry');ref=ref.get('identifier') if isinstance(ref,dict) else ref
   if ref:plant_refs.add(ref)
   for m in c.get('minecraft:material_instances',{}).values():
    if isinstance(m,dict):assert m['render_method']=='alpha_test_single_sided';count+=1
  # Gameplay state, collision and component logic are not part of the material fix.
  def strip(value):
   if isinstance(value,dict):return {k:strip(v) for k,v in value.items() if k!='render_method'}
   if isinstance(value,list):return [strip(v) for v in value]
   return value
  assert strip(b)==strip(before),name
 for ref in plant_refs:
  for bone in idx[ref]['bones']:
   for cube in bone.get('cubes',[]):
    if isinstance(cube['uv'],list):continue  # Box UV emits all six directions.
    for axis,size in enumerate(cube['size']):
     if size==0:assert all(face in cube['uv'] for face in [('east','west'),('up','down'),('north','south')][axis]),ref
 # Third-person interaction gestures must not translate arms out of their joints.
 animations=load(RP/'animations/player_binding.animation.json')['animations']
 for key,a in animations.items():
  if not any(key.startswith('animation.kg_imm.player.'+kind+'.') for kind in ('reach','brush','season')):continue
  for b in a['bones'].values():
   p=b.get('position',[]);vectors=p.values() if isinstance(p,dict) else [p]
   for vector in vectors:
    assert all(v==0 or isinstance(v,str) and v.endswith(' : 0.0') for v in vector),key
 print('A287 single-sided plant material instances:',count)
if __name__=='__main__':
 plant_gate();eating_gate();survival_gate();previous_gate()
