"""Actual native left socket regressions; no native-use or visual parity claim."""
import itertools,json,unittest
from pathlib import Path
from held_pose_frames import RP,chain,bone_matrix,point
from test_native_skewer_fp import reference_frame,vertices,visible
from test_native_bottle_fp import cases,projected,projected_by_bone
OLD=json.loads((Path(__file__).parent/'fixtures/idle-poses-before-2.8.58.json').read_text())['animations']
CURRENT={}
for f in ('a287_skewer_held.animation.json','a286_held.animation.json'):
 CURRENT.update(json.loads((RP/'animations'/f).read_text())['animations'])
class NativeOffhandIdle(unittest.TestCase):
 def test_only_inherited_left_skewer_and_bottle_framing_change(self):
  self.assertEqual({k for k in CURRENT if CURRENT[k]!=OLD[k]}, {'animation.kg_a287.skewer_fp_left','animation.kg_a286.bottle_fp_left','animation.kg_a286.bottle_fp_right'})
 def test_previous_mirrored_skewer_frame_fails_all_actual_left_cases(self):
  failed=0
  for p in (RP/'models/entity/a287_hand').glob('*.geo.json'):
   geo=json.loads(p.read_text())['minecraft:geometry'][0]
   cubes=vertices(geo,OLD['animation.kg_a287.skewer_fp_left'],'left')
   self.assertFalse(any(visible(c)for c in cubes),p.name);failed+=1
  self.assertEqual(failed,150)
 def test_previous_bottle_frame_fails_actual_left_cases(self):
  checked=0
  for name,hand,ref,g in cases():
   if hand!='left':continue
   self.assertFalse(visible(projected(g,OLD['animation.kg_a286.bottle_fp_left'],hand)),(name,ref));checked+=1
  version=tuple(json.loads((RP.parent/'behavior_pack/manifest.json').read_text())['header']['version'])
  self.assertEqual(checked,132 if version>=(2,8,61) else 133)
 def test_historical_bottle_routes_and_new_layer_delta_are_explicit(self):
  original={(name,ref):g for name,hand,ref,g in cases(legacy=True) if hand=='left'}
  self.assertEqual(len(original),133)
  for (name,ref),g in original.items():
   self.assertFalse(visible(projected(g,OLD['animation.kg_a286.bottle_fp_left'],'left')),(name,ref))
  version=tuple(json.loads((RP.parent/'behavior_pack/manifest.json').read_text())['header']['version'])
  if version<(2,8,61):return
  current={(name,ref):g for name,hand,ref,g in cases() if hand=='left'}
  # Empty/pending now reference one bound rig with shell and all16 selectable
  # half-layer children. Replacing their old1+2 refs with1+1 gives net -1.
  combined={key:g for key,g in current.items() if key[1]=='geometry.kg_bottle_held.combined'}
  self.assertEqual({name for name,ref in combined},{'empty_seasoning_bottle.attachable.json','pending_seasoning.attachable.json'})
  self.assertEqual(len(current)-len(original),-1)
  self.assertEqual(len(set(current)-set(original)),2)
  self.assertEqual(len(set(original)-set(current)),3)
  for (name,ref),g in combined.items():
   bound=[b for b in g['bones'] if b.get('binding')]
   self.assertEqual(len(bound),1)
   self.assertEqual(bound[0]['name'],'grip')
   self.assertEqual(bound[0]['binding'],'q.item_slot_to_bone_name(context.item_slot)')
   self.assertEqual(bound[0]['pivot'],[0,24,0])
   before=projected_by_bone(g,OLD['animation.kg_a286.bottle_fp_left'],'left')
   after=projected_by_bone(g,CURRENT['animation.kg_a286.bottle_fp_left'],'left')
   self.assertEqual(set(after),{'grip','shell'}|{f'pending_{n}' for n in range(16)})
   for bone in ('shell',*(f'pending_{n}' for n in range(16))):
    self.assertTrue(after[bone],(name,ref,bone))
    self.assertFalse(visible(before[bone]),(name,ref,bone))
    self.assertTrue(visible(after[bone]),(name,ref,bone))
 def test_native_equip_bob_and_slim_translation_are_inherited(self):
  for name,bone in [('animation.kg_a287.skewer_fp_left','skewer_pose'),('animation.kg_a286.bottle_fp_left','grip')]:
   pose=bone_matrix(CURRENT[name]['bones'][bone]);base=chain(reference_frame('left'),pose)
   for slim,H,bob in itertools.product((False,True),(0,.25,.5,.75,1),((0,0,0),(.25,-.5,.3),(-.3,.2,-.4))):
    actual=chain(reference_frame('left',slim,H,bob),pose)
    delta=(-bob[0],-(.5 if slim else 0)-10*(1-H)+bob[1],-bob[2])
    for v in ((0,0,0),(1,24,2),(-3,21,-4)):
     before=point(base,v);after=point(actual,v)
     for a,b,offset in zip(after,before,delta):self.assertAlmostEqual(a-b,offset,places=8)
 def test_no_unreliable_context_dependency_added(self):
  for name in ('animation.kg_a287.skewer_fp_left','animation.kg_a286.bottle_fp_left'):
   self.assertNotIn('player_offhand_arm_height',json.dumps(CURRENT[name]))
   self.assertNotIn('owning_entity',json.dumps(CURRENT[name]))
if __name__=='__main__':unittest.main()
