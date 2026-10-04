"""Ingredient layers and Java seasoning motion in the existing bound item frame.

The Java view translation is adapted to Bedrock's visible idle anchor. Curves,
duration, inversion and ordered tint layers come from the pinned Java source;
the resulting client presentation still requires human acceptance.
"""
from pathlib import Path
from copy import deepcopy
import argparse,json,math,re,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'development/gameplay_core'))
from held_pose_frames import chain,translate,xyz,scale,rigid_inverse,bedrock_rotation,bone_matrix,point
P=ROOT/'projects/grilling/gameplay_core';RP=P/'resource_pack';BP=P/'behavior_pack'
NS='kaleidoscope_grilling:'
def load(p):return json.loads(p.read_text())
def palette_size():
 return len(json.loads(re.search(r'PLACED_TINT_INDEX=Object.freeze\((.*)\);',(BP/'scripts/a2770_placed_visual_data.js').read_text()).group(1)))
def dispatch(pending=False):
 ids={};selectors={}
 for hand,slot,code in [('right','main_hand',1),('left','off_hand',2)]:
  fp=f"c.is_first_person == 1 && c.item_slot == '{slot}'"
  season=f"(q.property('{NS}season_hand') == {code} && q.property('{NS}season_phase') != 0)"
  shake=f"(q.is_using_item && q.property('{NS}pending_hand') == {code})" if pending else '0 == 1'
  ids['fp_'+hand]='animation.kg_a286.bottle_fp_'+hand
  ids['tp_'+hand]='animation.kg_a286.bottle_tp_'+hand
  ids['season_'+hand]='animation.kg_seasoning.item.sprinkle.'+hand
  # Explicit complementary selectors: one pose owns the entire grip at a time.
  selectors['fp_'+hand]=fp+f" && (q.property('{NS}season_hand') != {code} || q.property('{NS}season_phase') == 0)"
  if pending:
   ids['shake_'+hand]='animation.kg_seasoning.item.shake.'+hand
   selectors['fp_'+hand]+=f" && (q.is_using_item == 0 || q.property('{NS}pending_hand') != {code})"
   selectors['shake_'+hand]=fp+' && '+shake+f" && (q.property('{NS}season_hand') != {code} || q.property('{NS}season_phase') == 0)"
  selectors['season_'+hand]=fp+' && '+season
  selectors['tp_'+hand]=f"c.is_first_person == 0 && c.item_slot == '{slot}'"
 return ids,selectors
def motion(hand,t,shaking):
 sign=1 if hand=='right' else -1
 p=t/.5;wave=math.sin(t*20*1.8) if shaking else math.sin(p*math.pi*4)
 arc=1 if shaking else math.sin(math.pi*min(1,max(0,p)))
 angles=[-28+arc*42,180+sign*wave*18,sign*(22+wave*25)+(0 if shaking else 180)]
 initial=[14 if shaking else -28,180,sign*22]
 # Convert Java XYZ rotations, then rotate about the bottle center, not the
 # player's shoulder. Centered item motion cannot displace the native arm.
 held=load(RP/'animations/a286_held.animation.json')['animations']['animation.kg_a286.bottle_fp_'+hand]['bones']['grip']
 conversion=scale([-1,-1,1]);delta=chain(conversion,xyz(angles),rigid_inverse(xyz(initial)),conversion)
 center=[0,21.25-24,0]
 local=chain(bone_matrix(held),translate(center),delta,translate([-v for v in center]))
 # Java translates +/- .08 m laterally and .10 m vertically during sprinkling.
 # Adapt those relative movements to the established visible Bedrock anchor.
 local[0][3]-=sign*wave*.08*16
 local[1][3]+=(arc-(1 if shaking else 0))*.10*16
 rot=bedrock_rotation(chain(local,scale([1/.72]*3)))
 return {'position':[-local[0][3],local[1][3],local[2][3]],'rotation':rot,'scale':[.72]*3}
