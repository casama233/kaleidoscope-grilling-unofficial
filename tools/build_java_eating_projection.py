"""Source-derived standing first-person branch; native clips are a separate gate.

TWO/THREE_ALT/FOUR only. The helper-arm ONE/THREE branch and non-standing
views keep their existing path until separately implemented and accepted.
"""
from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'development/gameplay_core'))
from java_active_eating_frames import (PROFILES,ARRAYS,active_child_bone,
    native_arm_target)
from held_pose_frames import bedrock_rotation,point
from native_eating_clock import SECONDS

P=ROOT/'projects/grilling/gameplay_core';RP=P/'resource_pack';BP=P/'behavior_pack'
PROPERTY='kaleidoscope_grilling:eat_projection'
CODES={'TWO':2,'THREE_ALT':4,'FOUR':5}
# Eye height/camera calibration is deliberately bounded to upright normal use.
CONTEXT=("q.is_using_item && q.property('"+PROPERTY+"') == 1 && "
         "q.is_sneaking == 0 && q.is_swimming == 0 && q.is_gliding == 0 && q.is_riding == 0")

def number(n):
    if abs(n)<1e-8:n=0
    return format(n,'.8f').rstrip('0').rstrip('.') or '0'

def rounded_channel(value):
    # libm cancellation may produce either zero sign on different platforms.
    value=round(value,8)
    return 0.0 if value==0 else value

def initial_euler(value):
    # Choose one representative only at the first key. Wrapping every key
    # would turn a continuous curve into a spurious full-spin interpolation.
    value=(value+180.0)%360.0-180.0
    if abs(abs(value)-180.0)<1e-8:return -180.0
    return value

def unwrap(values,previous):
    if previous is None:return [initial_euler(v) for v in values]
    return [v+360*round((old-v)/360)for v,old in zip(values,previous)]

def sample_times():
    times={round(i/60,6)for i in range(271)}
    for key,rows in ARRAYS.items():
        if key.endswith('_TIMES'):times.update(float(v)for v in rows if 0<=v<=4.5)
    times.update([.45833,.95833,1.20833,2.25,2.33333,4.5])
    return sorted(times)

def item_animation_id(profile,hand):return 'animation.kg_java_eating.item.'+profile.lower()+'.'+hand
def player_animation_id(profile,hand):return 'animation.kg_java_eating.player.'+profile.lower()+'.'+hand

def animations():
    item_animations={};player_animations={}
    for profile in PROFILES:
        for hand,sign in [('right',1),('left',-1)]:
            arm=hand+'arm';socket=hand+'item';other=('left'if hand=='right'else'right')+'item'
            slim=("math.abs(q.get_default_bone_pivot('"+arm+"', 1) - 21.5) < 0.01")
            positions={};rotations={};arm_positions={};arm_rotations={};socket_positions={}
            last_item=None;last_arm=None
            for t in sample_times():
                key=number(t)
                wide=active_child_bone(profile,t,sign,False)
                narrow=active_child_bone(profile,t,sign,True)
                # Resolve rig shape in the player animation component, never
                # through an attachable owning_entity geometry assumption.
                # O is translation-only, so a child-origin delta can be moved
                # unchanged into the normalized player item socket.
                positions[key]=[rounded_channel(a) for a in wide['position']]
                socket_base=['0',"q.get_default_bone_pivot('"+arm+"',1) - q.get_default_bone_pivot('"+socket+"',1) - 7",
                             "-q.get_default_bone_pivot('"+socket+"',2)"]
                socket_positions[key]=[base+' + ('+slim+' ? '+number(b-a)+' : 0)'
                                       for base,a,b in zip(socket_base,wide['position'],narrow['position'])]
                rotation=unwrap(wide['rotation'],last_item);last_item=rotation
                rotations[key]=[rounded_channel(v)for v in rotation]
                target=native_arm_target(profile,t,sign)
                at=point(target,[0,0,0]);at[0]*=-1
                arm_positions[key]=[number(at[i])+" - q.get_default_bone_pivot('"+arm+"', "+str(i)+")"for i in range(3)]
                rotation=unwrap(bedrock_rotation(target),last_arm);last_arm=rotation
                arm_rotations[key]=[rounded_channel(v)for v in rotation]
            common={'loop':'hold_on_last_frame','animation_length':4.5,'anim_time_update':SECONDS}
            item_animations[item_animation_id(profile,hand)]={**common,'bones':{
                'skewer_pose':{'position':positions,'rotation':rotations,'scale':[1,1,1]},
                'skewer_model':{'position':[0,0,0],'rotation':[0,0,0],'scale':[1,1,1]}}}
            player_animations[player_animation_id(profile,hand)]={**common,'override_previous_animation':True,
                'blend_weight':'variable.is_first_person && '+CONTEXT,
                'bones':{
                    arm:{'position':arm_positions,'rotation':arm_rotations},
                    socket:{'position':socket_positions,
                            'rotation':[0,0,0]},
                    other:{'scale':0}}}
    return item_animations,player_animations

