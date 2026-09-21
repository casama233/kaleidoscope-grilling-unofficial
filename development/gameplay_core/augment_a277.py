from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,7]

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text((json.dumps(d,ensure_ascii=False,indent=2)+'\n') if isinstance(d,(dict,list)) else d,encoding='utf-8')
def replace_once(s,old,new,label):
 if old not in s:raise RuntimeError('A2.7.7 patch anchor missing: '+label)
 return s.replace(old,new,1)
def replace_between(s,start,end,new,label):
 i=s.find(start);j=s.find(end,i+len(start))
 if i<0 or j<0:raise RuntimeError('A2.7.7 range anchor missing: '+label)
 return s[:i]+new+s[j:]

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.7 Transaction Rollback BP'),(rm,'Kaleidoscope Grilling A2.7.7 Transaction Rollback RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.7 Transaction Rollback';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_7_Transaction_Rollback';write(P/'config.json',cfg)

def patch_runtime():
 shutil.copy2(DEV/'a277_grill_transaction_core.js',BP/'scripts/a277_grill_transaction_core.js')
 path=BP/'scripts/main.js';s=path.read_text(encoding='utf-8')

 anchor="import {chooseInteractionHand,makeIntent,intentMatches} from './a276_grill_intent_core.js';"
 s=replace_once(s,anchor,anchor+"\nimport {commitTwoParty,chooseExtractDelivery} from './a277_grill_transaction_core.js';",'transaction helper import')

 old="""function damageHandTool(player,hand,amount=1){
 if(creative(player))return false;
 const stack=heldByHand(player,hand);if(!stack)return false;
 try{
  const durability=stack.getComponent('minecraft:durability');if(!durability)return false;
  const next=nextDurability(durability.damage,durability.maxDurability,amount,!!durability.unbreakable);
  if(next.broken){setHand(player,hand,undefined);try{player.playSound('random.break',{volume:.8,pitch:1})}catch{};return true}
  if(next.damage!==durability.damage){durability.damage=next.damage;setHand(player,hand,stack)}
  return false;
 }catch{return false}
}"""
 new="""function planDamagedHand(player,hand,amount=1){
 const stack=heldByHand(player,hand);if(!stack)return {ok:false,reason:'missing'};
 const before=stack.clone();
 if(creative(player))return {ok:true,before,next:before.clone(),mutate:false,broken:false};
 try{
  const durability=stack.getComponent('minecraft:durability');if(!durability)return {ok:false,reason:'not_durable'};
  const plan=nextDurability(durability.damage,durability.maxDurability,amount,!!durability.unbreakable);
  if(plan.broken)return {ok:true,before,next:undefined,mutate:true,broken:true};
  const next=stack.clone(),d=next.getComponent('minecraft:durability');if(!d)return {ok:false,reason:'not_durable'};
  d.damage=plan.damage;return {ok:true,before,next,mutate:true,broken:false};
 }catch{return {ok:false,reason:'durability_error'}}
}
function commitGrillAndHand(block,beforeState,nextState,player,hand,beforeStack,nextStack,mutateHand=true){
 const r=commitTwoParty(
  ()=>writeState(block,nextState),
  ()=>{if(mutateHand&&!creative(player))setHand(player,hand,nextStack)},
  ()=>writeState(block,beforeState),
  ()=>{if(mutateHand&&!creative(player))setHand(player,hand,beforeStack)
 });
 return r.ok;
}"""
 s=replace_once(s,old,new,'state/resource transaction helper')

 new_extract_break="""function firstEmptyPlayerSlot(player){
 const c=mainContainer(player);if(!c)return -1;
 for(let i=0;i<c.size;i++)if(!c.getItem(i))return i;
 return -1;
}
function deliverExtractOutput(player,stack){
 const c=mainContainer(player),plan=chooseExtractDelivery(firstEmptyPlayerSlot(player));
 if(plan.kind==='inventory'&&c){c.setItem(plan.slot,stack);return true}
 player.dimension.spawnItem(stack,player.location);return true;
}
function extract(block,player,all=false){
 const state=readState(block);if(!canExtract(state))return 0;const c=inv(block);if(!c)return 0;let count=0;
 for(let i=0;i<3;i++){
  const raw=c.getItem(i);if(!raw)continue;
  let output;try{output=outputFor(raw,state,outputKind(state))}catch{break}
  try{c.setItem(i,undefined)}catch{break}
  try{deliverExtractOutput(player,output)}
  catch{try{c.setItem(i,raw)}catch{};message(player,'§c取串失敗，原串已嘗試回滾');break}
  count++;if(!all)break;
 }
 if(occupied(block)===0)resetBlock(block,state.lit);
 if(count)try{block.dimension.playSound('random.pop',block.location)}catch{}
 return count;
}
function removeEscrow(entities){for(const e of entities)try{e?.remove()}catch{}}
function restoreBrokenGrill(dim,loc,permutation,state,raws){
 try{
  let b=dim.getBlock(loc);if(!b)return;
  b.setPermutation(permutation);b=dim.getBlock(loc)??b;
  const c=inv(b);if(c)for(let i=0;i<3;i++)c.setItem(i,raws[i]);
  writeState(b,state);
 }catch{}
}
function customBreak(block,player){
 if(!block?.isValid||block.typeId!==GRILL_ID)return;
 const state=readState(block),kind=breakDisposition(state),c=inv(block),dim=block.dimension,loc={...block.location},permutation=block.permutation;
 const raws=[0,1,2].map(i=>c?.getItem(i)),drops=[];
 try{
  for(const raw of raws)if(raw)drops.push(outputFor(raw,state,kind));
  if(!creative(player))drops.push(new ItemStack(GRILL_ID,1));
 }catch{message(player,'§c拆除失敗：無法建立掉落物');return}
 const escrow=[];
 try{
  for(let i=0;i<drops.length;i++)escrow.push(dim.spawnItem(drops[i],{x:loc.x+.5,y:loc.y+(i===drops.length-1&&!creative(player)?.3:.4),z:loc.z+.5}));
 }catch{
  removeEscrow(escrow);message(player,'§c拆除失敗：掉落物生成失敗');return;
 }
 try{
  clearContainer(block);clearState(block);removeGrillLegs(block);block.setType('minecraft:air');
 }catch{
  removeEscrow(escrow);restoreBrokenGrill(dim,loc,permutation,state,raws);message(player,'§c拆除失敗，烤架內容已嘗試回滾');
 }
}
"""
 s=replace_between(s,'function extract(block,player,all=false){','function cookeryOilType(stack){',new_extract_break,'extract/break transactions')

 new_plans="""function planCookeryOil(player,hand,needed){
 const stack=heldByHand(player,hand);if(stack?.typeId!==COOKERY_FILLED)return {ok:false,reason:'not_pot'};
 const count=cookeryOilCount(stack);if(count<needed)return {ok:false,reason:'insufficient',count};
 const type=cookeryOilType(stack),before=stack.clone(),heat=heatForOil(type);
 if(creative(player))return {ok:true,heat,remaining:count,before,next:before.clone(),mutate:false};
 const remaining=count-needed,next=new ItemStack(remaining>0?COOKERY_FILLED:COOKERY_POT,1),cap=type?FLUID_CAPACITY:256;
 if(remaining>0){try{next.setLore(['§7Oil: '+remaining+'/'+cap]);next.setDynamicProperty(COOKERY_OIL_KEY,remaining);if(type)next.setDynamicProperty('kaleidoscope_grilling:oil_type',type)}catch{}}
 return {ok:true,heat,remaining,before,next,mutate:true};
}
function planSeasoningBottle(player,hand,needed){
 const stack=heldByHand(player,hand);if(stack?.typeId!==SEASONING_ID)return {ok:false,reason:'not_seasoning'};
 const uses=getUses(stack),remaining=16-uses;if(remaining<needed)return {ok:false,reason:'insufficient',remaining};
 const ingredients=readSeasonings(stack),before=stack.clone();
 if(creative(player))return {ok:true,ingredients,uses,before,next:before.clone(),mutate:false};
 const nextUses=uses+needed;
 if(nextUses>=16)return {ok:true,ingredients,uses:nextUses,before,next:new ItemStack(EMPTY_SEASONING_ID,1),mutate:true};
 const next=stack.clone();setUses(next,nextUses);try{next.setLore(['§7Uses: '+(16-nextUses)+'/16'])}catch{}
 return {ok:true,ingredients,uses:nextUses,before,next,mutate:true};
}
"""
 s=replace_between(s,'function consumeCookeryOil(player,hand,needed){','function handleGrill(block,player,hand=',new_plans,'resource planning')

 old_flint="""if(id==='minecraft:flint_and_steel'){
  if(!state.lit){state=light(state,true);writeState(block,state);damageHandTool(player,hand,1);try{block.dimension.playSound('fire.ignite',block.location)}catch{}message(player,'§6烤爐已點火')}
  return
 }"""
 new_flint="""if(id==='minecraft:flint_and_steel'){
  if(!state.lit){
   const tool=planDamagedHand(player,hand,1),nextState=light(state,true);
   if(!tool.ok){message(player,'§c點火失敗：打火石狀態無法提交');return}
   if(!commitGrillAndHand(block,state,nextState,player,hand,tool.before,tool.next,tool.mutate)){message(player,'§c點火交易失敗，已嘗試回滾');return}
   if(tool.broken)try{player.playSound('random.break',{volume:.8,pitch:1})}catch{}
   try{block.dimension.playSound('fire.ignite',block.location)}catch{}message(player,'§6烤爐已點火')
  }
  return
 }"""
 s=replace_once(s,old_flint,new_flint,'transactional ignition')

 old_oil="""if(id===COOKERY_FILLED){
  if(state.phase!==0||n<1){message(player,'§7現在不能刷油');return}
  const oil=consumeCookeryOil(player,hand,n);if(!oil.ok){message(player,oil.reason==='insufficient'?'§c油量不足：需要 '+n+'，目前 '+oil.count:'§7需要森羅物語裝油的油壺');return}
  const result=brush(state,n,oil.heat);if(result.ok){writeState(block,result.state);try{player.playAnimation('animation.kg_imm.player.brush.'+hand,{blendOutTime:.12})}catch{}message(player,'§e刷油完成，消耗 '+(creative(player)?0:n)+' 點油')}return;
 }"""
 new_oil="""if(id===COOKERY_FILLED){
  if(state.phase!==0||n<1){message(player,'§7現在不能刷油');return}
  const oil=planCookeryOil(player,hand,n);if(!oil.ok){message(player,oil.reason==='insufficient'?'§c油量不足：需要 '+n+'，目前 '+oil.count:'§7需要森羅物語裝油的油壺');return}
  const result=brush(state,n,oil.heat);
  if(result.ok){
   if(!commitGrillAndHand(block,state,result.state,player,hand,oil.before,oil.next,oil.mutate)){message(player,'§c刷油交易失敗，油與烤架已嘗試回滾');return}
   try{player.playAnimation('animation.kg_imm.player.brush.'+hand,{blendOutTime:.12})}catch{}message(player,'§e刷油完成，消耗 '+(creative(player)?0:n)+' 點油')
  }return;
 }"""
 s=replace_once(s,old_oil,new_oil,'transactional oil')

 old_season="""if(id===SEASONING_ID){
  if(state.phase!==2||state.seasoned||n<1){message(player,'§7現在不能撒料');return}
  const bottle=consumeSeasoningBottle(player,hand,n);if(!bottle.ok){message(player,bottle.reason==='insufficient'?'§c調料不足：爐上 '+n+' 串需要 '+n+' 次，剩 '+bottle.remaining+' 次':'§7需要完成的調料瓶');return}
  const result=season(state,n,bottle.ingredients);if(result.ok){writeState(block,result.state);try{player.playAnimation('animation.kg_imm.player.season.'+hand,{blendOutTime:.12})}catch{}message(player,'§a調味完成，消耗 '+(creative(player)?0:n)+' 次')}return;
 }"""
 new_season="""if(id===SEASONING_ID){
  if(state.phase!==2||state.seasoned||n<1){message(player,'§7現在不能撒料');return}
  const bottle=planSeasoningBottle(player,hand,n);if(!bottle.ok){message(player,bottle.reason==='insufficient'?'§c調料不足：爐上 '+n+' 串需要 '+n+' 次，剩 '+bottle.remaining+' 次':'§7需要完成的調料瓶');return}
  const result=season(state,n,bottle.ingredients);
  if(result.ok){
   if(!commitGrillAndHand(block,state,result.state,player,hand,bottle.before,bottle.next,bottle.mutate)){message(player,'§c撒料交易失敗，調料與烤架已嘗試回滾');return}
   try{player.playAnimation('animation.kg_imm.player.season.'+hand,{blendOutTime:.12})}catch{}message(player,'§a調味完成，消耗 '+(creative(player)?0:n)+' 次')
  }return;
 }"""
 s=replace_once(s,old_season,new_season,'transactional seasoning')

 path.write_text(s,encoding='utf-8')

