/** Actual completion body with item/storage doubles; no Minecraft players. */
import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import vm from 'node:vm';
import {captureEatingIdentity,commitEating} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a285_eating_transaction.js';
import {completedUseStillCurrent} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2810_use_transaction.js';
import {stopSoundHandle} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/immersion_audio_core.js';
import {configureItemDataWorld} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/itemDataCore.js';
configureItemDataWorld({getDynamicProperty(){},setDynamicProperty(){}});
class Stack{constructor(typeId,amount=1){this.typeId=typeId;this.amount=amount;this.nameTag='';this.lore=[]}getRawLore(){return this.lore}setLore(lore){this.lore=lore}clone(){return Object.assign(new Stack(this.typeId,this.amount),structuredClone({...this}))}}
const source=fs.readFileSync(new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/main.js',import.meta.url),'utf8');
const body=source.slice(source.indexOf('function completePending('),source.indexOf('world.afterEvents.itemStartUse.subscribe'));
function fixture(fail=false){
 const uses=new Map(),holder={id:'use-owner',selectedSlotIndex:0},original=new Stack('pending');let held=original.clone(),stops=0,successes=0,awards=0,writes=0;
 const active={use:captureEatingIdentity(original,'main',0),hand:'main',stack:original.clone(),audio:{stop(){stops++}}};uses.set(holder.id,active);
 const ctx=vm.createContext({ItemStack:Stack,PENDING_USES:uses,completedUseStillCurrent,heldByHand:()=>held,stopSoundHandle,readSeasonings:s=>s.ingredients??['base'],hasSeasoningBase:()=>true,SEASONING_VARIANT_MAX:0,SEASONING_MAX_USES:16,SEASONING_CAPACITY:5,SEASON_VARIANT_KEY:'variant',specialSeasoningVisualId:()=> 'finished',setSeasonings:(s,list)=>s.ingredients=list,setUses:(s,n)=>s.uses=n,getUses:s=>s.uses,setItemProperty(){},setItemLore:(s,l)=>s.setLore(l),commitEating,writeUseHand:(_p,_use,next)=>{held=next;writes++;if(fail&&writes===1)throw Error('injected write')},seasoningFinished:()=>successes++,awardSeasoningFinishedChallenges:()=>awards++,message(){}});
 vm.runInContext(body+';this.complete=completePending',ctx);
 return {uses,active,original,complete:event=>ctx.complete(holder,event),setHeld:s=>held=s,get held(){return held},get stops(){return stops},get successes(){return successes},get awards(){return awards}};
}
test('successful seasoning completion stops its shake and announces once',()=>{const f=fixture();f.complete(f.original);f.complete(f.original);assert.equal(f.held.typeId,'finished');assert.equal(f.stops,1);assert.equal(f.successes,1);assert.equal(f.awards,1)});
test('failed completion restores pending item and never announces success',()=>{const f=fixture(true);f.complete(f.original);assert.equal(f.held.typeId,'pending');assert.equal(f.stops,1);assert.equal(f.successes,0);assert.equal(f.awards,0)});
test('stale completion leaves a newer use and its sound untouched',()=>{const f=fixture();const next=f.original.clone();next.nameTag='new use';f.active.use=captureEatingIdentity(next,'main',0);f.setHeld(next);f.complete(f.original);assert.equal(f.uses.size,1);assert.equal(f.stops,0);assert.equal(f.successes,0)});
