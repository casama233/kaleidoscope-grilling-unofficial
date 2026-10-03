"""Native-frame shell/content projections; no Minecraft client simulation."""
import itertools,json,unittest
from pathlib import Path
from held_pose_frames import RP,chain,translate,zyx,bone_matrix,point
from test_native_skewer_fp import reference_frame,visible
OLD=json.loads((Path(__file__).parent/'fixtures/bottle-frame-before-2.8.52.json').read_text())['animations']
CURRENT=json.loads((RP/'animations/a286_held.animation.json').read_text())['animations']

def projected(geometry,pose,hand):
 matrix=chain(reference_frame(hand),bone_matrix(pose['bones']['grip']),translate([0,-24,0]))
 points=[]
 for b in geometry['bones']:
  for cube in b.get('cubes',[]):
   pivot=cube.get('pivot',[0,0,0]);pivot=[-pivot[0],pivot[1],pivot[2]];r=cube.get('rotation',[0,0,0])
   cm=chain(matrix,translate(pivot),zyx([-r[0],-r[1],r[2]]),translate([-v for v in pivot]))
   for corner in itertools.product((0,1),repeat=3):
    v=[cube['origin'][i]+corner[i]*cube['size'][i] for i in range(3)];v[0]*=-1;points.append(point(cm,v))
 return points

def cases():
 index={g['description']['identifier']:g for p in (RP/'models/entity/a286_hand').glob('*.json') for g in json.loads(p.read_text())['minecraft:geometry']}
 for p in sorted((RP/'attachables').glob('*seasoning*.json')):
  desc=json.loads(p.read_text())['minecraft:attachable']['description']
  for hand in ('right','left'):
   for ref in sorted(set(desc['geometry'].values())):
    yield p.name,hand,ref,index[ref]

class NativeBottleFrames(unittest.TestCase):
 def test_every_shell_and_content_geometry_is_visible_separately(self):
  count=0
  for name,hand,ref,g in cases():
   self.assertTrue(visible(projected(g,CURRENT['animation.kg_a286.bottle_fp_'+hand],hand)),(name,hand,ref));count+=1
  self.assertEqual(count,266)
 def test_old_frame_reproduces_missing_contents(self):
  failures=[(name,hand,ref) for name,hand,ref,g in cases() if not visible(projected(g,OLD['animation.kg_a286.bottle_fp_'+hand],hand))]
  self.assertEqual(len(failures),132)
 def test_only_bottle_first_person_tracks_change(self):
  changed={name for name in CURRENT if CURRENT[name]!=OLD[name]}
  self.assertEqual(changed,{'animation.kg_a286.bottle_fp_right','animation.kg_a286.bottle_fp_left'})
 def test_rack_still_uses_generated_item_icon(self):
  self.assertFalse((RP/'attachables/advanced_rack.attachable.json').exists())
if __name__=='__main__':unittest.main()
