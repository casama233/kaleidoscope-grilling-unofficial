"""Reproducible held-item motion from reviewed Java Catmull-Rom curves.

Uses a local first-person motion bone atop the reviewed hand frames. Native
Bedrock arm animation and Java's detached second-piece rendering differ; this
conversion does not certify the client presentation.
"""
from pathlib import Path
import json,math,re,argparse,sys
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'projects/grilling/gameplay_core';RP=P/'resource_pack';BP=P/'behavior_pack'
FIX=ROOT/'development/gameplay_core/fixtures/java-eating-curves-1.1.1.json'
ACTIVE_HAND="(q.is_using_item && ((c.item_slot == 'main_hand' && q.property('kaleidoscope_grilling:eat_hand') == 1) || (c.item_slot == 'off_hand' && q.property('kaleidoscope_grilling:eat_hand') == 2)))"
def sample(times,values,t):
 if t<=times[0]:return values[0]
 if t>=times[-1]:return values[-1]
 right=next(i for i,x in enumerate(times) if x>=t);left=right-1;u=(t-times[left])/(times[right]-times[left]);p0,p1,p2,p3=[values[i] for i in [max(0,left-1),left,right,min(len(times)-1,right+1)]]
 return .5*((2*p1)+(-p0+p2)*u+(2*p0-5*p1+4*p2-p3)*u*u+(-p0+3*p1-3*p2+p3)*u*u*u)
def curves(profile):
 source=json.loads(FIX.read_text())['files'];sk=source['SkewerEatingAnimation.java']['arrays'];pearl=source['EnderPearlEatingAnimation.java']['arrays']
 if profile=='ONE':return pearl,'ONE_RIGHT_TIMES','ONE_RIGHT_', 'ONE_RIGHT_TIMES','ONE_RIGHT_ROT_'
 if profile=='THREE':return pearl,'RIGHT_POSITION_TIMES','RIGHT_POSITION_','RIGHT_ROTATION_TIMES','RIGHT_ROTATION_'
 prefix={'TWO':'TWO_','THREE_ALT':'SQUID_','FOUR':''}[profile]
 return sk,prefix+'POSITION_TIMES',prefix+'POSITION_',prefix+'ROTATION_TIMES',prefix+'ROTATION_'
