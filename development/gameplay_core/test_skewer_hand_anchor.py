"""Structural grip invariant, not a substitute for Minecraft client acceptance."""
import hashlib
import json
import math
import unittest
from held_pose_frames import make_pose
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RP=ROOT/'projects/grilling/gameplay_core/resource_pack'
ANIM='animations/a287_skewer_held.animation.json'
def load(p): return json.loads(p.read_text())
BEFORE=load(Path(__file__).with_name('fixtures')/'skewer-hand-before-2814.json')
def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
class HandAnchorTests(unittest.TestCase):
    def test_all_bite_stages_preserve_assets_and_bind_once(self):
        refs={r for p in (RP/'attachables').glob('*_skewer.attachable.json') for r in load(p)['minecraft:attachable']['description']['geometry'].values()}
        seen=set()
        for p in (RP/'models/entity/a287_hand').glob('*.geo.json'):
            g=load(p)['minecraft:geometry'][0];seen.add(g['description']['identifier'])
            before=BEFORE['geometry'][p.name]
            self.assertEqual(g['description'],before['description'])
            anchor,pose,model=g['bones']
            self.assertEqual(anchor,{'name':'grip','pivot':[0,24,0],'binding':'q.item_slot_to_bone_name(context.item_slot)'})
            self.assertEqual(pose,{'name':'skewer_pose','parent':'grip','pivot':[0,24,0]})
            self.assertEqual(model['parent'],'skewer_pose')
            self.assertEqual(digest(model['cubes']),before['cubes_sha256'])
            shaft=model['cubes'][0]
            self.assertEqual(shaft['origin'],[-.25,24.75,-8])
            self.assertEqual(shaft['size'],[.5,.5,12.5])
        self.assertEqual(len(seen),150)
        self.assertEqual(refs,seen)
    def test_third_person_handle_is_bound_for_both_hands_and_any_arm_pose(self):
        animations=load(RP/ANIM)['animations']
        for hand in ('right','left'):
            bones=animations[f'animation.kg_a287.skewer_tp_{hand}']['bones']
            self.assertEqual(bones['skewer_pose']['position'],[0,0,0])
            correction=bones['skewer_model']['position']
            handle=[0,25,-6];pivot=[0,24,0]
            relative=[h+c-p for h,c,p in zip(handle,correction,pivot)]
            self.assertEqual(relative,[0,0,0])
            # Any linear rotation/scale keeps this zero vector at the hand anchor.
            # Native eat/sneak/walk arm motion therefore cannot amplify an offset.
            for scale in (.8,1,1.25):
                self.assertEqual([v*scale for v in relative],[0,0,0])
    def test_first_person_display_uses_converted_frame(self):
        before=BEFORE['animations'];after=load(RP/ANIM)['animations']
        for hand in ('right','left'):
            name=f'animation.kg_a287.skewer_fp_{hand}'
            self.assertEqual(after[name]['bones'],make_pose('skewer','fp',hand))
            self.assertNotEqual(after[name]['bones']['skewer_pose'],before[name]['bones']['grip'])
            self.assertEqual(after[name]['bones']['skewer_model']['position'],[0,0,0])
    def test_rack_preserves_assets_and_uses_converted_display_frame(self):
        g=load(RP/'models/entity/a286_hand/kg_a2763.advanced_rack_hand.geo.json')['minecraft:geometry'][0]
        self.assertEqual(g['bones'][2]['cubes'],BEFORE['rack_geometry']['bones'][0]['cubes'])
        self.assertEqual(g['bones'][1],{'name':'rack_pose','parent':'grip','pivot':[0,24,0]})
        self.assertEqual(g['bones'][2]['parent'],'rack_pose')
        self.assertEqual(g['bones'][2]['pivot'],[0,24,0])
        a=load(RP/'animations/a286_held.animation.json')['animations']
        for hand in ('right','left'):
            tp=a[f'animation.kg_a286.rack_tp_{hand}']['bones']
            self.assertEqual(tp,make_pose('rack','tp',hand))
            self.assertEqual([x+c-p for x,c,p in zip([0,16.5,1.625],tp['rack_model']['position'],[0,24,0])],[0,0,0])
            name=f'animation.kg_a286.rack_fp_{hand}'
            self.assertEqual(a[name]['bones'],make_pose('rack','fp',hand))
            self.assertEqual(a[name]['bones']['rack_model']['position'],[0,0,0])
    def test_reproduces_previous_displaced_grip(self):
        before=BEFORE['animations']
        for hand in ('right','left'):
            b=before[f'animation.kg_a287.skewer_tp_{hand}']['bones']['grip']
            # Even without assuming Euler conventions, unequal vector lengths
            # prove authored translation cannot cancel the rotated handle offset.
            displacement=math.sqrt(sum(v*v for v in b['position']))
            handle_radius=math.sqrt(37)*.8
            self.assertGreater(abs(displacement-handle_radius),3)
if __name__=='__main__':unittest.main()