def report():
 write(P/'reports/a277-grill-transaction-rollback.json',{
  'version':'A2.7.7',
  'scope':'grill commit ordering and rollback only; no new content',
  'java_baseline':'breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c',
  'fixes':{
   'state_resource_commits':{
    'status':'fixed',
    'covers':['flint_and_steel ignition','Cookery oil brush','special seasoning'],
    'policy':'apply grill state then used-hand resource; on either exception restore both snapshots best-effort'
   },
   'extract':{
    'status':'fixed',
    'policy':'prepare output -> clear grill source -> deliver to one known-empty inventory slot or spawn -> restore source on delivery exception'
   },
   'break':{
    'status':'fixed',
    'policy':'spawn all intended drops as escrow while source still intact -> commit container/state/block removal -> remove escrow and restore grill snapshot on commit exception',
    'escrow_cleanup_api':'Entity.remove()'
   }
  },
  'known_boundaries':[
   'When the player inventory has no empty slot, extraction intentionally spawns the output at the player instead of attempting a potentially-partial merge into a full inventory. Java placeItemBackInInventory may merge into a compatible partial stack.',
   'Rollback is best-effort if the underlying engine itself throws again while restoring a snapshot.',
   'The temporary escrow entities during custom break exist only inside one synchronous callback; script callbacks do not interleave during that commit section.',
   'Minecraft/BDS engine acceptance remains required.'
  ],
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,6]:raise RuntimeError('A2.7.7 must augment verified A2.7.6')
 patch_versions();patch_runtime();report();print('A2.7.7 grill transaction rollback complete')
if __name__=='__main__':main()
