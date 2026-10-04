import assert from 'node:assert/strict';
import {test} from 'node:test';
import fs from 'node:fs';
import vm from 'node:vm';
const source=fs.readFileSync(new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/main.js',import.meta.url),'utf8');
function fixture(){
 const queue=[],fx=new Map([['heavy_metal',{until:1000,amp:0}]]),sounds=[];
 const health={currentValue:8,setCurrentValue(v){this.currentValue=v}};
 const target={id:'entity',getComponent:()=>health,dimension:{playSound:id=>sounds.push(id)},location:{x:0,y:0,z:0}};
 let handler;const context=vm.createContext({console,world:{beforeEvents:{entityHurt:{subscribe:fn=>handler=fn}}},system:{run:fn=>queue.push(fn)},fxGet:(_t,id)=>fx.get(id),fxClear:(_t,id)=>fx.delete(id),fxSet:(_t,id,ticks)=>fx.set(id,{until:ticks})});
 vm.runInContext(source.slice(source.indexOf('const PENDING_METAL_RESCUES='),source.indexOf('world.afterEvents.playerSpawn.subscribe')),context);
 return {fx,health,sounds,queue,hit(cancel=false){const e={hurtEntity:target,damage:10,damageSource:{cause:'entityAttack'},cancel};handler(e);return e},flush(){while(queue.length)queue.shift()()}};
}
test('one reservation for repeated same-tick lethal events; later event is not granted extra immunity',()=>{
 const f=fixture();assert.equal(f.hit().cancel,true);assert.equal(f.hit().cancel,false);assert.equal(f.queue.length,1);
 f.flush();assert.equal(f.health.currentValue,1);assert.equal(f.fx.has('heavy_metal'),false);assert.equal(f.fx.get('heavy_metal_poisoning').until,12000);assert.equal(f.sounds.length,1);
});
for(const mode of ['milk','death','replacement'])test(`deferred rescue does not restore an invalidated ${mode} session`,()=>{
 const f=fixture();f.hit();if(mode==='milk')f.fx.clear();if(mode==='death')f.health.currentValue=0;if(mode==='replacement')f.fx.set('heavy_metal',{until:2000,amp:1});
 f.flush();assert.equal(f.fx.has('heavy_metal_poisoning'),false);assert.equal(f.sounds.length,0);assert.equal(f.health.currentValue,mode==='death'?0:8);
});
test('a prior addon cancellation does not consume or schedule heavy metal',()=>{
 const f=fixture();f.hit(true);assert.equal(f.queue.length,0);assert.equal(f.fx.has('heavy_metal'),true);
});
