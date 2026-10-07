/** Native G84 proved cap10 rejects target12.353846; this is source/transaction coverage. */
import assert from 'node:assert/strict';import fs from 'node:fs';import vm from 'node:vm';import {execFileSync} from 'node:child_process';
import {canonicalFoodId} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/eating_profile_ids.js';
import {captureEatingIdentity,commitEating} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a285_eating_transaction.js';
import {completedUseStillCurrent} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2810_use_transaction.js';
const path='projects/grilling/gameplay_core/behavior_pack/scripts/main.js',source=fs.readFileSync(path,'utf8'),N='kaleidoscope_grilling:',PLATE=N+'skewer_plate',SECRET=N+'secret_skewer';
function body(text,name){const start=text.indexOf('function '+name+'(');let end=text.indexOf('{',start)+1,depth=1;while(depth){const c=text[end++];if(c==='{')depth++;if(c==='}')depth--;}return text.slice(start,end);}
class Stack{constructor(typeId){this.typeId=typeId;this.amount=1;this.maxAmount=1;this.props={};}clone(){return Object.assign(new Stack(this.typeId),structuredClone({...this}));}getRawLore(){return [];}getDynamicPropertyIds(){return Object.keys(this.props);}getDynamicProperty(k){return this.props[k];}}
function fixture({script=source,id=SECRET,mode='fixed10',failure=''}={}){
 let saturationValue=10,hand,bowls=0,finish=0,reject=failure==='setter';const writes=[],plate=new Stack(PLATE),sessions=new Map();
 const h={currentValue:10,effectiveMax:20,setCurrentValue(v){if(v<0||v>20)throw Error('hunger bounds');this.currentValue=v;}};
 function satView(){const cap=mode==='fresh13'?h.currentValue:10;return {effectiveMax:cap,get currentValue(){return saturationValue;},setCurrentValue(v){writes.push({value:v,cap});if(reject){reject=false;throw Error('injected native write');}if(!Number.isFinite(v)||v<0||v>cap)throw Object.assign(new Error('native saturation bounds'),{name:'ArgumentOutOfBoundsError'});saturationValue=Math.fround(v);}};}
 const player={id:'fixture',selectedSlotIndex:3,getComponent(id){if(id.endsWith('hunger'))return h;if(h.currentValue===13&&failure==='refresh_missing')return undefined;if(h.currentValue===13&&failure==='refresh_throw')throw Error('fresh component unavailable');return satView();}};
 sessions.set(player.id,{plate:plate.clone(),hand:'main',use:captureEatingIdentity(plate,'main',3)});
 const ctx=vm.createContext({plateQaTrace(){},PLATE_EATS:sessions,completedUseStillCurrent,heldByHand:()=>hand,creative:()=>false,mainContainer:()=>({setItem(_slot,s){hand=s;}}),commitEating,
 dynamicFood:()=>({nutrition:3,saturation:.3923076923076923}),grillingConfig:()=>({saturationMultiplier:1.25}),a25PlateRows:()=>[{id}],plateHighestNutritionIndex:r=>r.length?0:-1,a25RestoreStack:r=>new Stack(r.id),primitiveStackProps:s=>s.props,
 stackMeta:()=>({hot:false}),a25PlateItem(){throw Error('unexpected second serving');},canonicalFoodId,SECRET_ID:SECRET,RAW_NAUSEA:{},MYSTERIOUS_ID:'m',DARK_ID:'d',dangerousPreservation(){},secretRemainders(){bowls++;},afterCommitted(){finish++;},console:{warn(){}}});
 vm.runInContext(['writeUseHand','addSecretNutrition','addNestedNutrition','completePlateUse'].map(name=>body(script,name)).join('\n'),ctx);
 return {run:()=>ctx.completePlateUse(player,plate.clone()),writes,h,get saturation(){return saturationValue;},get hand(){return hand;},get bowls(){return bowls;},get finish(){return finish;}};
}
let cases=0;
for(const id of [SECRET,SECRET+'_java_three_alt',SECRET+'_native_plain'])for(const mode of ['fixed10','fresh13']){
 const f=fixture({id,mode});f.run();assert.equal(f.hand,undefined);assert.equal(f.h.currentValue,13);assert.equal(f.saturation,mode==='fixed10'?10:Math.fround(12.353846153846154));assert.equal(f.bowls,1);assert.equal(f.finish,1);assert(f.writes.every(x=>x.value<=x.cap));f.run();assert.equal(f.bowls,1);assert.equal(f.finish,1);cases++;
}
for(const failure of ['refresh_missing','refresh_throw','setter']){const f=fixture({failure});f.run();assert.equal(f.hand.typeId,PLATE);assert.equal(f.h.currentValue,10);assert.equal(f.saturation,10);assert.equal(f.bowls,0);assert.equal(f.finish,0);cases++;}
const d=JSON.parse(fs.readFileSync('tools/fixtures/g85-main-reviewed-delta.json','utf8')),old=execFileSync('git',['show',d.base_commit+':'+path],{encoding:'utf8'});
for(const id of [SECRET,SECRET+'_java_three_alt',SECRET+'_native_plain']){const f=fixture({script:old,id});f.run();assert.equal(f.hand.typeId,PLATE);assert.equal(f.h.currentValue,10);assert.equal(f.saturation,10);assert.equal(f.bowls,0);assert(f.writes.some(x=>x.value>x.cap));cases++;}
console.log(`Native saturation bounds: ${cases} fixed/fresh cap, alias completion, rollback and exact G84 counterfactual scenarios PASS`);