def augment(output,profile_table):
    item,player=animations()
    output[RP/'animations/java_eating_projection.animation.json']={'format_version':'1.8.0','animations':item}
    output[RP/'animations/java_eating_player.animation.json']={'format_version':'1.8.0','animations':player}
    ids=[]
    for path,doc in list(output.items()):
        if path.parent!=RP/'attachables':continue
        d=doc['minecraft:attachable']['description'];configured=profile_table.get(d['identifier'])
        profile='THREE_ALT'if configured=='THREE_RANDOM'else configured
        if profile not in PROFILES:continue
        if not all(ref.startswith('geometry.kg_a287.kg_a22.')for ref in d['geometry'].values()):continue
        ids.append(d['identifier'])
        d['scripts']['animate']=[row for row in d['scripts']['animate']if not any(k.startswith('fp_eat_')for k in row)]
        for hand,slot,code in [('right','main_hand',1),('left','off_hand',2)]:
            active=("c.is_first_person == 1 && "+CONTEXT+" && q.property('kaleidoscope_grilling:eat_profile') == "+str(CODES[profile])+
                    " && q.property('kaleidoscope_grilling:eat_hand') == "+str(code)+" && c.item_slot == '"+slot+"'")
            for row in d['scripts']['animate']:
                if 'fp_'+hand in row:
                    row['fp_'+hand]="c.is_first_person == 1 && c.item_slot == '"+slot+"' && ("+active+") == 0"
                for key in ('eat_'+hand,'eat_alt_'+hand):
                    if key in row:row[key]='('+row[key]+') && ('+active+') == 0'
            alias='fp_eat_'+hand;d['animations'][alias]=item_animation_id(profile,hand)
            d['scripts']['animate'].append({alias:active})
    native=json.loads((ROOT/'development/gameplay_core/fixtures/native-first-person-controller-1.26.50.4.json').read_text())['controller']
    controller=json.loads(json.dumps(native))
    owned="q.has_property('"+PROPERTY+"') && "+CONTEXT
    for row in controller['part_visibility']:
        for bone,expression in list(row.items()):
            if bone in ('rightArm','rightSleeve','leftArm','leftSleeve'):
                hand=1 if bone.startswith('right')else 2
                row[bone]='('+owned+") ? (q.property('kaleidoscope_grilling:eat_hand') == "+str(hand)+') : ('+expression+')'
    output[RP/'render_controllers/java_eating_player.render_controllers.json']={'format_version':'1.8.0','render_controllers':{'controller.render.player.first_person':controller}}
    # Data-only eligibility: missing/failed/secret geometries never enable a
    # different player arm while their item remains on a legacy transform.
    output[BP/'scripts/java_eating_projection_items.js']='// Fixed-geometry eligibility for the scoped Java first-person projection.\nexport const JAVA_FP_EATING_ITEMS=Object.freeze('+json.dumps(sorted(ids))+');\n'
    return output
