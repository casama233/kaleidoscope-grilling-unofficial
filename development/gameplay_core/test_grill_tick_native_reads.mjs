import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {test} from 'node:test';
const source=fs.readFileSync(new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/main.js',import.meta.url),'utf8');
const callback=source.slice(source.indexOf('function tickGrill(block){'),source.indexOf('function tundraFactor'));
function fixture({burn=false,reject=false,missing=false}={}){
 let state={lit:true},count=3,reads=0,occupancy=0;const audio=[];
 const context=vm.createContext({system:{currentTick:1},readState:()=>{reads++;return state},occupied:()=>{occupancy++;if(missing)throw Error('unavailable inventory');return count},tickState:()=>({state:{lit:true},events:burn?[{kind:'burn_to_charcoal'}]:[]}),writeTickState:(_,before,next)=>{if(reject)throw Error('write failed');state=next;return next},burnGrillContents:()=>{state={lit:false};count=0},updateGrillAudio:(_,lit,n)=>audio.push([lit,n]),removeGrillAudio:()=>audio.push('removed'),grillAmbientParticles:()=>{},console});
 vm.runInContext(callback+';this.tick=tickGrill;',context);context.tick({});return {reads,occupancy,audio};
}
test('ordinary tick and audio share the same validated native inventory read',()=>assert.deepEqual(fixture(),{reads:1,occupancy:1,audio:[[true,3]]}));
test('audio re-reads committed contents and state after burn-to-charcoal mutation',()=>assert.deepEqual(fixture({burn:true}),{reads:2,occupancy:2,audio:[[false,0]]}));
test('failed state update falls back to persisted state for audio',()=>assert.deepEqual(fixture({reject:true}),{reads:2,occupancy:2,audio:[[true,3]]}));
test('unavailable inventory never invents empty contents and removes only transient audio',()=>assert.deepEqual(fixture({missing:true}),{reads:2,occupancy:2,audio:['removed']}));

const adapter=fs.readFileSync(new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/a2740_grill_state_adapter.js',import.meta.url),'utf8');
test('native occupancy counts every fill level without materializing item copies',()=>{
 const container={size:3,emptySlotsCount:3,getItem(){throw Error('unnecessary native item copy')}};
 const context=vm.createContext({stationContainer:()=>container});
 vm.runInContext(adapter.slice(adapter.indexOf('export function occupiedGrillSlots')).replace('export ',''),context);
 for(let count=0;count<=3;count++){container.emptySlotsCount=3-count;assert.equal(context.occupiedGrillSlots({}),count)}
 container.emptySlotsCount=undefined;assert.throws(()=>context.occupiedGrillSlots({}),/Invalid/);
 container.emptySlotsCount=0;container.size=9;assert.throws(()=>context.occupiedGrillSlots({}),/Invalid/);
});

test('display schedule refreshes within helper expiry without intervening block reads',()=>{
 const visual=fs.readFileSync(new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/grill_visual_runtime.js',import.meta.url),'utf8');
 let sync=0;const system={currentTick:0};
 const context=vm.createContext({system,audience:()=>[],syncGrillDisplay:()=>sync++});
 vm.runInContext(visual.slice(visual.indexOf('export function tickGrillDisplay'),visual.indexOf('export function syncGrillDisplay')).replace('export ',''),context);
 for(let i=0;i<15;i++){system.currentTick=i;context.tickGrillDisplay({get location(){throw Error('intervening location read')}})}
 assert.equal(sync,3);
});
