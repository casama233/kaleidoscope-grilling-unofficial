import assert from 'node:assert/strict';
import {
 primitiveStackProps,stackIntentSignature,stackIntentDescriptor,
 captureInteractionIntentFromStacks,interactionIntentMatchesStacks
} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2762_interaction_intent_core.js';

let n=0;const t=(name,fn)=>{fn();n++;console.log('PASS',name)};

function item(id,amount=1,{name='',lore=[],props={},damage=null}={}){
 return {
  typeId:id,amount,nameTag:name,
  getLore(){return [...lore]},
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

console.log('A2.7.62 interaction intent core: '+n+'/'+n);
