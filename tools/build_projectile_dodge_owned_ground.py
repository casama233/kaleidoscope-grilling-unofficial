"""Finite authored geometry/property source proof; never a generic solid guess."""
import argparse
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/'development/gameplay_core/fixtures/java-projectile-dodge-owned-ground.json'
OUTPUT=ROOT/'projects/grilling/gameplay_core/behavior_pack/scripts/projectile_dodge_owned_ground_catalog.js'

def decision(flags,box,threshold):
 if flags['forceSolidOn']:return True
 if flags['forceSolidOff'] or flags['dynamicShape'] or not flags['hasCollision']:return False
 if not box:return False
 width,height,depth=[(box[i+3]-box[i])/16 for i in range(3)]
 return (width+height+depth)/3>=threshold or height>=1

def build():
 data=json.loads(FIXTURE.read_text());rows=data['rows']
 if data['schema']!=1 or data['limitations']['actual_author_blocksMotion_invoked'] is not False:raise ValueError('Keep derived source proof distinct from an executed author registry')
 if len(rows)!=20 or [r['id'] for r in rows]!=sorted({r['id'] for r in rows}):raise ValueError('Unique complete current qualified identity list required')
 out=[]
 for row in rows:
  role=row['role'];proof=row['native_default_observation']
  if proof['type_id']!=row['id'] or sorted(proof['states'])!=sorted(row['states']):raise ValueError('Native identity/key witness differs')
  for key,values in row['states'].items():
   if not values or len({type(x) for x in values})!=1 or any(type(x) not in [int,bool,str] for x in values):raise ValueError('Exact typed domains required')
   if type(proof['states'][key]) is not type(values[0]) or proof['states'][key] not in values:raise ValueError('Native default out of typed source domain')
  decisions=[]
  for version in ['1.20.1','1.21.1']:
   if role.endswith('_oil'):flags=data['fluid_flags_by_branch'][version];boxes=[[]]
   else:
    flags=data['property_flags_by_branch'][version][role]
    if role=='seasoning_bottle':boxes=[data['bottle_bounds_by_count'][row['id'].rsplit('_',1)[1]]]
    else:boxes=data['collision_bounds_in_sixteenths'].get(role,[[]])
   if set(flags)!={'hasCollision','forceSolidOn','forceSolidOff','dynamicShape'} or any(type(v) is not bool for v in flags.values()):raise ValueError('Original flag readback must retain boolean types')
   outcomes={decision(flags,box,data['source_threshold']) for box in boxes}
   if outcomes!={row['motion']}:raise ValueError('Authored predicate proof disagrees: '+row['id']+' '+version)
   decisions.append(row['motion'])
  if len(set(decisions))!=1:raise ValueError('Loader branch discrepancy requires an explicit profile')
  out.append({'typeId':row['id'],'blocksMotion':row['motion'],'states':row['states'],'sourceKind':row['source_kind']})
 text='// Generated current author-source/property proof; not an executed author registry or collision-equivalence claim.\n'
 text+="function freeze(v){if(v&&typeof v==='object'){for(const child of Object.values(v))freeze(child);Object.freeze(v)}return v}\n"
 text+='export const PROJECTILE_DODGE_OWNED_GROUND_ROWS=freeze('+json.dumps(out,separators=(',',':'))+');\n'
 return text

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args();text=build()
 if args.check:
  if OUTPUT.read_text()!=text:raise SystemExit('Owned ground catalog differs from proof')
 else:OUTPUT.write_text(text)
 print('20 finite current-author ground rules; original vanilla source facts remain separate')
if __name__=='__main__':main()
