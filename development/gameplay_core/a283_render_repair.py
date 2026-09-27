"""Reproducible A2.8.3 render repair; canonical A2.8.1 inputs remain in Git.

Bound entity models use Bedrock's y=24 item origin (see Mojang trident.geo.json).
World meshes keep their coordinates. Opposite-facing inner/outer surfaces are
preserved and use backface culling; only identical oriented faces are removed.
"""
from copy import deepcopy
from pathlib import Path
import argparse, collections, hashlib, json, subprocess
from PIL import Image, ImageDraw
import a281_bottle_icons as sprites

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core'; BP=P/'behavior_pack'; RP=P/'resource_pack'
BASE='10de23706bed7392884d3c693423c57b87eb59e3'
AXES={'west':(0,0),'east':(0,1),'down':(1,0),'up':(1,1),'north':(2,0),'south':(2,1)}
STATIONS=('advanced_rack_block','grill','grill_legs','oil_press','big_vat','skewer_plate_block','skewer_recipe')

def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def original(p):
 return json.loads(subprocess.check_output(['git','show',BASE+':'+p.relative_to(ROOT).as_posix()],cwd=ROOT))

def deduplicate(geo):
 """Exact same facing, plane, rectangle and transform only; no epsilon welding.

 Prefer positive-volume geometry over redundant conversion planes. UVs on
 surviving faces are unchanged. Separate materials are never merged.
 """
 bones={b['name']:b for b in geo['bones']}; seen={}; removed=[]
 def transform(b):
  chain=[]
  while b:
   # An unrotated pivot has no effect on world coordinates.
   if any(b.get('rotation',[0,0,0])):chain.append((b.get('pivot'),b['rotation']))
   b=bones.get(b.get('parent'))
  return json.dumps(chain,sort_keys=True)
 candidates=[]
 for bi,b in enumerate(geo['bones']):
  for ci,c in enumerate(b.get('cubes',[])):
   if not isinstance(c.get('uv'),dict):continue
   candidates.append((int(min(c['size'])==0),bi,ci,b,c))
 for _,bi,ci,b,c in sorted(candidates,key=lambda x:x[:3]):
  for face,uv in list(c['uv'].items()):
   axis,end=AXES[face];others=[i for i in range(3) if i!=axis]
   if any(abs(c['size'][i])<1e-8 for i in others):continue
   key=(face,round(c['origin'][axis]+end*c['size'][axis],6),
        tuple((round(c['origin'][i],6),round(c['size'][i],6)) for i in others),
        transform(b),json.dumps([c.get('rotation'),c.get('pivot'),c.get('inflate',0)]),uv.get('material_instance'))
   if key in seen:
    removed.append({'bone':b['name'],'face':face,'kept':seen[key]});del c['uv'][face]
   else:seen[key]=b['name']
 for b in geo['bones']:
  if 'cubes' in b:b['cubes']=[c for c in b['cubes'] if c.get('uv')]
 return removed

def shifted(geo):
 out=deepcopy(geo)
 out['description']['identifier']='geometry.kg_a283.'+geo['description']['identifier'].removeprefix('geometry.')
 out['description']['visible_bounds_offset']=[0,1.5,0]
 out['description']['visible_bounds_height']=4
 for b in out['bones']:
  if 'pivot' in b:b['pivot'][1]+=24
  for c in b.get('cubes',[]):
   c['origin'][1]+=24
   if 'pivot' in c:c['pivot'][1]+=24
 return out

def rack_icon():
 # Java supplies a real generated-item sprite for the rack. Do not substitute
 # the block UV sheet, or invent a different inventory view.
 return Image.open(ROOT/'development/gameplay_core/fixtures/a283/advanced_rack.png').convert('RGBA')

def plate_icon():
 # The old icon was the plate's unwrapped block texture. Bake its mesh instead.
 geo=load(RP/'models/blocks/skewer_plate.geo.json')['minecraft:geometry'][0]
 texture=Image.open(RP/'textures/blocks/skewer_plate.png').convert('RGBA')
 faces=[]
 for bone in geo['bones']:
  for c in bone.get('cubes',[]):
   a=c['origin'];b=[a[i]+c['size'][i] for i in range(3)]
   for side,uv in c['uv'].items():
    pts=[sprites.rotate([p[0],p[1]-1,p[2]],[30,225,0]) for p in sprites.vertices(a,b,side)]
    u,v=uv['uv'];U,V=[uv['uv'][i]+uv['uv_size'][i] for i in range(2)]
    faces.append((pts,[(u,v),(U,v),(U,V),(u,V)],texture))
 return sprites.render(faces)

