/** Current Java completion oracles and actual runtime bodies; API doubles, not client evidence. */
import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import vm from 'node:vm';
import {hasSeasoningBase,BASE_SEASONINGS} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2743_seasoning_contract_core.js';
import {captureEatingIdentity,commitEating} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a285_eating_transaction.js';
import {completedUseStillCurrent} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2810_use_transaction.js';
import {configureItemDataWorld} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/itemDataCore.js';
configureItemDataWorld({getDynamicProperty(){},setDynamicProperty(){}});
class Stack{constructor(typeId,amount=1){this.typeId=typeId;this.amount=amount;this.nameTag='';this.lore=[];this.ingredients=[]}getDynamicPropertyIds(){return ['test:ingredients']}getDynamicProperty(){return JSON.stringify(this.ingredients)}getRawLore(){return this.lore}setLore(v){this.lore=v}clone(){return Object.assign(new Stack(this.typeId,this.amount),structuredClone({...this}))}}
const source=fs.readFileSync(new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/main.js',import.meta.url),'utf8');
const body=source.slice(source.indexOf('function completePending('),source.indexOf('world.afterEvents.itemStartUse.subscribe'));
function fixture(hand,ingredients,{fail=false,mutation}={}){
 const player={id:'owner',selectedSlotIndex:3},original=new Stack('kaleidoscope_grilling:pending_seasoning');original.ingredients=[...ingredients];original.nameTag='old bottle';let held=original.clone(),writes=0,feedback=0,awards=0,warnings=0,stops=0;
 const map=new Map([[player.id,{hand,stack:original.clone(),use:captureEatingIdentity(original,hand,3),audio:{}}]]);
 const ctx=vm.createContext({ItemStack:Stack,PENDING_USES:map,completedUseStillCurrent,heldByHand:()=>held,stopSoundHandle(){stops++},readSeasonings:s=>s.ingredients,hasSeasoningBase,javaInteractionFeedback(){warnings++},SEASONING_VARIANT_MAX:7,SEASONING_MAX_USES:16,SEASON_VARIANT_KEY:'variant',specialSeasoningVisualId:(uses,variant)=>'finished:'+uses+':'+variant,setSeasonings:(s,list)=>s.ingredients=[...list],setUses:(s,n)=>s.uses=n,getUses:s=>s.uses,setItemProperty:(s,k,v)=>s[k]=v,setItemLore:(s,l)=>s.lore=l,seasoningLore:()=>[],commitEating,writeUseHand(_p,_use,next){writes++;held=next;if(fail&&writes===1)throw Error('write refused')},seasoningFinished(){feedback++},awardSeasoningFinishedChallenges(_p,list){assert.deepEqual([...list],ingredients);awards++}});
 vm.runInContext(body+';this.complete=completePending;',ctx);
 if(mutation==='slot')player.selectedSlotIndex=4;
 if(mutation==='contents')held.ingredients=['different'];
 if(mutation==='missingStart')map.clear();
 if(mutation==='missingHand')held=undefined;
 return {complete(){ctx.complete(player,original.clone())},get held(){return held},get feedback(){return feedback},get warnings(){return warnings},get awards(){return awards},get writes(){return writes},get stops(){return stops},original};
}
// Java PendingSeasoningItem.finishUsingItem never checks base membership. Its
// loadLegacy creates PENDING for any nonempty Ingredients list, including these.
for(const hand of ['main','off'])for(const list of [[],[BASE_SEASONINGS[0]],['external:legacy_spice'],[...BASE_SEASONINGS],[BASE_SEASONINGS[0],BASE_SEASONINGS[0]]])test(hand+' pending preserves '+JSON.stringify(list),()=>{
 const f=fixture(hand,list);f.complete();assert.match(f.held.typeId,/^finished:0:[0-7]$/);assert.deepEqual([...f.held.ingredients],list);assert.equal(f.held.nameTag,'');assert.equal(f.held.uses,0);assert.equal(f.feedback,1);assert.equal(f.awards,1);assert.equal(f.warnings,0);f.complete();assert.equal(f.feedback,1);assert.equal(f.writes,1);
});
for(const hand of ['main','off'])test(hand+' rejected write restores pending without feedback',()=>{const f=fixture(hand,[BASE_SEASONINGS[0]],{fail:true});f.complete();assert.equal(f.held.typeId,f.original.typeId);assert.deepEqual(f.held.ingredients,f.original.ingredients);assert.equal(f.feedback,0);assert.equal(f.awards,0)});
for(const mutation of ['slot','contents','missingStart','missingHand'])test('stale '+mutation+' is retained',()=>{const f=fixture('main',[BASE_SEASONINGS[0]],{mutation});f.complete();assert.equal(f.feedback,0);assert.equal(f.writes,0);assert.equal(f.stops,0)});
const audioSource=fs.readFileSync(new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/immersion_audio_runtime.js',import.meta.url),'utf8');
const audioBody=audioSource.slice(audioSource.indexOf('export function seasoningFinished('),audioSource.indexOf('export {stopSoundHandle}')).replace('export function','function');
const original={events:[],playSound(...args){this.events.push(['sound',...args])}},next={events:[],playSound(...args){this.events.push(['sound',...args])}};
test('finish particles precede original PLAYERS sound with captured level and fresh BlockPos center',()=>{
 const actor={dimension:original,location:{x:-2.75,y:81.9,z:3.25}};original.events=[];next.events=[];
 const origin=e=>Object.fromEntries(Object.entries(e.location).map(([a,n])=>[a,Math.floor(n)+.5]));
 const ctx=vm.createContext({SEASONING_FINISH_SOUND_ID:'kg_java21.seasoning_finished',seasoningFinishSoundOrigin:origin,interactionParticleBurst(d,p,event){d.events.push(['particles',{...p},event]);actor.dimension=next;actor.location={x:-3.8,y:83.1,z:7.9}},useSound(p,id,volume){p.dimension.playSound('kg_imm.'+id,p.location,{volume,pitch:1})}});
 vm.runInContext(audioBody+';this.finish=seasoningFinished;',ctx);ctx.finish(actor);
 assert.equal(original.events.length,2);assert.equal(original.events[0][0],'particles');assert.deepEqual(original.events[0][1],{x:-2.75,y:81.9,z:3.25});assert.equal(original.events[1][1],'kg_java21.seasoning_finished');assert.deepEqual({...original.events[1][2]},{x:-3.5,y:83.5,z:7.5});assert.deepEqual({...original.events[1][3]},{volume:.8,pitch:1});assert.equal(next.events.length,0);
});
test('finish sound definition preserves original sample gain and PLAYERS category',()=>{
 const d=JSON.parse(fs.readFileSync(new URL('../../projects/grilling/gameplay_core/resource_pack/sounds/sound_definitions.json',import.meta.url),'utf8')).sound_definitions['kg_java21.seasoning_finished'];
 assert.deepEqual(d,{category:'player',sounds:[{name:'sounds/kg_imm/action_success',volume:.85}],max_distance:16});
});
