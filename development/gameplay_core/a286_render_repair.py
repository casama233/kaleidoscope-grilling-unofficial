"""Reproducible mesh repairs from the deployed A285 source; no raster regeneration.
A285 video evidence: near-coplanar grate/rim, vat underside spanning the cavity,
canonical seasoning bound to an empty mesh, and child-bone held offsets.
"""
from copy import deepcopy
import json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RP=ROOT/'projects/grilling/gameplay_core/resource_pack'
BASE='a01c8b76ff11a18bccf901e6a47482b814ddec18'
def source(path):
 return json.loads(subprocess.check_output(['git','show',f'{BASE}:{path.relative_to(ROOT).as_posix()}'],cwd=ROOT))
def write(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 text=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
 if path.name in {'grill_flat.geo.json','grill_flat_lit.geo.json','grill_legged.geo.json','grill_legged_lit.geo.json'}:text=text.replace('\n','\r\n')
 path.write_bytes(text.encode())
def crop_horizontal(c,face,x0,x1,z0,z1):
 """Crop a horizontal face, preserving its signed Bedrock UV mapping."""
 n=deepcopy(c); u=n['uv'][face]; ox,_,oz=c['origin']; sx,_,sz=c['size']
 z_fraction=(oz+sz-z1)/sz if face=='up' else (z0-oz)/sz
 u['uv']=[u['uv'][0]+u['uv_size'][0]*(x0-ox)/sx,u['uv'][1]+u['uv_size'][1]*z_fraction]
 u['uv_size']=[u['uv_size'][0]*(x1-x0)/sx,u['uv_size'][1]*(z1-z0)/sz]
 n['origin']=[x0,c['origin'][1]+(c['size'][1] if face=='up' else 0),z0]
 n['size']=[x1-x0,0,z1-z0];n['uv']={face:u}
 return n
def ring(c,face,hx,hz):
 x0,_,z0=c['origin'];x1=x0+c['size'][0];z1=z0+c['size'][2]
 return [crop_horizontal(c,face,*r) for r in [(x0,x1,z0,-hz),(x0,x1,hz,z1),(x0,-hx,-hz,hz),(hx,x1,-hz,hz)]]
def world_mesh(g,kind):
 g=deepcopy(g)
 for b in g['bones']:
  if kind=='grill':
   if b['name']=='instance_0_element_0_0':
    c=b['cubes'][0];parts=ring(c,'up',7,5);del c['uv']['up'];b['cubes']+=parts
   if 'inward_down' in b['name']:b['cubes']=[]  # No ceiling across the firebox.
   if b['name']=='instance_0_element_7_7':
    c=b['cubes'][0]
    # Keep the original mesh height; trim overlap with the solid rim instead of nudging it.
    b['cubes']=[crop_horizontal(c,f,-7,7,-5,5) for f in ('up','down')]
  elif kind=='vat' and b['name']=='instance_0_element_0_0':
   c=b['cubes'][0];parts=ring(c,'down',6,6);del c['uv']['down'];b['cubes']+=parts
 return g
def held_mesh(g,rack=False):
 g=deepcopy(g);g['description']['identifier']=g['description']['identifier'].replace('kg_a283.','kg_a286.')
 cubes=[]
 for b in g['bones']:
  assert not any(b.get('rotation',[])),b['name']
  cubes.extend(deepcopy(b.get('cubes',[])))
 # Rack was world-space (Y=29..38, Z=2.75..8) beneath an extra display bone.
 # Centre it on the binding anchor. Bottle was already centred near Y=24.
 offset=[0,-9.5,-5.375] if rack else [0,0,0]
 for c in cubes:
  for k in ('origin','pivot'):
   if k in c:c[k]=[round(v+offset[i],8) for i,v in enumerate(c[k])]
 g['bones']=[{'name':'grip','pivot':[0,24,0],'binding':'q.item_slot_to_bone_name(context.item_slot)','cubes':cubes}]
 return g

def main():
 for name in ['grill_flat','grill_flat_lit','grill_legged','grill_legged_lit','a283_item_grill']+[f'big_vat_{i}' for i in range(5)]:
  p=RP/f'models/blocks/{name}.geo.json';d=source(p);d['minecraft:geometry']=[world_mesh(g,'vat' if name.startswith('big_vat') else 'grill') for g in d['minecraft:geometry']];write(p,d)
 # Use depth-writing, one-sided cutout for opaque wood/oil/lava. Water keeps blending.
 bp=ROOT/'projects/grilling/gameplay_core/behavior_pack/blocks/big_vat.json'
 block=source(bp);definition=block['minecraft:block']
 for comp in [definition['components']]+[p['components'] for p in definition['permutations'] if "== 'water'" not in p['condition']]:
  for mat in comp.get('minecraft:material_instances',{}).values():mat['render_method']='alpha_test_single_sided'
 write(bp,block)
 # Leave the skewer bite skeletons and their existing native eating path intact.
 for p in (RP/'attachables').glob('*.json'):
  d=source(p);a=d['minecraft:attachable']['description'];name=p.name.split('.')[0]
  if 'seasoning' not in name and name!='advanced_rack':continue
  ref=a['geometry']['default']
  if name=='special_seasoning':ref='geometry.kg_a283.kg_a2766.special_seasoning.r8.v0'
  if name=='pending_seasoning':ref='geometry.kg_a283.kg_a2766.special_seasoning.r4.v0'
  old=RP/('models/entity/a283_hand/'+ref.removeprefix('geometry.kg_a283.')+'.geo.json')
  geo=source(old);geo['minecraft:geometry']=[held_mesh(g,name=='advanced_rack') for g in geo['minecraft:geometry']]
  newref=geo['minecraft:geometry'][0]['description']['identifier'];write(RP/('models/entity/a286_hand/'+newref.removeprefix('geometry.kg_a286.')+'.geo.json'),geo)
  a['geometry']['default']=newref
  if name!='advanced_rack':
   g=geo['minecraft:geometry'][0];cubes=g['bones'][0]['cubes']
   contents=[c for c in cubes if c['origin'][0]==-2.5 and c['size'][0]==5]
   if contents:
    # Opaque spice is drawn before the translucent glass, in its own render pass.
    inner=deepcopy(geo);inner_g=inner['minecraft:geometry'][0]
    inner_g['description']['identifier']=newref+'.contents';inner_g['bones'][0]['cubes']=contents
    g['bones'][0]['cubes']=[c for c in cubes if c not in contents]
    write(RP/('models/entity/a286_hand/'+newref.removeprefix('geometry.kg_a286.')+'.geo.json'),geo)
    write(RP/('models/entity/a286_hand/'+newref.removeprefix('geometry.kg_a286.')+'.contents.geo.json'),inner)
    a['geometry']['contents']=newref+'.contents';a['materials']['contents']='entity_alphatest_one_sided'
    a['render_controllers']=['controller.render.kg_a286.contents','controller.render.kg_a2733.seasoning_bottle_hand']
  family='rack' if name=='advanced_rack' else 'bottle'
  a['animations']={k:f'animation.kg_a286.{family}_{k}' for k in ['fp_right','fp_left','tp_right','tp_left']}
  write(p,d)
 write(RP/'render_controllers/a286_bottle.render_controllers.json',{'format_version':'1.8.0','render_controllers':{'controller.render.kg_a286.contents':{'geometry':'Geometry.contents','materials':[{'*':'Material.contents'}],'textures':['Texture.default']}}})
 animations={}
 for family in ('bottle','rack'):
  for context in ('fp','tp'):
   for hand in ('right','left'):
    if family=='bottle':rot=[27,-39,-159] if context=='fp' else [90,0,0];scale=.625 if context=='fp' else .5
    else:rot=[0,57,0] if context=='fp' else [75,45,0];scale=.4 if context=='fp' else .375
    if hand=='left':rot=[rot[0],-rot[1],-rot[2]]
    animations[f'animation.kg_a286.{family}_{context}_{hand}']={'loop':True,'bones':{'grip':{'position':[0,0,0] if context=='fp' else [0,-1.5,-1],'rotation':rot,'scale':scale}}}
 write(RP/'animations/a286_held.animation.json',{'format_version':'1.8.0','animations':animations})
if __name__=='__main__':main()
