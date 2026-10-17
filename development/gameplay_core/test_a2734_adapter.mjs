import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

class MockItemStack{
 constructor(typeId,amount=1){
  this.typeId=typeId;this.amount=amount;this.props=new Map();this.lore=[];
 }
 getDynamicProperty(k){return this.props.get(k)}
 setDynamicProperty(k,v){if(v===undefined)this.props.delete(k);else this.props.set(k,v)}
 setLore(v){this.lore=[...v]}
 getLore(){return [...this.lore]}
 clone(){const x=new MockItemStack(this.typeId,this.amount);x.props=new Map(this.props);x.lore=[...this.lore];return x}
}
const context=vm.createContext({console,JSON,Map,Set,Object,Array,Number,String,Boolean,Error,Math});
const root=new URL('./',import.meta.url);
const core=new vm.SourceTextModule(fs.readFileSync(new URL('a2734_cookery_oil_pot_core.js',root),'utf8'),{context,identifier:'core'});
const adapter=new vm.SourceTextModule(fs.readFileSync(new URL('a2734_cookery_oil_pot_adapter.js',root),'utf8'),{context,identifier:'adapter'});
const server=new vm.SyntheticModule(['ItemStack'],function(){this.setExport('ItemStack',MockItemStack)},{context,identifier:'server'});
await core.link(()=>{throw new Error('unexpected import')});
await adapter.link(async spec=>spec==='@minecraft/server'?server:core);
await adapter.evaluate();
const ns=adapter.namespace;

function filled(type,count,withCount=true){
 const s=new MockItemStack('kaleidoscope_cookery:oil_pot_filled',1);
 if(type)s.setDynamicProperty('kaleidoscope_grilling:oil_type',type);
 if(withCount)s.setDynamicProperty('kc_oil_count',count);
 return s;
}
const empty=new MockItemStack('kaleidoscope_cookery:oil_pot',1);

let r=ns.readCookeryOilPot(filled('',0,false));
assert.equal(r.count,0);assert.equal(r.capacity,256);

r=ns.readCookeryOilPotForPlacement(filled('',0,false));
assert.equal(r.count,256);assert.equal(r.capacity,256);

r=ns.readCookeryOilPot(filled('premium_chili',0,false));
assert.equal(r.count,0);assert.equal(r.capacity,64);

r=ns.readCookeryOilPotForPlacement(filled('premium_chili',0,false));
assert.equal(r.count,64);assert.equal(r.capacity,64);

r=ns.planCookeryTypedOilAddition(empty,'canola',8);
assert.equal(r.ok,true);assert.equal(r.next.typeId,'kaleidoscope_cookery:oil_pot_filled');
assert.equal(r.next.getDynamicProperty('kc_oil_count'),8);
assert.equal(r.next.getDynamicProperty('kaleidoscope_grilling:oil_type'),'canola');

const nativeFat=filled('',16,true);
r=ns.planCookeryTypedOilAddition(nativeFat,'canola',8);
assert.equal(r.ok,false);assert.equal(r.reason,'native_fat');

const typed=filled('secret_chili',56,true);
typed.setDynamicProperty('third_party:test','keep');
r=ns.planCookeryTypedOilAddition(typed,'secret_chili',8);
assert.equal(r.ok,true);assert.equal(r.next.getDynamicProperty('kc_oil_count'),64);
assert.equal(r.next.getDynamicProperty('third_party:test'),'keep');

r=ns.planCookeryOilPotConsumption(filled('premium_chili',2,true),2,'premium_chili');
assert.equal(r.ok,true);assert.equal(r.remaining,0);
assert.equal(r.next.typeId,'kaleidoscope_cookery:oil_pot');

r=ns.planCookeryOilPotConsumption(filled('premium_chili',0,false),2,'premium_chili');
assert.equal(r.ok,false);assert.equal(r.reason,'insufficient');

console.log(JSON.stringify({passed:9,failed:0,scope:'A2.7.34 strict hand-held vs legacy placement Cookery oil-pot adapter'}));
