"""Structural grip invariant, not a substitute for Minecraft client acceptance."""
import hashlib
import json
import math
import unittest
from held_pose_frames import make_pose,chain,translate,rotate,xyz,scale,point,bone_matrix
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
        refs={r for p in (RP/'attachables').glob('*_skewer.attachable.json') if p.name!='secret_skewer.attachable.json' for r in load(p)['minecraft:attachable']['description']['geometry'].values()}
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
    def test_secret_ingredients_share_the_existing_grip_and_stable_two_sided_faces(self):
        geometries=load(RP/'models/entity/secret_held.geo.json')['minecraft:geometry']
        refs=set(load(RP/'attachables/secret_skewer.attachable.json')['minecraft:attachable']['description']['geometry'].values())
        self.assertEqual(refs,{g['description']['identifier'] for g in geometries})
        for geo in geometries:
            anchor,pose,model=geo['bones']
            self.assertEqual(anchor,{'name':'grip','pivot':[0,24,0],'binding':'q.item_slot_to_bone_name(context.item_slot)'})
            self.assertEqual(pose,{'name':'skewer_pose','parent':'grip','pivot':[0,24,0]})
            self.assertEqual(model['parent'],'skewer_pose')
            self.assertNotIn('texture_meshes',model)
            if '.part_' in geo['description']['identifier']:
                for cube in model.get('cubes',[]):self.assertEqual(set(cube['uv']),{'up','down'})
    def test_third_person_matches_java_corners_for_both_hands(self):
        animations=load(RP/ANIM)['animations']
        display=load(ROOT/'projects/grilling/reports/java_display_transforms/beef_raw.json')['java_display']
        for hand,sign in [('right',1),('left',-1)]:
            bones=animations[f'animation.kg_a287.skewer_tp_{hand}']['bones']
            source=display['thirdperson_'+hand+'hand']
            r=source['rotation'];r=[r[0],r[1]*sign,r[2]*sign]
            t=source['translation'];t=[t[0]*sign,t[1],t[2]]
            arm=rotate('x',15)
            target=chain(translate([6*sign,22,0]),arm,translate([0,-10,-2]),rotate('x',-90),translate(t),xyz(r),scale(source['scale']),translate([-8,-8,-8]),translate([8,-24,8]))
            base=chain(translate([5*sign,22,0]),arm,translate([sign,-31,1]))
            actual=chain(base,translate([0,24,0]),bone_matrix(bones['skewer_pose']),bone_matrix(bones['skewer_model']),translate([0,-24,0]))
            # Compare every bite-stage cube corner, including bamboo grip points.
            import itertools
            for path in (RP/'models/entity/a287_hand').glob('*.geo.json'):
                model=load(path)['minecraft:geometry'][0]['bones'][2]
                for cube in model['cubes']:
                    for delta in itertools.product((0,1),repeat=3):
                        vertex=[cube['origin'][i]+delta[i]*cube['size'][i] for i in range(3)]
                        for a,b in zip(point(actual,vertex),point(target,vertex)):
                            self.assertAlmostEqual(a,b,places=6)
            self.assertNotEqual(bones['skewer_pose']['position'],[0,0,0])
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
