// Pure algorithms only: no Minecraft server import, no mock players, no world.
import test from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
const root=path.resolve(process.env.GRILLING_PROJECT||path.join(path.dirname(fileURLToPath(import.meta.url)),'..'));
const load=name=>import(pathToFileURL(path.join(root,'behavior_pack/scripts',name)));
const {commitSteps,commitTwoParty}=await load('a277_grill_transaction_core.js');
const {makeTwoHandIntent,sameTwoHandIntent}=await load('a288_intent_core.js');
const {visitUniqueTracked}=await load('a288_visual_budget_core.js');

test('void-returning successful steps are accepted',()=>{
 const calls=[];const r=commitTwoParty(()=>calls.push('a'),()=>{},()=>calls.push('undo a'),()=>calls.push('undo b'));
 assert.equal(r.ok,true);assert.deepEqual(calls,['a']);
});
test('first-step failure rolls back only the attempted step',()=>{
 const calls=[];const r=commitTwoParty(()=>{calls.push('a');throw Error('fail')},()=>calls.push('b'),()=>calls.push('undo a'),()=>calls.push('undo b'));
 assert.equal(r.ok,false);assert.deepEqual(calls,['a','undo a']);
});
test('explicit false from second step is a failure with reverse rollback',()=>{
 const calls=[];const r=commitTwoParty(()=>calls.push('a'),()=>{calls.push('b');return false},()=>calls.push('undo a'),()=>calls.push('undo b'));
 assert.equal(r.ok,false);assert.equal(r.rollbackErrors,0);assert.deepEqual(calls,['a','b','undo b','undo a']);
});
test('rollback false or exception does not suppress remaining rollback',()=>{
 const calls=[];const r=commitSteps([
  {apply(){calls.push('a')},rollback(){calls.push('undo a');throw Error('restore fail')}},
  {apply(){calls.push('b');throw Error('fail')},rollback(){calls.push('undo b');return false}}
 ]);
 assert.equal(r.rollbackErrors,2);assert.deepEqual(calls,['a','b','undo b','undo a']);
});
test('all partial stages restore in reverse order',()=>{
 const value=[0,0,0];const steps=value.map((_,i)=>({apply(){value[i]=1;if(i===2)throw Error('partial')},rollback(){value[i]=0}}));
 assert.equal(commitSteps(steps).ok,false);assert.deepEqual(value,[0,0,0]);
});
test('zero-step transaction is a no-op',()=>assert.deepEqual(commitSteps([]),{ok:true,rollbackErrors:0}));
const base=()=>makeTwoHandIntent('food amount=2','stick amount=4',3,'minecraft:overworld',false);
test('unchanged two-hand intent is accepted',()=>assert.equal(sameTwoHandIntent(base(),base()),true));
for(const [key,value] of [['main','different food'],['off','different stick'],['slot',4],['dimensionId','minecraft:nether'],['sneaking',true]]){
 test('changed '+key+' cancels deferred intent',()=>assert.equal(sameTwoHandIntent(base(),{...base(),[key]:value}),false));
}
test('invalid or lost snapshot is never accepted',()=>{
 assert.equal(makeTwoHandIntent(null,null,-1,'minecraft:overworld',false),null);
 assert.equal(makeTwoHandIntent(null,null,0,null,false),null);
 assert.equal(sameTwoHandIntent(null,null),false);assert.equal(sameTwoHandIntent(base(),null),false);
});
function rows(n){return new Map(Array.from({length:n},(_,i)=>[i,{id:i}]))}
for(const size of [0,1,3,12,40])test('round-robin visits unique rows, size '+size,()=>{
 const data=rows(size),visited=[];const r=visitUniqueTracked(data,undefined,new Set(),12,row=>visited.push(row.id));
 assert.equal(r.visited,Math.min(12,size));assert.equal(new Set(visited).size,visited.length);
});
test('dirty rows are not visited a second time',()=>{
 const data=rows(5),visited=[],seen=new Set([data.get(0),data.get(1)]);
 visitUniqueTracked(data,undefined,seen,10,row=>visited.push(row.id));
 assert.deepEqual(visited,[2,3,4]);
});
test('large queues preserve round-robin progress',()=>{
 const data=rows(50),visited=[];let cursor;
 for(let i=0;i<5;i++){const r=visitUniqueTracked(data,cursor,new Set(),12,row=>visited.push(row.id));cursor=r.cursor}
 assert.deepEqual(visited.slice(0,50),Array.from({length:50},(_,i)=>i));
});
test('deletion during traversal stays bounded',()=>{
 const data=rows(8),visited=[];
 const r=visitUniqueTracked(data,undefined,new Set(),12,row=>{visited.push(row.id);data.delete(row.id)});
 assert.equal(r.visited,8);assert.equal(data.size,0);assert.equal(new Set(visited).size,8);
});
test('all rows already seen causes zero repeat work',()=>{
 const data=rows(4);assert.equal(visitUniqueTracked(data,undefined,new Set(data.values()),12,()=>assert.fail()).visited,0);
});
