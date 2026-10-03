import assert from 'node:assert/strict';
import {
 primitiveStackProps,stackIntentSignature,stackIntentDescriptor,
 captureInteractionIntentFromStacks,interactionIntentMatchesStacks
} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2762_interaction_intent_core.js';
import {makeTwoHandIntent,sameTwoHandIntent} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a288_intent_core.js';

let n=0;const t=(name,fn)=>{fn();n++;console.log('PASS',name)};

function item(id,amount=1,{name='',lore=[],props={},damage=null,keepOnDeath=false,lockMode='none',canDestroy=[],canPlaceOn=[]}={}){
 return {
  typeId:id,amount,maxAmount:1,nameTag:name,keepOnDeath,lockMode,
  getLore(){return [...lore]},
  getRawLore(){return lore.map(text=>({text}))},
  getCanDestroy(){return [...canDestroy]},
  getCanPlaceOn(){return [...canPlaceOn]},
  getDynamicPropertyIds(){return Object.keys(props)},
  getDynamicProperty(key){return props[key]},
  getComponent(key){return key==='minecraft:durability'&&damage!==null?{damage}:undefined}
 };
}

t('primitive properties keep supported scalar and vector data',()=>{
 const s=item('x:item',1,{props:{z:2,a:true,pos:{x:1,y:2,z:3},bad:{q:1}}});
 assert.deepEqual(primitiveStackProps(s),{z:2,a:true,pos:{x:1,y:2,z:3}});
});

t('signature canonicalizes dynamic property key order',()=>{
 const a=item('x:item',2,{props:{z:2,a:1}});
 const b=item('x:item',2,{props:{a:1,z:2}});
 assert.equal(stackIntentSignature(a),stackIntentSignature(b));
});

t('signature includes amount lore name and durability',()=>{
 const a=item('x:item',2,{name:'A',lore:['L'],damage:3});
 const b=item('x:item',1,{name:'A',lore:['L'],damage:3});
 assert.notEqual(stackIntentSignature(a),stackIntentSignature(b));
 assert.notEqual(stackIntentSignature(a),stackIntentSignature(item('x:item',2,{name:'B',lore:['L'],damage:3})));
 assert.notEqual(stackIntentSignature(a),stackIntentSignature(item('x:item',2,{name:'A',lore:['M'],damage:3})));
 assert.notEqual(stackIntentSignature(a),stackIntentSignature(item('x:item',2,{name:'A',lore:['L'],damage:4})));
});

t('empty descriptor remains explicit',()=>assert.deepEqual(stackIntentDescriptor(undefined),{empty:true,id:null,sig:null}));

t('event stack matching offhand resolves offhand',()=>{
 const main=item('x:main'),off=item('x:off');
 const intent=captureInteractionIntentFromStacks(off,main,off,4);
 assert.equal(intent.hand,'off');
 assert.equal(interactionIntentMatchesStacks(intent,main,off,8),true);
});

t('main intent binds selected slot',()=>{
 const main=item('x:main'),off=item('x:off');
 const intent=captureInteractionIntentFromStacks(main,main,off,4);
 assert.equal(intent.hand,'main');
 assert.equal(interactionIntentMatchesStacks(intent,main,off,4),true);
 assert.equal(interactionIntentMatchesStacks(intent,main,off,5),false);
});

t('stack mutation invalidates deferred intent',()=>{
 const main=item('x:main',2,{props:{k:'v'}});
 const intent=captureInteractionIntentFromStacks(main,main,undefined,1);
 assert.equal(interactionIntentMatchesStacks(intent,item('x:main',1,{props:{k:'v'}}),undefined,1),false);
 assert.equal(interactionIntentMatchesStacks(intent,item('x:main',2,{props:{k:'changed'}}),undefined,1),false);
});

const metadataChanges={keepOnDeath:true,lockMode:'inventory',canDestroy:['minecraft:dirt'],canPlaceOn:['minecraft:stone']};
const bottle=(metadata={})=>item('kaleidoscope_grilling:pending_seasoning',1,
 {name:'same bottle',lore:['same lore'],props:{'kaleidoscope_grilling:seasonings':'["minecraft:redstone"]'},...metadata});
