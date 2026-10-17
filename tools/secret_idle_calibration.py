"""Empirical 1.26.52.3 idle-only calibration; not a universal engine-eye claim.

The shared pose and active eating/helper clips remain canonical and unchanged.
A +3.41 world-Y displacement from the accepted 6710 A/B is inverse-mapped
through the right socket. Only three owned threaded attachables opt into it.
"""
from pathlib import Path
from copy import deepcopy
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];RP=ROOT/'projects/grilling/gameplay_core/resource_pack'
FIX=ROOT/'development/gameplay_core/fixtures/secret-idle-fp-calibration-1.26.52.3.json'
TARGET=RP/'animations/secret_idle_fp_calibration.animation.json'
OWNED=('kaleidoscope_grilling:secret_skewer','kaleidoscope_grilling:secret_skewer_java_three_alt','kaleidoscope_grilling:unfinished_skewer')

def clip_id(hand):return 'animation.kg_secret_held.fp_idle_calibrated_1_26_52_3_'+hand

def owning_hand_using(hand):
 return "q.is_using_item && q.property('kaleidoscope_grilling:eat_hand') == "+str(1 if hand=='right'else 2)+" && c.item_slot == '"+('main_hand'if hand=='right'else 'off_hand')+"'"

def animation_document():
 proof=json.loads(FIX.read_text());shared_path=RP/'animations/a287_skewer_held.animation.json';raw=shared_path.read_bytes()
 assert hashlib.sha256(raw).hexdigest()==proof['shared_animation_sha256'],'Recalibration needs fresh native evidence when shared pose changes'
 source=json.loads(raw)['animations'];sys.path.insert(0,str(ROOT/'development/gameplay_core'))
 from held_pose_frames import chain,rotate,point,rigid_inverse
 socket=chain(*(rotate(axis,degrees)for axis,degrees in proof['right_socket_rotation_order']));delta=proof['world_y_delta'];local=point(rigid_inverse(socket),[0,delta,0]);animations={}
 for hand in ('right','left'):
  clone=deepcopy(source['animation.kg_a287.skewer_fp_'+hand]);position=clone['bones']['skewer_pose']['position'];shift=[-local[0],local[1],local[2]]if hand=='right'else[0,delta,0]
  result=[round(position[i]+shift[i],8)for i in range(3)];assert result==proof['expected_positions'][hand]
  clone['bones']['skewer_pose']['position']=result;animations[clip_id(hand)]=clone
 return {'format_version':'1.8.0','animations':animations}

def apply_idle_calibration(description):
 if description['identifier']not in OWNED:return description
 description['animations']={k:v for k,v in description['animations'].items()if not k.startswith('fp_idle_calibrated_')}
 animate=description['scripts']['animate'];animate=[r for r in animate if not any(k.startswith('fp_idle_calibrated_')for k in r)]
 for hand in ('right','left'):
  alias='fp_'+hand;description['animations'][alias]='animation.kg_a287.skewer_'+alias
  calibrated='fp_idle_calibrated_'+hand;description['animations'][calibrated]=clip_id(hand)
  suffix=' && ('+owning_hand_using(hand)+')'
  for row in animate:
   if alias in row:
    expression=row[alias]
    while expression.endswith(suffix):expression=expression[:-len(suffix)]
    row[alias]=expression+suffix
  slot='main_hand'if hand=='right'else'off_hand'
  animate.append({calibrated:"c.is_first_person == 1 && c.item_slot == '"+slot+"' && ("+owning_hand_using(hand)+') == 0'})
 description['scripts']['animate']=animate
 return description

def augment(output):
 for path,doc in output.items():
  if path.parent==RP/'attachables':apply_idle_calibration(doc['minecraft:attachable']['description'])
 output[TARGET]=animation_document()
 return output
