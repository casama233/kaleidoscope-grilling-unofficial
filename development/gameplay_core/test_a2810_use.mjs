import {seasoningLore} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/localized_lore_core.js';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {setItemProperty,setItemLore} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/itemDataCore.js';
import {execFileSync} from 'node:child_process';
import {captureEatingIdentity,commitEating} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a285_eating_transaction.js';
import {completedUseStillCurrent} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2810_use_transaction.js';
const path='projects/grilling/gameplay_core/behavior_pack/scripts/main.js';
const source=fs.readFileSync(path,'utf8');
const plateId='kaleidoscope_grilling:skewer_plate',pendingId='kaleidoscope_grilling:pending_seasoning';
class Stack{
 constructor(id,amount=1){this.typeId=id;this.amount=amount;this.maxAmount=1;this.props={};this.lore=[];this.rows=[];this.list=[];this.nameTag='';}
 clone(){const s=new Stack(this.typeId,this.amount);Object.assign(s,JSON.parse(JSON.stringify(this)));return s;}
 getRawLore(){return this.lore.map(text=>({text}));}getLore(){return this.lore;} setLore(v){this.lore=v;}
 getDynamicPropertyIds(){return Object.keys(this.props);}getDynamicProperty(k){return this.props[k];}setDynamicProperty(k,v){this.props[k]=v;}
}
function fixture({hand='main',consumed=true,creative=false,failure,selected=3,script=source}={}){
 const plate=new Stack(plateId);plate.rows=[{id:'test:food',props:{ingredients:'apple'}},{id:'test:second',props:{}}];plate.props.rows=JSON.stringify(plate.rows);
 const pending=new Stack(pendingId);pending.list=['pepper','onion','chili'];pending.props.ingredients=JSON.stringify(pending.list);
 const slots=new Map([[3,consumed?undefined:plate.clone()]]);let off=hand==='off'?(consumed?undefined:plate.clone()):undefined,awards=0,effects=0;
 const hunger={currentValue:10,setCurrentValue(v){this.currentValue=v;}},sat={currentValue:2,setCurrentValue(v){this.currentValue=v;}};
 const write=(h,v,slot=player.selectedSlotIndex)=>{if(failure==='debit'&&v?.typeId===plateId&&v.rows.length===1)throw Error('write rejected');if(failure==='pendingWrite'&&v?.typeId==='test:filled')throw Error('write rejected');if(h==='off')off=v;else slots.set(slot,v);};
 const player={id:'p',selectedSlotIndex:selected,creative,getComponent(id){return id.endsWith('hunger')?hunger:id.endsWith('saturation')?sat:id.endsWith('equippable')?{setEquipment(_,v){write('off',v);return true;}}:null;}};
 const active={plate:plate.clone(),stack:pending.clone(),hand,use:captureEatingIdentity(plate,hand,3)};
 const plateMap=new Map([['p',active]]),pendingMap=new Map();
 const context={seasoningLore,setItemProperty,setItemLore,PLATE_EATS:plateMap,PENDING_USES:pendingMap,completedUseStillCurrent,commitEating,stopSoundHandle(){},seasoningFinished(){},
 heldByHand:(_,h)=>h==='off'?off:slots.get(player.selectedSlotIndex),creative:p=>p.creative,mainContainer:()=>({setItem(slot,v){write('main',v,slot);}}),EquipmentSlot:{Offhand:'off'},
 a25PlateRows:s=>structuredClone(s.rows),plateHighestNutritionIndex:r=>r.length?0:-1,
 a25RestoreStack:r=>{if(failure==='restore')return undefined;const s=new Stack(r.id);s.props=failure==='metadata'?{}:{...r.props};return s;},
 primitiveStackProps:s=>s.props,
 a25PlateItem:(rows,p)=>{const s=p.clone();if(failure!=='plateData'){s.rows=rows;s.props.rows=JSON.stringify(rows);}return s;},stackMeta:()=>({hot:false,seasonings:[]}),
 addNestedNutrition(){hunger.currentValue+=4;sat.currentValue+=3;if(failure==='reward')throw Error('nutrition rejected');},dangerousPreservation(){effects++;},RAW_NAUSEA:{},MYSTERIOUS_ID:'m',DARK_ID:'d',SECRET_ID:'secret',
 secretRemainders(){effects++;},afterCommitted(){effects++;},console:{warn(){}},setHand:(_,h,v)=>write(h,v),
 ItemStack:Stack,readSeasonings:s=>s.list,setSeasonings:(s,v)=>{if(failure!=='seasonData')s.list=v;},setUses(){},getUses:()=>0,hasSeasoningBase:()=>true,message(){},specialSeasoningVisualId:()=> 'test:filled',SEASONING_VARIANT_MAX:7,SEASON_VARIANT_KEY:'variant',SEASONING_MAX_USES:16,SEASONING_CAPACITY:8,PENDING_SEASONING:pendingId,handFor:()=>({name:'main'}),awardSeasoningFinishedChallenges(){awards++;}};
 const text=script.slice(script.indexOf('function '+(script.includes('function writeUseHand')?'writeUseHand':'completePlateUse')+'('),script.indexOf('world.afterEvents.itemStartUse.subscribe'));
 vm.createContext(context);vm.runInContext(text,context);
 return {player,plate,pending,active,plateMap,pendingMap,context,hunger,sat,slots,get off(){return off;},get effects(){return effects;},get awards(){return awards;},usePlate(){context.completePlateUse(player,plate.clone());},
 usePending(){context.completePending(player,pending.clone());},setPending(){if(hand==='off')off=pending.clone();else slots.set(3,pending.clone());pendingMap.set('p',{stack:pending.clone(),hand,use:captureEatingIdentity(pending,hand,3)});}};
}
// Reproduce the two defects in the actual previous completion handlers.
const baseline=execFileSync('git',['show',(process.env.GRILLING_USE_BASE??'7ef78bb360ac6a34664a15deef2c2aff5cc3d719')+':'+path],{encoding:'utf8'});
const old=fixture({script:baseline,consumed:false,selected:4});old.slots.set(4,new Stack('test:unrelated'));old.usePlate();assert.equal(old.hunger.currentValue,14);assert.equal(old.slots.get(4).typeId,plateId);
const oldFail=fixture({script:baseline,failure:'debit'});assert.throws(()=>oldFail.usePlate());assert.equal(oldFail.hunger.currentValue,14);
let cases=2;
for(const hand of ['main','off'])for(const creative of [false,true]){
 const f=fixture({hand,creative,consumed:!creative});f.usePlate();const out=hand==='off'?f.off:f.slots.get(3);
 assert.equal(out.rows.length,1);assert.equal(f.hunger.currentValue,14);assert.equal(f.effects,2);
 f.usePlate();assert.equal(f.hunger.currentValue,14);assert.equal(out.rows.length,1);cases++;
}
for(const failure of ['debit','reward','restore','metadata','plateData'])for(const hand of ['main','off']){
 const f=fixture({hand,failure});f.usePlate();assert.equal(f.hunger.currentValue,10);assert.equal(f.sat.currentValue,2);assert.equal(f.effects,0);
 assert.equal((hand==='off'?f.off:f.slots.get(3)).rows.length,2);cases++;
}
for(const selected of [3,4]){
 const f=fixture({consumed:false,selected});const replacement=new Stack('test:unrelated');f.slots.set(selected,replacement);f.usePlate();assert.equal(f.slots.get(selected),replacement);assert.equal(f.effects,0);assert.equal(f.hunger.currentValue,10);cases++;
}
const changed=fixture({consumed:false});changed.slots.get(3).props.rows='different plate';changed.usePlate();assert.equal(changed.hunger.currentValue,10);cases++;
for(const hand of ['main','off']){
 const f=fixture({hand});f.setPending();f.usePending();assert.equal((hand==='off'?f.off:f.slots.get(3)).typeId,'test:filled');assert.equal(f.awards,1);f.usePending();assert.equal(f.awards,1);cases++;
}
for(const failure of ['pendingWrite','seasonData']){
 const f=fixture({failure});f.setPending();if(failure==='seasonData')assert.throws(()=>f.usePending());else f.usePending();assert.equal(f.slots.get(3).typeId,pendingId);assert.equal(f.awards,0);cases++;
}
for(const mutation of ['slot','differentContents','empty','missingStart']){
 const f=fixture();f.setPending();if(mutation==='slot')f.player.selectedSlotIndex=4;
 if(mutation==='differentContents')f.slots.get(3).props.ingredients='poison';if(mutation==='empty')f.slots.delete(3);if(mutation==='missingStart')f.pendingMap.clear();
 f.usePending();assert.equal(f.awards,0);assert.notEqual(f.slots.get(3)?.typeId,'test:filled');cases++;
}
const p=new Stack(plateId),use=captureEatingIdentity(p,'main',3);
assert(completedUseStillCurrent(use,p,undefined,3,true));assert(!completedUseStillCurrent(use,p,undefined,4,true));assert(!completedUseStillCurrent(use,p,undefined,3,false));assert(!completedUseStillCurrent(null,p,p,3,true));cases+=4;
console.log(`A2810: ${cases} completion/rollback regression scenarios PASS (actual handlers; no client event simulation)`);
