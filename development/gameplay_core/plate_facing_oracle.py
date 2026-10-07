"""Sample-calibrated mesh/world oracle, not a Minecraft renderer or client pass.

Java layout source: breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c
neoforge-1.21.1/.../skewer/SkewerPlateRenderer.java, SHA256
81afc858b3eb2d347af3ba9c228178519931d1091c17eb2b884df721be426f93.
Native yaw/basis calibration comes from bounded G88 observations, runtime
7e0d855fcd9a5e5e9a1ed71f27f25137c4334543. It is a hypothesis to verify
against native upper diagonals/asymmetric models, not all-facing acceptance.
"""
import itertools
import json
from pathlib import Path
import subprocess
from held_pose_frames import chain, point, rotate, scale, translate, xyz

ROOT=Path(__file__).resolve().parents[2]
RP=ROOT/'projects/grilling/gameplay_core/resource_pack'
FACING={'south':0,'west':90,'north':180,'east':270}
JAVA_LAYOUTS=[[],[[8,4,6.3,0]],[[5.6,4.15,5.95,0],[10.4,4.2,5.9,0]],
 [[5.6,3.95,6.35,0],[10.4,4,6.3,0],[8,7.375,7.65,-22.5]],
 [[8,3.95,6.35,0],[12.55,4,6.3,0],[3.45,4,6.3,0],[8,7.325,7.7,-45]],
 [[8,3.95,6.35,0],[12.55,4,6.3,0],[3.45,4,6.3,0],[10.4,7.325,7.4,-22.5],[5.7,7.375,7.35,-22.5]]]
CALIBRATION_CAPTURES={
 'g88_plate_south5.jpg':'bbf135974e5136dd009225071ca05ac490a1dc48bf1851ce619aaf363030e197',
 'g88_plate_east5.jpg':'248680e4a07a2dd40db1eadf43e48e604ec836aeb75e6f3926f3054aefe0fed1',
 'g88_plate_after_reload.jpg':'f0801e9caf75f36003db73416826636f80459cc3867b4a2cc5c6d9d5dbc027ca',
 'g88_plate_north_state.jpg':'7ea59d5bd01e1ec53220e4f955ac3f29b3c83044e82d28271da890ccb77bb62b'}

def runtime_poses():
 module=(ROOT/'projects/grilling/gameplay_core/behavior_pack/scripts/plate_visual_core.js').as_uri()
 code=f"import {{plateVisualPose,PLATE_VISUAL_LAYOUTS}} from '{module}';"+"const rows=[];for(const direction of ['south','west','north','east'])for(let count=1;count<=5;count++)for(let slot=0;slot<count;slot++){const block={x:0,y:0,z:0,permutation:{getState:()=>direction}};rows.push({direction,count,slot,pose:plateVisualPose(block,slot,count)});}process.stdout.write(JSON.stringify({layouts:PLATE_VISUAL_LAYOUTS,rows}));"
 return json.loads(subprocess.check_output(['node','--input-type=module','-e',code],text=True))

def native_matrix(yaw):
 # Derived from native samples; unlike a requested-yaw assertion this applies
 # the signed entity yaw and model Z basis to actual exported mesh points.
 return chain(rotate('y',-yaw),scale([1,1,-1]))

def java_model_matrix(fixed):
 return chain(rotate('z',180),rotate('x',90),scale([.8]*3),
  translate(fixed['translation']),xyz(fixed['rotation']),scale(fixed['scale']),translate([-8,-8,-8]))

def shaft_errors(geo,fixed,poses,clip,mesh_y_shift=1,yaw_override=None):
 shaft=next(c for b in geo['bones']for c in b.get('cubes',[])
  if c['size']==[.5,.5,12.5])
 assert 'rotation'not in shaft
 errors=[]
 for row in poses:
  sx,sy,sz,theta=JAVA_LAYOUTS[row['count']][row['slot']];F=FACING[row['direction']]
  target=chain(translate([8,0,8]),rotate('y',-F),translate([-8,0,-8]),
   translate([sx,sy,sz]),rotate('y',theta),java_model_matrix(fixed))
  at=row['pose'];yaw=-at['angle']if yaw_override is None else yaw_override(F,theta)
  anchor=[at['location'][axis]*16 for axis in 'xyz']
  native=chain(translate(anchor),native_matrix(yaw),translate(clip['position']),scale([clip['scale']]*3))
  for corner in itertools.product((0,1),repeat=3):
   q=[shaft['origin'][i]+shaft['size'][i]*corner[i]for i in range(3)]
   authored=[8-q[0],q[1]+mesh_y_shift,q[2]+8]
   errors.append(max(abs(a-b)for a,b in zip(point(target,authored),point(native,q))))
 return errors

if __name__=='__main__':
 poses=runtime_poses();assert poses['layouts']==JAVA_LAYOUTS
 geos=json.loads((RP/'models/entity/grill_display.geo.json').read_text())['minecraft:geometry']
 geo=next(g for g in geos if g['description']['identifier'].endswith('.raw_beef_skewer'))
 fixed=json.loads((ROOT/'projects/grilling/reports/java_display_transforms/beef_raw.json').read_text())['java_display']['fixed']
 errors=shaft_errors(geo,fixed,poses['rows'],{'scale':1.2,'position':[0,-.6,1.8]})
 assert len(errors)==480 and max(errors)<1e-8,max(errors)
 print(f'Calibrated480-corner plate projection PASS; max error{max(errors):.3g}px; native acceptance separate')
