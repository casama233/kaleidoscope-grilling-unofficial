/** SDK-shaped RawMessage serialization, actual itemData and production helper.
 * API doubles are contract regressions, not a claim about a live getter sample.
 */
import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import vm from 'node:vm';
import * as lore from '../../projects/grilling/gameplay_core/behavior_pack/scripts/bottle_lore_core.js';
import * as data from '../../projects/grilling/gameplay_core/behavior_pack/scripts/itemDataCore.js';
import {metadataSignature} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/skewer_item_snapshot.js';
import {seasoningLore} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/localized_lore_core.js';
const main=fs.readFileSync(new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/main.js',import.meta.url),'utf8');
const start=main.indexOf('function refreshBottleIngredientLore('),end=main.indexOf('\nfunction ',start+1),body=main.slice(start,end);
const old=seasoningLore(undefined,3,{pending:true}),fresh=seasoningLore(undefined,8,{pending:true});
function sdk(node,style){
 if(typeof node==='string')return {text:node};
 if(node.rawtext)return {rawtext:node.rawtext.map(n=>sdk(n,style))};
 if(node.translate){const out={};if(node.with!==undefined)out.with=style==='args'&&Array.isArray(node.with)?{rawtext:node.with.map(text=>({text}))}:structuredClone(node.with);out.translate=node.translate;return out}
 return structuredClone(node);
}
class Stack{
 constructor(style,maxAmount=1){Object.assign(this,{style,maxAmount,props:{},raw:[],fault:null,nameTag:'kept',keepOnDeath:true})}
 getDynamicPropertyIds(){return Object.keys(this.props)}getDynamicProperty(k){return this.props[k]}setDynamicProperty(k,v){this.props[k]=v}
 getRawLore(){return structuredClone(this.raw)}
 setLore(lines){if(this.fault==='throw')throw Error('native setLore refused');if(this.fault==='reject')return;
  this.raw=lines.map(line=>{const n=sdk(line,this.style);return this.style==='keys'||n.rawtext?n:{rawtext:[n]}});
  if(this.fault==='dropCustom')this.raw.shift();if(this.fault==='wrongCount'){const i=this.raw.findIndex(lore.isOwnedBottleLore);this.raw[i]=sdk(seasoningLore(undefined,7,{pending:true})[0],this.style)}
  if(this.fault==='dropToken')this.raw=this.raw.filter(n=>!JSON.stringify(n).includes('§r§0§r§1§r§2'));
 }
 clone(){return Object.assign(new Stack(this.style,this.maxAmount),structuredClone({...this}))}
}
function fixture(style,maxAmount=1){const records=new Map();data.configureItemDataWorld({getDynamicProperty:k=>records.get(k),setDynamicProperty:(k,v)=>records.set(k,v)});const stack=new Stack(style,maxAmount);stack.setLore([{rawtext:[{text:'Custom secret '},{translate:'custom.key',with:['kept']} ]},...old]);data.setItemProperty(stack,'test:retained','metadata');const context=vm.createContext({...lore,...data,seasoningLore,metadataSignature});vm.runInContext(body+';this.refresh=refreshBottleIngredientLore;',context);return {stack,refresh:s=>context.refresh(s,{kind:'pending',ingredients:Array(8).fill('minecraft:redstone')})};}
for(const style of ['keys','wrapper','args'])for(const maxAmount of [1,64])test(style+' actual itemData refresh replaces owned lines once and preserves custom/metadata token '+maxAmount,()=>{
 const f=fixture(style,maxAmount),before=f.stack.clone(),custom=data.getItemRawLore(before)[0],next=f.stack.clone();f.refresh(next);
 assert.equal(lore.bottleLoreSignature(data.getItemRawLore(next)),lore.bottleLoreSignature([custom,...fresh]));assert.equal(data.getItemRawLore(next).filter(lore.isOwnedBottleLore).length,2);
 assert.deepEqual(data.getItemRawLore(next)[0],custom);assert.equal(data.getItemProperty(next,'test:retained'),'metadata');assert.equal(next.nameTag,before.nameTag);assert.equal(next.keepOnDeath,true);assert.deepEqual(f.stack,before);
 f.refresh(next);assert.equal(data.getItemRawLore(next).filter(lore.isOwnedBottleLore).length,2);
});
for(const fault of ['throw','reject','dropCustom','wrongCount','dropToken'])test('failed '+fault+' readback cannot be committed and retains original clone source',()=>{
 const f=fixture('wrapper',fault==='dropToken'?64:1),before=f.stack.clone(),next=f.stack.clone();next.fault=fault;
 assert.throws(()=>f.refresh(next));assert.deepEqual(f.stack,before);
});
test('owned identification never strips mixed or unknown custom messages',()=>{
 const owned=old[0];for(const line of [{rawtext:[{text:'prefix'},owned]},{rawtext:[owned,{text:'suffix'}]},{translate:owned.translate,text:'custom'}, {rawtext:[owned],text:'custom'}, {rawtext:[{translate:owned.translate,with:{rawtext:[{translate:'custom.argument'}]}}]}])assert.equal(lore.isOwnedBottleLore(line),false);
 assert.equal(lore.isOwnedBottleLore({rawtext:[{rawtext:[owned]}]}),true);
});
test('semantic signatures preserve argument/line order, translation identity and unknown structure',()=>{
 const good=fresh;for(const bad of [[...fresh].reverse(),seasoningLore(undefined,7,{pending:true}),[{...fresh[0],translate:'other'},fresh[1]],[{...fresh[0],with:['8','7']},fresh[1]],[{rawtext:[fresh[0],{text:'extra'}]},fresh[1]]])assert.notEqual(lore.bottleLoreSignature(good),lore.bottleLoreSignature(bad));
 assert.equal(lore.bottleLoreSignature([{text:'x'}]),lore.bottleLoreSignature(['x']));assert.equal(lore.bottleLoreSignature([{rawtext:[fresh[0]]}]),lore.bottleLoreSignature([fresh[0]]));
});
test('mismatch diagnostics never contain custom text or metadata values',()=>{
 const message=lore.bottleLoreMismatch([{text:'private text'}],[{text:'private other'}]);assert.equal(message,'line 0 (object -> object)');assert.ok(!message.includes('private'));
});
test('argument order, unknown extra keys and literal values remain fail-closed',()=>{
 const translation={translate:'custom.key',with:['first','second']};assert.notEqual(lore.bottleLoreSignature([translation]),lore.bottleLoreSignature([{...translation,with:['second','first']}]));
 const extra={rawtext:[old[0]],unknown:'retained'};assert.equal(lore.isOwnedBottleLore(extra),false);assert.notEqual(lore.bottleLoreSignature([extra]),lore.bottleLoreSignature([{rawtext:[old[0]]}]));
 assert.equal(lore.bottleLoreSignature(['custom']),lore.bottleLoreSignature([{text:'custom'}]));assert.notEqual(lore.bottleLoreSignature(['custom']),lore.bottleLoreSignature([{text:'changed'}]));
});
test('empty and depth-limited wrappers stay unknown rather than becoming owned or equivalent',()=>{
 let within=old[0];for(let i=0;i<15;i++)within={rawtext:[within]};assert.equal(lore.isOwnedBottleLore(within),true);
 const deep={rawtext:[within]};assert.equal(lore.isOwnedBottleLore(deep),false);assert.notEqual(lore.bottleLoreSignature([deep]),lore.bottleLoreSignature([old[0]]));
 const empty={rawtext:[]};assert.equal(lore.isOwnedBottleLore(empty),false);assert.notEqual(lore.bottleLoreSignature([empty]),lore.bottleLoreSignature([{text:''}]));
});