def build():
 index={}
 for p in (RP/'models').rglob('*.geo.json'):
  if 'a283_hand' in p.parts:continue
  for g in load(p)['minecraft:geometry']:index[g['description']['identifier']]=(p,g)
 stats={'hand_geometries':0,'attachables':0,'removed_faces':{},'block_materials':0}
 for p in (RP/'models/blocks').glob('*.geo.json'):
  if p.name.startswith('a283_'):continue
  d=original(p);removed=[]
  for g in d['minecraft:geometry']:
   removed+=deduplicate(g)
   # Tank fluid is a surface, not a box coincident with the four inside walls.
   for b in g['bones']:
    if b['name']=='fluid_surface':
     for c in b.get('cubes',[]):
      for face in list(c['uv']):
       if face!='up':removed.append({'bone':b['name'],'face':face,'kept':'fluid top only'});del c['uv'][face]
  if removed:write(p,d);stats['removed_faces'][p.name]=removed
 # Rebuild all active attachables from the pinned input, including all bite/fill states.
 refs={}
 for p in sorted((RP/'attachables').glob('*.json')):
  d=original(p);desc=d['minecraft:attachable']['description']
  for alias,ref in desc['geometry'].items():
   if ref not in refs:
    source,g=index[ref];g=deepcopy(g);deduplicate(g);g=shifted(g)
    refs[ref]=g['description']['identifier']
    write(RP/'models/entity/a283_hand'/(ref.removeprefix('geometry.')+'.geo.json'),{'format_version':'1.16.0','minecraft:geometry':[g]})
   desc['geometry'][alias]=refs[ref]
  if desc['identifier'].endswith('_skewer') or desc['identifier'].endswith(':advanced_rack'):
   desc['materials']['default']='entity_alphatest_one_sided'
  if desc['identifier'].endswith(':advanced_rack'):
   desc['animations']['fp_left']='animation.kaleidoscope_grilling.a283.advanced_rack_fp_left'
   desc['scripts']['animate'].append({'fp_left':"context.is_first_person == 1.0 && q.item_slot_to_bone_name(context.item_slot) == 'leftItem'"})
  write(p,d);stats['attachables']+=1
 stats['hand_geometries']=len(refs)
 write(RP/'animations/a283_rack_left.animation.json',{'format_version':'1.8.0','animations':{
  'animation.kaleidoscope_grilling.a283.advanced_rack_fp_left':{'loop':True,'bones':{'display':{'rotation':[0,-57,0],'scale':[.4]*3}}}}})
 for name in STATIONS:
  p=BP/'blocks'/(name+'.json')
  if not p.exists():continue
  d=load(p);block=d['minecraft:block']
  def materials(comp):
   for m in comp.get('minecraft:material_instances',{}).values():
    if isinstance(m,dict) and m.get('render_method') in ('alpha_test','alpha_test_single_sided'):m['render_method']='alpha_test_single_sided';stats['block_materials']+=1
    if isinstance(m,dict) and isinstance(m.get('ambient_occlusion'),bool):m['ambient_occlusion']=int(m['ambient_occlusion'])
   if 'minecraft:item_visual' in comp:materials({'minecraft:material_instances':comp['minecraft:item_visual']['material_instances']})
  materials(block['components'])
  for perm in block.get('permutations',[]):materials(perm['components'])
  write(p,d)
 # Native block items use item_display_transforms, not attachable animations.
 # Dedicated item meshes avoid inheriting placed-state geometry or rotation.
 for name,source in [('grill','grill_flat'),('oil_press','oil_press_c0_s0')]:
  doc=load(RP/f'models/blocks/{source}.geo.json');geo=doc['minecraft:geometry'][0]
  doc['format_version']='1.21.0';geo['description']['identifier']='geometry.kg_a283.item_'+name
  geo['item_display_transforms']=load(ROOT/f'development/gameplay_core/fixtures/a283/{name}.json')['display']
  write(RP/f'models/blocks/a283_item_{name}.geo.json',doc)
  path=BP/f'blocks/{name}.json';d=load(path);comp=d['minecraft:block']['components']
  comp['minecraft:item_visual']={'geometry':geo['description']['identifier'],'material_instances':deepcopy(comp['minecraft:material_instances'])}
  write(path,d)
 atlas=original(RP/'textures/item_texture.json')
 for name,img in [('advanced_rack',rack_icon()),('skewer_plate',plate_icon())]:
  img.save(RP/f'textures/items/{name}.png',compress_level=9)
  atlas['texture_data'][name]={'textures':f'textures/items/{name}'}
 stats['animation_strip_icons']=[]
 for key,row in atlas['texture_data'].items():
  tex=row.get('textures')
  if not isinstance(tex,str):continue
  path=RP/(tex+'.png')
  if not path.is_file():continue
  im=Image.open(path).convert('RGBA')
  if im.height>im.width and im.height%im.width==0:
   # Item atlases cannot consume Java .mcmeta animation metadata. Keep the
   # strip as source material and use a separate square sprite in the atlas.
   dest='textures/items/a283_icons/'+key
   (RP/dest).parent.mkdir(parents=True,exist_ok=True)
   im.crop((0,0,im.width,im.width)).save(RP/(dest+'.png'))
   row['textures']=dest;stats['animation_strip_icons'].append(key)
 write(RP/'textures/item_texture.json',atlas)
 # Keep guide sprites identical to the actual item icons when that entry exists.
 catalog_path=ROOT/'projects/grilling/guide/catalog.a3.json';catalog=load(catalog_path)
 for name in ('advanced_rack','skewer_plate',*stats['animation_strip_icons']):
  key='textures/ui/kg_grilling/catalog/'+name
  if key in catalog['icon_sources']:
   data=(RP/(atlas['texture_data'][name]['textures']+'.png')).read_bytes();(RP/(key+'.png')).write_bytes(data)
   catalog['icon_sources'][key]['sha256']=hashlib.sha256(data).hexdigest()
   catalog['icon_sources'][key]['source']=(RP/(atlas['texture_data'][name]['textures']+'.png')).relative_to(ROOT).as_posix()
 write(catalog_path,catalog)
 stats['block_materials']=sum(p.read_text().count('"alpha_test_single_sided"') for p in (BP/'blocks').glob('*.json'))
 write(P/'reports/a283-render-changes.json',stats)
 print(json.dumps({k:(sum(map(len,v.values())) if k=='removed_faces' else v) for k,v in stats.items()}))

if __name__=='__main__':build()
