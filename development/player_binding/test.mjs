import assert from 'node:assert/strict';
const base='../../projects/grilling/integration/immersion_lab/behavior_pack/scripts/';
const rules=await import(base+'profile_rules.js');
const flow=await import(base+'flow.js');
let passed=0;const ok=(name,fn)=>{fn();passed++;console.log('PASS',name);};
const expected={
 ONE:{durationTicks:90,bites:[1.16667,3.08333]},
 TWO:{durationTicks:90,bites:[.95833,4.0]},
 THREE:{durationTicks:100,bites:[.95833,2.33333,3.54167]},
 THREE_ALT:{durationTicks:90,bites:[.95833,2.16667,3.5]},
 THREE_RANDOM:{durationTicks:100,bites:[.95833,2.33333,3.54167]},
 FOUR:{durationTicks:90,bites:[.95833,2.33333,3.45833,4.08333]}
};
ok('all six source rules preserved',()=>assert.deepEqual(JSON.parse(JSON.stringify(rules.PROFILE_RULES)),expected));
ok('THREE_RANDOM low branch is THREE',()=>assert.equal(rules.resolveProfile('THREE_RANDOM',.2),'THREE'));
ok('THREE_RANDOM high branch is THREE_ALT',()=>assert.equal(rules.resolveProfile('THREE_RANDOM',.8),'THREE_ALT'));
ok('fixed profiles never reroll',()=>assert.equal(rules.resolveProfile('FOUR',.1),'FOUR'));
ok('profile audio mapping',()=>assert.deepEqual(['ONE','TWO','THREE','THREE_ALT','FOUR'].map(rules.soundFor),['one_skewer_eat','two_skewer_eat','three_skewer_eat','three_skewer_eat','four_skewer_eat']));
const taken=()=>({schema:1,phase:'taken',flips:4,seq:5,action:null,lastCue:-1});
for(const p of ['ONE','TWO','THREE','THREE_ALT','FOUR']){
 ok(p+' exact duration',()=>{
   const r=flow.apply(taken(),'eat',100,{profile:p});assert.equal(r.accepted,true);assert.equal(r.state.action.ends-100,expected[p].durationTicks);
 });
 ok(p+' bite checkpoints',()=>{
   let r=flow.apply(taken(),'eat',100,{profile:p}),s=r.state;
   for(let i=0;i<expected[p].bites.length;i++){
     const tick=100+Math.ceil(expected[p].bites[i]*20);
     const a=flow.advance(s,tick);s=a.state;assert.ok(a.events.some(e=>e.kind==='bite'&&e.index===i),p+' bite '+i);
   }
 });
}
ok('unresolved THREE_RANDOM is rejected',()=>assert.throws(()=>flow.apply(taken(),'eat',0,{profile:'THREE_RANDOM'})));
ok('cancelled eating returns to taken',()=>{const s=flow.apply(taken(),'eat',0,{profile:'TWO'}).state;assert.equal(flow.cancel(s).state.phase,'taken');});
ok('brush includes pickup/stow envelope',()=>{let s={schema:1,phase:'loaded',flips:0,seq:1,action:null,lastCue:-1};s=flow.apply(s,'brush',10).state;assert.equal(s.action.ends-s.action.started,26);assert.ok(flow.advance(s,12).events.every(e=>e.kind!=='brush_contact'));assert.ok(flow.advance(s,13).events.some(e=>e.kind==='brush_contact'));});
ok('season includes pickup/stow envelope',()=>{let s={schema:1,phase:'seasonable',flips:4,seq:1,action:null,lastCue:-1};s=flow.apply(s,'season',10).state;assert.equal(s.action.ends-s.action.started,16);assert.ok(flow.advance(s,13).events.some(e=>e.kind==='season_contact'));});
ok('stand no longer renders floating eating sample',()=>assert.equal(flow.view(taken(),0).held,false));
ok('FOUR stage count reaches four',()=>assert.equal(rules.stageAt('FOUR',4.1),4));
console.log(JSON.stringify({passed,failed:0,scope:'six source eating rules and A1.16 presentation flow; not Minecraft engine acceptance'}));