for(const [field,value] of Object.entries(metadataChanges)){
 t(field+' alone distinguishes offhand and inverse main event',()=>{
  const main=bottle(),off=bottle({[field]:value});
  assert.notEqual(stackIntentSignature(main),stackIntentSignature(off));
  // Event is a separate API snapshot, not an object identity alias.
  const fromOff=captureInteractionIntentFromStacks(bottle({[field]:value}),main,off,4);
  assert.equal(fromOff.hand,'off');
  assert.equal(interactionIntentMatchesStacks(fromOff,main,off,9),true);
  assert.equal(captureInteractionIntentFromStacks(bottle(),main,off,4).hand,'main');
 });
 t(field+' replacement invalidates deferred intent in either hand',()=>{
  const original=bottle(),replacement=bottle({[field]:value}),other=item('x:other');
  const mainIntent=captureInteractionIntentFromStacks(original,original,other,4);
  const offIntent=captureInteractionIntentFromStacks(original,other,original,4);
  assert.equal(interactionIntentMatchesStacks(mainIntent,replacement,other,4),false);
  assert.equal(interactionIntentMatchesStacks(offIntent,other,replacement,4),false);
 });
 t(field+' replacement invalidates shared two-hand snapshot',()=>{
  const main=bottle(),off=bottle(),changed=bottle({[field]:value});
  const snapshot=(m,o)=>makeTwoHandIntent(stackIntentSignature(m),stackIntentSignature(o),4,'minecraft:overworld',false);
  const before=snapshot(main,off);
  assert.equal(sameTwoHandIntent(before,snapshot(main,off)),true);
  assert.equal(sameTwoHandIntent(before,snapshot(changed,off)),false);
  assert.equal(sameTwoHandIntent(before,snapshot(main,changed)),false);
 });
}

t('restriction order canonicalizes without mutating API-owned metadata',()=>{
 const destroy=Object.freeze(['minecraft:stone','minecraft:dirt','minecraft:dirt']);
 const place=Object.freeze(['minecraft:stone','minecraft:grass_block']);
 const a=bottle();a.getCanDestroy=()=>destroy;a.getCanPlaceOn=()=>place;
 const b=bottle({canDestroy:[...destroy].reverse(),canPlaceOn:[...place].reverse()});
 assert.equal(stackIntentSignature(a),stackIntentSignature(b));
 assert.deepEqual(destroy,['minecraft:stone','minecraft:dirt','minecraft:dirt']);
 assert.deepEqual(place,['minecraft:stone','minecraft:grass_block']);
 assert.notEqual(stackIntentSignature(a),stackIntentSignature(bottle({canDestroy:[...destroy],canPlaceOn:[]})));
 assert.notEqual(stackIntentSignature(bottle()),stackIntentSignature(bottle({canDestroy:['minecraft:stone']})));
});

const capabilityFaults={
 'missing keepOnDeath':s=>{delete s.keepOnDeath},
 'missing lockMode':s=>{delete s.lockMode},
 'missing getCanDestroy':s=>{delete s.getCanDestroy},
 'missing getCanPlaceOn':s=>{delete s.getCanPlaceOn},
 'throwing keepOnDeath':s=>Object.defineProperty(s,'keepOnDeath',{get(){throw Error('capability read')}}),
 'throwing lockMode':s=>Object.defineProperty(s,'lockMode',{get(){throw Error('capability read')}}),
 'throwing getCanDestroy':s=>{s.getCanDestroy=()=>{throw Error('capability read')}},
 'throwing getCanPlaceOn':s=>{s.getCanPlaceOn=()=>{throw Error('capability read')}},
 'invalid keepOnDeath':s=>{s.keepOnDeath=0},
 'invalid lockMode':s=>{s.lockMode=null},
 'invalid restriction array':s=>{s.getCanDestroy=()=>undefined},
 'invalid restriction entry':s=>{s.getCanPlaceOn=()=>[null]},
};
for(const [name,fault] of Object.entries(capabilityFaults))t(name+' rejects capture and deferred equality',()=>{
 const invalid=bottle();fault(invalid);
 const valid=bottle(),intent=captureInteractionIntentFromStacks(valid,valid,undefined,4);
 assert.throws(()=>stackIntentSignature(invalid));
 assert.throws(()=>captureInteractionIntentFromStacks(invalid,valid,undefined,4));
 assert.throws(()=>captureInteractionIntentFromStacks(valid,invalid,undefined,4));
 assert.equal(interactionIntentMatchesStacks(intent,invalid,undefined,4),false);
 const offIntent=captureInteractionIntentFromStacks(valid,item('x:other'),valid,4);
 assert.equal(interactionIntentMatchesStacks(offIntent,item('x:other'),invalid,4),false);
});

t('fully identical readable stacks retain the explicit main-hand ambiguity',()=>{
 const main=bottle(),off=bottle();
 assert.equal(stackIntentSignature(main),stackIntentSignature(off));
 assert.equal(captureInteractionIntentFromStacks(bottle(),main,off,4).hand,'main');
 // API doubles cannot certify native offhand event reachability/acceptance.
});

console.log('A2.7.62 interaction intent core: '+n+'/'+n);
