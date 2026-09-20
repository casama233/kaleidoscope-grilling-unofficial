import {world} from '@minecraft/server';
import {weightedHeat,NORMAL_HEAT_WINDOW} from './a23_hot_merge.js';

const HOT='kaleidoscope_grilling:hot_until';
const IGNORE=new Set([
 HOT,'kaleidoscope_grilling:model_variants','kaleidoscope_grilling:creator',
 'kaleidoscope_grilling:creator_name','kaleidoscope_grilling:creator_uuid',
 'SkewerModelVariants','Creator','CreatorName','CreatorUuid'
]);
function now(){try{return world.getAbsoluteTime()}catch{return 0}}
function norm(v){
 if(v===undefined)return null;
 if(typeof v==='number'||typeof v==='string'||typeof v==='boolean'||v===null)return v;
 if(Array.isArray(v))return v.map(norm);
 if(typeof v==='object')return Object.fromEntries(Object.keys(v).sort().map(k=>[k,norm(v[k])]));
 return String(v);
}
function baseLore(stack){try{return stack.getLore().filter(x=>!String(x).startsWith('§c🔥'))}catch{return []}}
function props(stack,includeHot=false){
 let ids=[];try{ids=stack.getDynamicPropertyIds()}catch{}
 return ids.filter(k=>includeHot||!IGNORE.has(k)).sort().map(k=>{let v;try{v=stack.getDynamicProperty(k)}catch{}return [k,norm(v)]});
}
export function isSkewer(stack){return !!stack&&stack.typeId.startsWith('kaleidoscope_grilling:')&&(stack.typeId.includes('skewer')||stack.typeId==='kaleidoscope_grilling:dark_grilling')}
export function mergeSignature(stack){return JSON.stringify({type:stack?.typeId??'',name:stack?.nameTag??'',lore:baseLore(stack),props:props(stack,false)})}
export function sameForHeatMerge(a,b){return !!a&&!!b&&mergeSignature(a)===mergeSignature(b)}
export function hotUntil(stack){try{return Number(stack?.getDynamicProperty(HOT)??0)}catch{return 0}}
export function isHot(stack,t=now()){return hotUntil(stack)>t}
function bucket(t){return t-(((t%100)+100)%100)}
function setHot(stack,remaining,t=now()){
 try{
  if(remaining>0)stack.setDynamicProperty(HOT,bucket(t+remaining));
  else stack.setDynamicProperty(HOT,undefined);
  const lore=baseLore(stack);
  if(remaining>0){const sec=Math.max(1,Math.ceil(remaining/20)),m=Math.floor(sec/60),s=String(sec%60).padStart(2,'0');lore.push('§c🔥 煙火氣 '+m+':'+s)}
  stack.setLore(lore);
 }catch{}
 return stack;
}
function moveCount(target,source,moved,t=now()){
 const tc=target.amount,sc=source.amount,th=Math.max(0,hotUntil(target)-t),sh=Math.max(0,hotUntil(source)-t);
 const bothHot=th>0&&sh>0;
 if(bothHot)setHot(target,weightedHeat(th,tc,sh,moved),t);
 target.amount=tc+moved;
 if(moved>=sc)return undefined;
 const remain=source.clone();remain.amount=sc-moved;return remain;
}
export function canManualMerge(a,b,t=now()){
 if(!sameForHeatMerge(a,b))return false;
 return isHot(a,t)===isHot(b,t);
}
export function mergeIntoContainer(container,incoming,t=now()){
 if(!incoming)return undefined;
 let remaining=incoming.clone();
 for(let i=0;i<container.size;i++){
  const target=container.getItem(i);if(!target||!canManualMerge(target,remaining,t))continue;
  const capacity=Math.max(0,target.maxAmount-target.amount);if(capacity<=0)continue;
  const moved=Math.min(capacity,remaining.amount);remaining=moveCount(target,remaining,moved,t);container.setItem(i,target);
  if(!remaining)return undefined;
 }
 try{return container.addItem(remaining)}catch{return remaining}
}
function normalCompatible(rep,stack,t){
 if(!sameForHeatMerge(rep,stack))return false;
 const rh=Math.max(0,hotUntil(rep)-t),sh=Math.max(0,hotUntil(stack)-t);
 if((rh>0)!==(sh>0))return false;
 if(rh<=0)return true;
 return Math.abs(rh-sh)<=NORMAL_HEAT_WINDOW;
}
export function compactSkewerContainer(container,fullSort=false,t=now()){
 const groups=[],nonSkewer=[];
 for(let slot=0;slot<container.size;slot++){
  const stack=container.getItem(slot);if(!stack)continue;
  if(!isSkewer(stack)){nonSkewer.push({slot,stack});continue}
  let group=groups.find(g=>fullSort?sameForHeatMerge(g.rep,stack):normalCompatible(g.rep,stack,t));
  if(!group){group={rep:stack.clone(),count:0,totalHeat:0};groups.push(group)}
  group.count+=stack.amount;group.totalHeat+=Math.max(0,hotUntil(stack)-t)*stack.amount;
 }
 if(!groups.length)return {changed:false,groups:0,stacks:0};
 const oldSkewerSlots=[];
 for(let i=0;i<container.size;i++)if(isSkewer(container.getItem(i)))oldSkewerSlots.push(i);
 for(const i of oldSkewerSlots)container.setItem(i,undefined);
 const out=[];
 for(const g of groups){
  const avg=g.count?Math.floor(g.totalHeat/g.count):0;let left=g.count;
  while(left>0){const s=g.rep.clone(),count=Math.min(s.maxAmount,left);s.amount=count;setHot(s,avg,t);out.push(s);left-=count}
 }
 const targets=[...oldSkewerSlots];
 while(targets.length<out.length){
  let empty=-1;for(let i=0;i<container.size;i++){if(!container.getItem(i)&&!targets.includes(i)){empty=i;break}}
  if(empty<0)break;targets.push(empty);
 }
 for(let i=0;i<out.length;i++){if(i<targets.length)container.setItem(targets[i],out[i]);}
 return {changed:true,groups:groups.length,stacks:out.length};
}
