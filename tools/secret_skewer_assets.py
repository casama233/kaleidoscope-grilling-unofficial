"""Pinned Java secret-skewer geometry and tint-atlas layout.

Coordinate conversion is the canonical build_assets.py mapping, preserving every
source cell, exposed face, rotation and UV. Palette colors are baked into copies
of the original white-concrete sprite, not projected ingredient item icons.
"""
from pathlib import Path
from copy import deepcopy
import hashlib,json
from functools import lru_cache
ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/'development/gameplay_core/fixtures/java-secret-skewer-9a1acdab'
STATES=(21,42,63)
COMPLETE_STATES=tuple(a*16+b*4+c for a in range(1,4)for b in range(1,4)for c in range(1,4))
ASSET='common/src/main/resources/assets/kaleidoscope_grilling/'
ATLAS_WIDTH,ATLAS_HEIGHT=256,96

def pinned(path):
 data=(FIX/path).read_bytes();manifest=json.loads((FIX/'source-manifest.json').read_text())
 assert hashlib.sha256(data).hexdigest()==manifest['files'][path]['sha256'],path
 return data

@lru_cache(maxsize=64)
def model(state):return json.loads(pinned(ASSET+f'models/item/skewer_states/state_{state}.json'))

def cube(element,held=False,palette=True):
 a,b=element['from'],element['to'];uv={}
 for name,face in element['faces'].items():
  x0,y0,x1,y1=face['uv']
  if palette:
   local=face['tintindex']%128;cell=local%16;side=local//16
   assert 0<=side<6
   x0+=cell*16;x1+=cell*16;y0+=side*16;y1+=side*16
  if name in ('up','down'):x0,y0,x1,y1=x1,y1,x0,y0
  uv[name]={'uv':[x0,y0],'uv_size':[x1-x0,y1-y0]}
  if face.get('rotation'):uv[name]['uv_rotation']=face['rotation']
 out={'origin':[8-b[0],a[1]+(24 if held else 0),a[2]-8],
      'size':[b[i]-a[i] for i in range(3)],'uv':uv}
 r=element.get('rotation',{})
 if r.get('angle'):
  p=r['origin'];out['pivot']=[8-p[0],p[1]+(24 if held else 0),p[2]-8]
  out['rotation']=[0,0,0];axis='xyz'.index(r['axis']);out['rotation'][axis]=r['angle']*(-1 if axis<2 else 1)
 return out

def slot_cubes(slot,shape,held=False):
 if shape==0:return []
 d=model(STATES[shape-1]);selected=[]
 for element in d['elements']:
  indices=[face.get('tintindex') for face in element['faces'].values()]
  if not any(i is not None for i in indices):continue
  assert all(i is not None and i//128==indices[0]//128 for i in indices)
  if indices[0]//128==slot:selected.append(cube(element,held))
 assert selected and all(all(v>0 for v in c['size']) for c in selected)
 return selected

def shaft_cubes(held=False):
 elements=[e for e in model(21)['elements'] if not any('tintindex'in f for f in e['faces'].values())]
 assert len(elements)==1 and [b-a for a,b in zip(elements[0]['from'],elements[0]['to'])]==[.5,.5,12.5]
 return [cube(elements[0],held,palette=False)]

def geometry(identifier,cubes,held=False,shaft=False):
 description={'identifier':identifier,'texture_width':16 if shaft else ATLAS_WIDTH,'texture_height':16 if shaft else ATLAS_HEIGHT,
              'visible_bounds_width':4 if held else 2,'visible_bounds_height':4 if held else 2,'visible_bounds_offset':[0,1.5,0] if held else [0,.3,0]}
 if held:
  bones=[{'name':'grip','pivot':[0,24,0],'binding':'q.item_slot_to_bone_name(context.item_slot)'},
         {'name':'skewer_pose','parent':'grip','pivot':[0,24,0]},
         {'name':'skewer_model','parent':'skewer_pose','pivot':[0,24,0]}]
 else:bones=[{'name':'root','pivot':[0,0,0]},{'name':'secret_model','parent':'root','pivot':[0,0,0]}]
 if cubes:bones[-1]['cubes']=deepcopy(cubes)
 return {'description':description,'bones':bones}

def held_geometries():
 rows=[geometry('geometry.kg_secret_held.stick',shaft_cubes(True),True,True)]
 for slot in range(3):rows.append(geometry(f'geometry.kg_secret_held.part_{slot}_0',[],True))
 rows.extend(completed_geometries(held=True))
 from generated_food_sprite import helper_assets
 rows.extend(helper_assets()[0])
 return rows

def palette_texture(index,style):return f'textures/secret_food_palette/food_{index}_{style}'
def palette_keys(count):return [f'food_{i}_s{style}'for style in range(7)for i in range(count+1)]
def palette_refs(count):return {f'food_{i}_s{style}':palette_texture(i,style) if i else 'textures/secret_skewer_stick' for style in range(7) for i in range(count+1)}

PARTIAL_STATES=(16,32,48,20,24,28,36,40,44,52,56,60)
def partial_geometries():
 """Exact source states: mixed shape neighbors also alter cell seam extents."""
 rows=[]
 for state in PARTIAL_STATES:
  count=1 if state in (16,32,48)else 2
  for slot in range(count):
   elements=[e for e in model(state)['elements']if any('tintindex'in f for f in e['faces'].values())and next(iter(e['faces'].values()))['tintindex']//128==slot]
   identifier=f'geometry.kg_secret_held.partial_state_{state}_{slot}'
   rows.append(geometry(identifier,[cube(e,held=True)for e in elements],held=True))
 return rows

def state_slot_cubes(state,slot,held=False):
 elements=[e for e in model(state)['elements']if any('tintindex'in f for f in e['faces'].values())and next(iter(e['faces'].values()))['tintindex']//128==slot]
 assert elements
 return [cube(e,held=held)for e in elements]

def completed_geometries(held=False):
 prefix='geometry.kg_secret_held.'if held else 'geometry.kg_station.grill.'
 return [geometry(prefix+f'state_{state}_{slot}',state_slot_cubes(state,slot,held),held)for state in COMPLETE_STATES for slot in range(3)]
