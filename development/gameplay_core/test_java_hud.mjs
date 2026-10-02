// Source/asset/adapter regressions; never Minecraft client acceptance.
import assert from 'node:assert/strict';
import {test} from 'node:test';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {javaEatingHudFrame} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/java_eating_hud_core.js';
import {javaInteractionMessage,JAVA_INTERACTION_KEYS} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/interaction_feedback_core.js';
const root=new URL('../../',import.meta.url),rp=new URL('projects/grilling/gameplay_core/resource_pack/',root);
test('original keys and argument order; invented hints rejected',()=>{
 assert.deepEqual(javaInteractionMessage('grill_wait_flip',[2,4]),{rawtext:[{translate:'message.kaleidoscope_grilling.grill_wait_flip',with:['2','4']}]});
 assert.deepEqual(javaInteractionMessage('grill_ready_to_take',[],true).rawtext.map(x=>x.text??x.translate),['§c','message.kaleidoscope_grilling.grill_ready_to_take','§r']);
 assert.equal(javaInteractionMessage('flip_cooldown'),undefined);
 for(const locale of ['en_US','zh_CN','zh_TW']){
  const text=fs.readFileSync(new URL(`texts/${locale}.lang`,rp),'utf8');
  for(const key of JAVA_INTERACTION_KEYS)assert.ok(text.includes(`message.kaleidoscope_grilling.${key}=`),`${locale}: ${key}`);
 }
});
test('90/100 tick progress uses 102 pixels and changes at tick 25',()=>{
 for(const duration of [90,100]){
  assert.equal(javaEatingHudFrame({id:'minecraft:unknown',elapsed:0,duration}).width,0);
  for(const elapsed of [24,25,duration,duration+1]){
   const f=javaEatingHudFrame({id:'kaleidoscope_grilling:grilled_fish_skewer',elapsed,duration});
   assert.equal(f.ready,elapsed>=25);assert.equal(f.width,Math.min(102,Math.round(102*elapsed/duration)));
   assert.notEqual(f.icon,255);assert.equal(f.packet.replace(/§[0-9a-fr]/g,''),'','graphical transport has no printable text');
  }
 }
 assert.equal(javaEatingHudFrame({elapsed:NaN,duration:90}),undefined);
});
test('slime and failed icons follow original four-tick/five-frame cycle',()=>{
 for(const id of ['grilled_slime_skewer','mysterious_skewer']){
  const icons=Array.from({length:5},(_,i)=>javaEatingHudFrame({id,elapsed:30,duration:90,tick:i*4}).icon);
  assert.ok(!icons.includes(255));assert.equal(new Set(icons).size,5);
  assert.equal(javaEatingHudFrame({id,elapsed:30,duration:90,tick:20}).icon,icons[0]);
 }
});
test('GUI copies all pinned original assets and preserves own packet expiry',()=>{
 const f=JSON.parse(fs.readFileSync(new URL('development/gameplay_core/fixtures/java-hud-1.1.1.json',root)));
 for(const [name,row] of Object.entries(f.assets))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(new URL(name,rp))).digest('hex'),row.sha256,name);
 const ui=JSON.parse(fs.readFileSync(new URL('ui/hud_screen.json',rp)));
 assert.equal(f.machine_hud_default,false);assert.equal(ui.kg_eating_expire.destroy_at_end,'kg_eating_packet');
 assert.equal(ui.kg_eating_expire.duration,.075);assert.equal(ui.kg_eating_packet.controls.length,405);
 assert.ok(ui.hud_actionbar_text.visible.includes('§r[KT]'));
 const script=fs.readFileSync(new URL('projects/grilling/gameplay_core/behavior_pack/scripts/java_eating_hud_runtime.js',root),'utf8');
 assert.ok(!script.includes("setActionBar('')"));assert.ok(!script.includes('runInterval'));
});
