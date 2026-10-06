"""Verify reviewed author hooks and retained foreign oil routes, outside packaging."""
from pathlib import Path
import hashlib,json,os,subprocess,tempfile,urllib.request,zipfile
ROOT=Path(__file__).resolve().parents[1]
BP=ROOT/'projects/grilling/gameplay_core/behavior_pack'
def check():
 spec=json.loads((BP/'host-extensions/board-api.json').read_text())
 assert spec['host_uuid']=='5df753c9-3436-4fba-87f1-a2da3651cfcf' and spec['version']==[0,2,5]
 assert spec['archive_sha256']=='da12fe6d39d7514aff1de3c963d69899324d771be5ca0fc3da1ccb759c7ad458'
 with tempfile.TemporaryDirectory() as tmp:
  base=Path(tmp);archive=Path(os.environ['COOKERY_160_ARCHIVE']) if os.environ.get('COOKERY_160_ARCHIVE') else base/'author.mcaddon'
  if not archive.exists():
   with urllib.request.urlopen('https://edge.forgecdn.net/files/9054/164/Kaleidoscope%20Cookery%20v1.6.0.mcaddon',timeout=60) as response:archive.write_bytes(response.read())
  assert hashlib.sha256(archive.read_bytes()).hexdigest()==spec['archive_sha256']
  with zipfile.ZipFile(archive) as z:
   prefix='Kaleidoscope Cookery v1.6.0 [BP]/'
   originals={name:z.read(prefix+name) for name in spec['original_files']}
   original_oil_registry=z.read(prefix+'scripts/api/oilContainers.js')
  for name,raw in originals.items():
   assert hashlib.sha256(raw).hexdigest()==spec['original_files'][name],name
   text=spec['imports'].get(name,'')+raw.decode()
   if name.endswith('.json'):
    data=json.loads(text)
    for op in spec['json_updates']:
     if op['path']==name:
      assert op['pointer']==['minecraft:item','components','minecraft:allow_off_hand'] and op['value'] is True
      assert 'minecraft:allow_off_hand' not in data['minecraft:item']['components'];data['minecraft:item']['components']['minecraft:allow_off_hand']=True
    text=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
   for op in spec['insertions']:
    if op['path']==name:
     assert text.count(op['anchor'])==1; text=text.replace(op['anchor'],op['text']+op['anchor'] if op['position']=='before' else op['anchor']+op['text'])
   assert hashlib.sha256(text.encode()).hexdigest()==spec['patched_files'][name],name
   if name.endswith('.js'):
    p=base/(Path(name).stem+'.mjs');p.write_text(text);subprocess.run(['node','--check',str(p)],check=True)
   if name.endswith('/oilPot.js'):
    start=text.index('export function consumeOilFromHeldContainer(player){')
    body=text[start:].split('// Backward-compatible private alias',1)[0]
    # Actual adapted author function + actual generic author registry; no owned
    # registry substitute and no in-game/simulated player acceptance claimed.
    registry=original_oil_registry.decode().replace('import { EquipmentSlot, GameMode, ItemStack } from "@minecraft/server";','')
    fixture="""import assert from 'node:assert/strict';
const EquipmentSlot={Mainhand:'Mainhand'},GameMode={Creative:'Creative'},FILLED_POT='kaleidoscope_cookery:oil_pot_filled';
class ItemStack {constructor(typeId,amount){this.typeId=typeId;this.amount=amount;this.data={}}getDynamicProperty(k){return this.data[k]}setDynamicProperty(k,v){this.data[k]=v}}
let sharedCalls=0;const consumeSharedOilFromHeldPot=()=>{sharedCalls++;return true};const slot=p=>p.getComponent('minecraft:equippable').getEquipmentSlot('Mainhand');
"""+registry+'\n'+body+"""
const hand={item:new ItemStack('external:oil_can',1),hasItem(){return !!this.item},getItem(){return this.item},setItem(i){this.item=i}};
const owner={getComponent:()=>({getEquipmentSlot:()=>hand}),getGameMode:()=> 'Survival'};
assert.equal(registerOilContainer({api:1,source:'external',container:{id:'external:oil_can',empty:'external:empty_can',oil:'external:oil',capacity:3,defaultAmount:3,amountProperty:'external:amount'}}).ok,true);
for(const expected of [2,1]){assert.equal(consumeOilFromHeldContainer(owner),true);assert.equal(hand.item.typeId,'external:oil_can');assert.equal(readRegisteredOilAmount(hand.item),expected)}
assert.equal(consumeOilFromHeldContainer(owner),true);assert.equal(hand.item.typeId,'external:empty_can');assert.equal(sharedCalls,0);
hand.item=new ItemStack(FILLED_POT,1);assert.equal(consumeOilFromHeldContainer(owner),true);assert.equal(sharedCalls,1);
console.log('Cookery 1.6.0 original foreign container route/debit/empty remainder and shared author can dispatch PASS');
"""
    p=base/'foreign-oil.mjs';p.write_text(fixture);subprocess.run(['node',str(p)],check=True)
  print('All eight reviewed 1.6.0 targets, syntax and scoped oil adapter PASS; native/client gates remain separate')
if __name__=='__main__':check()