def animation_id(profile,hand):return 'animation.kg_eating.item.'+profile.lower()+'.'+hand
def build():
 modern=tuple(json.loads((BP/'manifest.json').read_text())['header']['version']) >= (2,8,58)
 sys.path.insert(0,str(ROOT/'development/gameplay_core'))
 from native_eating_clock import SECONDS,VARIABLE,ASSIGNMENT
 animations={};profiles=['ONE','TWO','THREE','THREE_ALT','FOUR']
 for profile in profiles:
  a,pt,prefix,rt,rprefix=curves(profile);duration=5 if profile=='THREE' else 4.5
  for hand in ['right','left']:
   sign=1 if hand=='right' else -1;position={};rotation={}
   for n in range(round(duration*20)+1):
    t=n/20;pos=[sample(a[pt],a[prefix+c],t)-a[prefix+c][0] for c in 'XYZ'];rot=[sample(a[rt],a[rprefix+c],t)-a[rprefix+c][0] for c in 'XYZ']
    # Source curve displacement, mirrored across the already bound hand rig.
    position[f'{t:.2f}']=[round(-pos[0]*sign,6),round(-pos[1],6),round(pos[2],6)]
    rotation[f'{t:.2f}']=[round(rot[0],6),round(-rot[1]*sign,6),round(rot[2]*sign,6)]
   animations[animation_id(profile,hand)]={'loop':'hold_on_last_frame','animation_length':duration,'anim_time_update':SECONDS if modern else 'q.item_in_use_duration','bones':{'skewer_model':{'position':position,'rotation':rotation}}}
 output={RP/'animations/eating_motion.animation.json':{'format_version':'1.8.0','animations':animations}}
 table=json.loads(re.search(r'PROFILE_BY_ITEM=Object.freeze\((\{.*?\})\)',(BP/'scripts/data.js').read_text()).group(1))
 for p in (RP/'attachables').glob('*.json'):
  doc=json.loads(p.read_text());d=doc['minecraft:attachable']['description'];profile=table.get(d['identifier']);
  if d['identifier']=='kaleidoscope_grilling:secret_skewer':profile='THREE_RANDOM'
  if not profile or not d['identifier'].endswith('_skewer'):continue
  d['scripts']['pre_animation']=[row.replace(VARIABLE,'q.item_in_use_duration') for row in d['scripts']['pre_animation'] if not row.startswith(VARIABLE+' =')]
  for hand in ['right','left']:
   alias='eat_'+hand;d['animations'][alias]=animation_id('THREE' if profile=='THREE_RANDOM' else profile,hand)
   if profile=='THREE_RANDOM':d['animations']['eat_alt_'+hand]=animation_id('THREE_ALT',hand)
  animate=[row for row in d['scripts']['animate'] if not any(str(k).startswith('eat_') for k in row)]
  for hand in ['right','left']:
   # ItemInHandSkewerEatingMixin replaces renderArmWithItem, an FP renderer.
   # Its camera-space arm displacements are not TP item-local transforms.
   using="c.is_first_person == 1 && q.is_using_item && q.property('kaleidoscope_grilling:eat_hand') == "+str(1 if hand=='right' else 2)+" && c.item_slot == '"+('main_hand' if hand=='right' else 'off_hand')+"'"
   if profile=='THREE_RANDOM':
    alternate="q.property('kaleidoscope_grilling:eat_profile') == 4"
    animate += [{'eat_'+hand:using+" && q.property('kaleidoscope_grilling:eat_profile') != 4"},{'eat_alt_'+hand:using+' && '+alternate}]
   else:animate.append({'eat_'+hand:using})
  if profile=='THREE_RANDOM':
   first="q.item_in_use_duration >= 0.95833 ? 1 : 0"
   normal="q.item_in_use_duration >= 3.54167 ? 3 : (q.item_in_use_duration >= 2.33333 ? 2 : ("+first+"))"
   alt="q.item_in_use_duration >= 3.5 ? 3 : (q.item_in_use_duration >= 2.16667 ? 2 : ("+first+"))"
   d['scripts']['pre_animation']=["v.kg_bite_stage = q.is_using_item ? (q.property('kaleidoscope_grilling:eat_profile') == 4 ? ("+alt+") : ("+normal+")) : 0;"]
  d['scripts']['pre_animation']=[row.replace(ACTIVE_HAND,'q.is_using_item').replace('q.is_using_item',ACTIVE_HAND) for row in d['scripts']['pre_animation']]
  if modern:d['scripts']['pre_animation']=[ASSIGNMENT]+[row.replace('q.item_in_use_duration',VARIABLE) for row in d['scripts']['pre_animation']]
  d['scripts']['animate']=animate;output[p]=doc
 if tuple(json.loads((BP/'manifest.json').read_text())['header']['version']) >= (2,8,58):
  sys.path.insert(0,str(ROOT/'tools'))
  from build_java_eating_projection import augment
  output=augment(output,table)
 return output
def mismatch_details(expected, actual, limit=20):
 """Bounded diagnostics only; the full byte-for-byte check remains authoritative."""
 def walk(a,b,pointer=''):
  if type(a) is not type(b):
   yield pointer,a,b
  elif isinstance(a,dict):
   for key in dict.fromkeys([*a,*b]):
    escaped=str(key).replace('~','~0').replace('/','~1')
    if key not in a or key not in b:yield pointer+'/'+escaped,a.get(key),b.get(key)
    else:yield from walk(a[key],b[key],pointer+'/'+escaped)
  elif isinstance(a,list):
   if len(a)!=len(b):yield pointer+'/length',len(a),len(b)
   for i,(x,y) in enumerate(zip(a,b)):yield from walk(x,y,pointer+'/'+str(i))
  elif repr(a)!=repr(b):yield pointer,a,b
 try:
  from itertools import islice
  rows=list(islice(walk(json.loads(expected),json.loads(actual)),limit))
 except (ValueError,TypeError):rows=[]
 if not rows:return 'Serialized text differs (including whitespace); no structural difference found'
 lines=[]
 for pointer,a,b in rows:
  kind='value'
  if isinstance(a,(int,float)) and isinstance(b,(int,float)):
   if a==b==0:kind='signed zero'
   elif abs(a-b)==360:kind='360-degree representative'
  lines.append(f'{pointer}: committed={a!r}; generated={b!r} ({kind})')
 return '\n'.join(lines)
def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
 for path,value in build().items():
  data=value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2)+'\n'
  if args.check:
   existing=path.read_text()
   assert existing==data,f'{path}\n{mismatch_details(existing,data)}'
  else:path.write_text(data)
 print('Authored eating item motion: five profiles, both hands; client acceptance false')
if __name__=='__main__':main()
