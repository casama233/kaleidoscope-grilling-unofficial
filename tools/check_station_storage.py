#!/usr/bin/env python3
"""Read-only wiring/resource assertions, not a simulated container or player test."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
BP=R/'projects/grilling/gameplay_core/behavior_pack';RP=R/'projects/grilling/gameplay_core/resource_pack'
def load(p):return json.loads(p.read_text())
for block,suffix,size in [('grill','grill',3),('advanced_rack_block','rack',9)]:
 b=load(BP/f'blocks/{block}.json')['minecraft:block']
 assert 'minecraft:block_entity' not in b['components']
 e=load(BP/f'entities/family_inventory_{suffix}.json')['minecraft:entity']
 assert e['description']['identifier']==f'kaleidoscope_grilling:inventory_{suffix}_v1'
 c=e['components'];assert 'minecraft:persistent' in c
 assert c['minecraft:inventory']=={'inventory_size':size,'container_type':'inventory','private':True,'restrict_to_owner':True,'can_be_siphoned_from':False}
 assert c['minecraft:damage_sensor']['triggers'][0]['deals_damage']=='no'
 assert not c['minecraft:physics']['has_gravity'] and not c['minecraft:physics']['has_collision']
 rc=load(RP/f'entity/family_inventory_{suffix}.entity.json')['minecraft:client_entity']['description']
 assert rc['identifier']==e['description']['identifier']
for name in ['family_station_storage.js','a2740_grill_state_adapter.js','a2746_rack_state_adapter.js','a2746_advanced_rack_runtime.js']:
 assert (BP/'scripts'/name).read_bytes()==(R/'development/gameplay_core'/name).read_bytes(),name
text=(BP/'scripts/family_station_storage.js').read_text()
assert 'kc_station' not in text and 'kc_oilpot' not in text
assert 'linked inventory is unavailable; contents not reset' in text and 'refusing to retire nonempty inventory' in text
assert 'Object.hasOwn(STORAGE_TYPES,r.block)' in text and 'transaction quarantined' in text
assert 'encodeRackStack' not in text and 'encodeRackPayload' not in text,'Backing must keep native ItemStacks'
assert "function inv(block){return stationContainer(block)}" in (BP/'scripts/main.js').read_text()
assert "throw new Error('Grill inventory unavailable; ticking paused')" in (BP/'scripts/a2740_grill_state_adapter.js').read_text()
assert 'Packed rack payload was not saved' in (BP/'scripts/a2746_advanced_rack_runtime.js').read_text()
print('PASS: stable inventory wiring, two native helper resources, metadata ownership and fail-closed source guards. Not a native/client test.')