def build():
 out={};controllers={};geometries=[];count=palette_size();rows=(count+7)//8
 placed=load(RP/'models/entity/a2770_placed/seasoning.geo.json')['minecraft:geometry']
 for tint in range(16):
  g=deepcopy(next(g for g in placed if g['description']['identifier']=='geometry.kg_a2770.pending_'+str(tint)))
  g['description']['identifier']='geometry.kg_seasoning.held_'+str(tint)
  b=g['bones'][0];b.update(name='grip',pivot=[0,24,0],binding='q.item_slot_to_bone_name(context.item_slot)')
  for cube in b['cubes']:cube['origin'][1]+=17
  geometries.append(g)
  slot=tint//2
  packed=f"(c.item_slot == 'off_hand' ? q.property('{NS}bottle_off_{slot}') : q.property('{NS}bottle_main_{slot}'))"
  index=f'math.floor({packed}/{count})' if tint%2==0 else f'math.mod({packed},{count})'
  controllers['controller.render.kg_seasoning.held_'+str(tint)]={'geometry':'Geometry.layer_'+str(tint),'materials':[{'*':'Material.contents'}],'textures':['Texture.layer_'+str(tint)],'uv_anim':{'scale':[1/8,1/rows],'offset':[f'math.mod({index},8)/8',f'math.floor({index}/8)/{rows}']}}
 out[RP/'models/entity/seasoning_held.geo.json']={'format_version':'1.16.0','minecraft:geometry':geometries}
 out[RP/'render_controllers/seasoning_held.render_controllers.json']={'format_version':'1.8.0','render_controllers':controllers}
 animations={}
 for hand in ['right','left']:
  for shaking in [False,True]:
   duration=2*math.pi/1.8/20 if shaking else .5
   samples=[duration*n/40 for n in range(41)] if shaking else [n/20 for n in range(11)]
   values={str(round(t,8)):motion(hand,t,shaking) for t in samples}
   bone={key:{t:row[key] for t,row in values.items()} for key in ['position','rotation']};bone['scale']=[.72]*3
   animations['animation.kg_seasoning.item.'+('shake' if shaking else 'sprinkle')+'.'+hand]={'loop':shaking,'animation_length':duration,'bones':{'grip':bone}}
 out[RP/'animations/seasoning_held.animation.json']={'format_version':'1.8.0','animations':animations}
 for p in (RP/'attachables').glob('*.json'):
  d=load(p);a=d['minecraft:attachable']['description'];identifier=a['identifier']
  if identifier not in [NS+'empty_seasoning_bottle',NS+'pending_seasoning'] and not identifier.startswith(NS+'special_seasoning'):continue
  pending=identifier==NS+'pending_seasoning';ids,selectors=dispatch(pending)
  a['animations']=ids;a['scripts']['animate']=[{k:v} for k,v in selectors.items()]
  if identifier in [NS+'empty_seasoning_bottle',NS+'pending_seasoning']:
   a['geometry'].pop('contents',None)
   a['render_controllers']=['controller.render.kg_a2733.seasoning_bottle_hand']
   for tint in range(16):
    a['geometry']['layer_'+str(tint)]='geometry.kg_seasoning.held_'+str(tint)
    a['textures']['layer_'+str(tint)]='textures/a2770_placed/pending_'+str(tint)
    fill=f"(c.item_slot == 'off_hand' ? q.property('{NS}bottle_off_fill') : q.property('{NS}bottle_main_fill'))"
    a['render_controllers'].append({'controller.render.kg_seasoning.held_'+str(tint):fill+' > '+str(tint//2)})
  out[p]=d
 # Authored third-person arm gestures must never move a first-person holder.
 for name,prefix in [('player_binding.animation.json','animation.kg_imm.player.season.'),('a21_shake.animation.json','animation.kg_a21.player.shake.')]:
  p=RP/'animations'/name;d=load(p)
  original=load(ROOT/'development/gameplay_core/fixtures/seasoning-arm-clips-2.8.55.json')[name]
  for key,seed in original.items():
   a=deepcopy(seed);d['animations'][key]=a
   a.pop('override_previous_animation',None);a['blend_weight']='!variable.is_first_person'
   if name=='player_binding.animation.json':
    a['animation_length']=.5
    for bone in a['bones'].values():
     bone.pop('position',None)
     for channel,v in list(bone.items()):
      if isinstance(v,dict):bone[channel]={str(round(float(t)*.5/.8,8)):row for t,row in v.items()}
  out[p]=d
 return out
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
 for p,d in build().items():
  text=json.dumps(d,ensure_ascii=False,indent=2)+'\n'
  if args.check:assert load(p)==d,str(p)
  else:
   p.parent.mkdir(parents=True,exist_ok=True)
   if p.name in ['player_binding.animation.json','a21_shake.animation.json']:text=text.replace('\n','\r\n')
   p.write_bytes(text.encode())
 print('Seasoning layers and bound-item Java 10-tick motion generated; client pending')
if __name__=='__main__':main()
