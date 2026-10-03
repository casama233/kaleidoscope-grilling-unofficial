"""Append owned groups/properties to a hash-pinned, unchanged Mojang player.

No RP player replacement. The family must reject competing BP player definitions.
"""
from pathlib import Path
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/'development/gameplay_core/fixtures/vanilla-player-1.26.30.json'
TARGET=ROOT/'projects/grilling/gameplay_core/behavior_pack/entities/player.json'
PREFIX='kaleidoscope_grilling:'
def build():
 source=json.loads(FIX.with_suffix('.source.json').read_text())
 assert hashlib.sha256(FIX.read_bytes()).hexdigest()==source['sha256']
 doc=json.loads(FIX.read_text());entity=doc['minecraft:entity']
 props=entity['description'].setdefault('properties',{})
 props[PREFIX+'eat_profile']={'type':'int','range':[0,5],'default':0,'client_sync':True}
 props[PREFIX+'eat_hand']={'type':'int','range':[0,2],'default':0,'client_sync':True}
 if tuple(json.loads((ROOT/'baseline.json').read_text())['version']) >= (2,8,58):
  props[PREFIX+'eat_projection']={'type':'bool','default':False,'client_sync':True}
  props[PREFIX+'eat_native_ticks']={'type':'int','range':[0,72000],'default':0,'client_sync':True}
  props[PREFIX+'eat_elapsed_ticks']={'type':'int','range':[0,72000],'default':0,'client_sync':True}
 for hand in ['main','off']:
  for slot in range(3):props[PREFIX+'secret_'+hand+'_'+str(slot)]={'type':'int','range':[0,255],'default':0,'client_sync':True}
 if tuple(json.loads((ROOT/'baseline.json').read_text())['version']) >= (2,8,61):
  for hand in ['main','off']:
   for slot in range(8):props[PREFIX+'bottle_'+hand+'_'+str(slot)]={'type':'int','range':[0,9],'default':0,'client_sync':True}
 assert len(props)<=32,'Player client property limit exceeded'
 groups=entity.setdefault('component_groups',{});events=entity.setdefault('events',{})
 ids=[PREFIX+'dragon_health_'+str(i) for i in range(3)]
 for i,maximum in enumerate([20,26,30]):
  assert ids[i] not in groups and ids[i] not in events
  groups[ids[i]]={'minecraft:health':{'value':maximum,'max':maximum}}
  events[ids[i]]={'sequence':[{'remove':{'component_groups':ids}},{'add':{'component_groups':[ids[i]]}}]}
 return doc
def check_preserved(doc):
 expected=json.loads(FIX.read_text());stripped=json.loads(json.dumps(doc));entity=stripped['minecraft:entity']
 for key in list(entity['description'].get('properties',{})):
  if key.startswith(PREFIX):del entity['description']['properties'][key]
 if not entity['description'].get('properties') and 'properties' not in expected['minecraft:entity']['description']:entity['description'].pop('properties',None)
 for section in ['component_groups','events']:
  for key in list(entity[section]):
   if key.startswith(PREFIX):del entity[section][key]
 assert stripped==expected,'Native player definition changed beyond owned extensions'
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
 doc=build();check_preserved(doc);data=json.dumps(doc,ensure_ascii=False,indent=2)+'\n'
 if args.check:assert TARGET.read_text()==data
 else:TARGET.parent.mkdir(exist_ok=True);TARGET.write_text(data)
 print('Pinned native player preserved; owned health groups and shared eating property only')
if __name__=='__main__':main()
