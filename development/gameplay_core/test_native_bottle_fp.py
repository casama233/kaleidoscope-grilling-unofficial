"""Native-frame shell/content projections; no Minecraft client simulation."""
import itertools,json,math,unittest
from pathlib import Path
from held_pose_frames import RP,chain,translate,zyx,bone_matrix,point
from test_native_skewer_fp import reference_frame,visible
OLD=json.loads((Path(__file__).parent/'fixtures/bottle-frame-before-2.8.52.json').read_text())['animations']
CURRENT=json.loads((RP/'animations/a286_held.animation.json').read_text())['animations']
LEGACY_FIXED=json.loads((Path(__file__).parent/'fixtures/bottle-fixed-source-routes.json').read_text())['routes']

def vector(value,default):
 if value is None:value=default
 if isinstance(value,(int,float)):value=[value]*3
 if not isinstance(value,(tuple,list)) or len(value)!=3 or not all(isinstance(v,(int,float)) and math.isfinite(v) for v in value):
  raise ValueError('Projection requires finite numeric bone channels')
 return value

def projected_by_bone(geometry,pose,hand):
 """Traverse actual parent transforms; return every shell/contents bone's corners.

 The bound grip's pivot maps to the native item socket. Child bone transforms
 act around their model-space pivots and inherit the parent's complete matrix.
 No render-controller visibility filtering: every potentially selected contents
 layer must fit. Unsupported bindings, cyclic/missing parents fail closed.
 """
 bones={b['name']:b for b in geometry['bones']}
 if len(bones)!=len(geometry['bones']):raise ValueError('Duplicate bone name')
 bound=[b for b in bones.values() if b.get('binding')]
 if len(bound)!=1 or bound[0]['name']!='grip' or bound[0].get('parent') or bound[0].get('pivot')!=[0,24,0] or bound[0]['binding']!='q.item_slot_to_bone_name(context.item_slot)':
  raise ValueError('Unsupported item binding')
 if set(pose['bones'])-set(bones):raise ValueError('Animation targets missing bones')
 matrices={};visiting=set()
 def matrix(name):
  if name in matrices:return matrices[name]
  if name in visiting:raise ValueError('Cyclic bone hierarchy')
  if name not in bones:raise ValueError('Missing parent bone')
  visiting.add(name);b=bones[name];animated=pose['bones'].get(name,{})
  if b.get('reset') or b.get('inherit_scale') is False:raise ValueError('Unsupported inheritance modifier')
  channels={}
  for key in ('position','rotation'):
   base=vector(b.get(key),[0,0,0]);delta=vector(animated.get(key),[0,0,0]);channels[key]=[a+d for a,d in zip(base,delta)]
  base=vector(b.get('scale'),[1,1,1]);delta=vector(animated.get('scale'),[1,1,1]);channels['scale']=[a*d for a,d in zip(base,delta)]
  pivot=vector(b.get('pivot'),[0,0,0]);pivot=[-pivot[0],pivot[1],pivot[2]]
  if name=='grip':result=chain(reference_frame(hand),bone_matrix(channels),translate([-v for v in pivot]))
  else:
   if not b.get('parent'):raise ValueError('Unbound root bone')
   result=chain(matrix(b['parent']),translate(pivot),bone_matrix(channels),translate([-v for v in pivot]))
  visiting.remove(name);matrices[name]=result;return result
 points={}
 for name,b in bones.items():
  parent=matrix(name);points[name]=[]
  for cube in b.get('cubes',[]):
   pivot=vector(cube.get('pivot'),[0,0,0]);pivot=[-pivot[0],pivot[1],pivot[2]];r=vector(cube.get('rotation'),[0,0,0])
   cm=chain(parent,translate(pivot),zyx([-r[0],-r[1],r[2]]),translate([-v for v in pivot]))
   origin=vector(cube['origin'],[0,0,0]);size=vector(cube['size'],[0,0,0]);inflate=cube.get('inflate',0)
   if not isinstance(inflate,(int,float)) or not math.isfinite(inflate):raise ValueError('Invalid cube inflation')
   for corner in itertools.product((0,1),repeat=3):
    v=[origin[i]-inflate+corner[i]*(size[i]+2*inflate) for i in range(3)];v[0]*=-1;points[name].append(point(cm,v))
 return points

def projected(geometry,pose,hand):
 return [v for points in projected_by_bone(geometry,pose,hand).values() for v in points]

def geometry_index():
 index={}
 for p in (RP/'models/entity').rglob('*.json'):
  for g in json.loads(p.read_text()).get('minecraft:geometry',[]):
   ref=g['description']['identifier']
   if ref in index:raise ValueError('Duplicate geometry identifier: '+ref)
   index[ref]=g
 return index

def cases(legacy=False):
 index=geometry_index()
 for p in sorted((RP/'attachables').glob('*seasoning*.json')):
  desc=json.loads(p.read_text())['minecraft:attachable']['description']
  refs=set(desc['geometry'].values())
  if legacy:
   # G71-only proxy routes did not exist in the historical missing-fill frame.
   # Keep that 67-route witness exact; current-frame coverage above includes all.
   if desc['identifier'].startswith(('kaleidoscope_grilling:partial_seasoning_f','kaleidoscope_grilling:pending_seasoning_f')):continue
   if desc['identifier']=='kaleidoscope_grilling:empty_seasoning_bottle':
    refs={'geometry.kg_a286.kg_a2733.seasoning_bottle_hand'}
   elif desc['identifier']=='kaleidoscope_grilling:pending_seasoning':
    refs={'geometry.kg_a286.kg_a2766.special_seasoning.r4.v0','geometry.kg_a286.kg_a2766.special_seasoning.r4.v0.contents'}
   else:
    # Exact source aliases preserve invalid-v fallbacks; never infer r/v refs.
    refs=set(LEGACY_FIXED[desc['identifier']]['geometry'].values())
  for hand in ('right','left'):
   for ref in sorted(refs):
    yield p.name,hand,ref,index[ref]

class NativeBottleFrames(unittest.TestCase):
 def test_every_shell_and_content_geometry_is_visible_separately(self):
  count=0
  for name,hand,ref,g in cases():
   self.assertTrue(visible(projected(g,CURRENT['animation.kg_a286.bottle_fp_'+hand],hand)),(name,hand,ref));count+=1
  self.assertEqual(count,sum(2*len(set(json.loads(p.read_text())['minecraft:attachable']['description']['geometry'].values())) for p in (RP/'attachables').glob('*seasoning*.json')))
 def test_old_frame_reproduces_missing_contents(self):
  # Preserve the original133-per-hand route inventory independently of the
  # new partial-bottle contents. The retained r4 meshes remain source assets.
  failures=[(name,hand,ref) for name,hand,ref,g in cases(legacy=True) if not visible(projected(g,OLD['animation.kg_a286.bottle_fp_'+hand],hand))]
  self.assertEqual(sum(hand=='right' for _,hand,_ in failures),66)
  self.assertEqual(sum(hand=='left' for _,hand,_ in failures),133)
 def test_only_bottle_first_person_tracks_change(self):
  changed={name for name in CURRENT if CURRENT[name]!=OLD[name]}
  self.assertEqual(changed,{'animation.kg_a286.bottle_fp_right','animation.kg_a286.bottle_fp_left'})
 def test_rack_still_uses_generated_item_icon(self):
  self.assertFalse((RP/'attachables/advanced_rack.attachable.json').exists())
if __name__=='__main__':unittest.main()
