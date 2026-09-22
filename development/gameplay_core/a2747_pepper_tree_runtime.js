import {world,system,ItemStack,BlockPermutation} from '@minecraft/server';
import {getMainHand,getOffHand,setHand,findHandEntry,isCreative} from './a2735_player_io.js';
import {
 PEPPER_LOG_ID,PEPPER_LEAVES_ID,PEPPER_SAPLING_ID,SICHUAN_PEPPER_ID,
 LEAVES_COMPONENT_ID,SAPLING_COMPONENT_ID,LOG_COMPONENT_ID,
 HAS_PEPPER_STATE,PERSISTENT_STATE,SAPLING_STAGE_STATE,LEAF_DECAY_DISTANCE,STING_INTERVAL_TICKS,
 shouldFruitPepperLeaf,harvestedPepperCount,saplingBonemealSucceeds,saplingRandomTickSucceeds,
 nextSaplingAction,pepperTreeHeight,pepperLogAxis,pepperLeafBreakPlan,pepperTreePlan
} from './a2747_pepper_tree_core.js';

const STING_UNTIL='kaleidoscope_grilling:pepper_sting_until';
const REPLACEABLE=new Set(['minecraft:air','minecraft:short_grass','minecraft:tall_grass','minecraft:snow_layer','minecraft:vine']);
const AXES=new Set(['minecraft:wooden_axe','minecraft:stone_axe','minecraft:iron_axe','minecraft:golden_axe','minecraft:diamond_axe','minecraft:netherite_axe']);
const DIRS=[[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]];

function at(d,loc,dx=0,dy=0,dz=0){
 try{return d.getBlock({x:loc.x+dx,y:loc.y+dy,z:loc.z+dz})}catch{return undefined}
}
function state(block,key,fallback){
 try{const v=block?.permutation?.getState(key);return v===undefined?fallback:v}catch{return fallback}
}
function setState(block,key,value){
 try{block.setPermutation(block.permutation.withState(key,value));return true}catch{return false}
}
function drop(block,id,count=1){
 if(!block||count<=0)return;
 try{block.dimension.spawnItem(new ItemStack(id,count),{x:block.x+.5,y:block.y+.4,z:block.z+.5})}catch{}
}
function lightAbove(block){
 try{return Number(block.dimension.getLightLevel({x:block.x,y:block.y+1,z:block.z}))||0}catch{return 0}
}
function isDirt(block){
 try{return !!block?.hasTag('dirt')}catch{return ['minecraft:dirt','minecraft:grass_block','minecraft:coarse_dirt','minecraft:podzol','minecraft:rooted_dirt','minecraft:mycelium'].includes(block?.typeId)}
}
function isReplaceable(block,origin=false){
 if(!block)return false;
 if(origin&&block.typeId===PEPPER_SAPLING_ID)return true;
 return REPLACEABLE.has(block.typeId);
}
function isAxe(stack){
 if(!stack)return false;
 try{if(stack.hasTag('minecraft:is_axe'))return true}catch{}
 return AXES.has(stack.typeId);
}
function heldAxe(player){
 const m=getMainHand(player);if(isAxe(m))return {hand:'main',stack:m};
 const o=getOffHand(player);if(isAxe(o))return {hand:'off',stack:o};
 return null;
}
function damageTool(player,entry){
 if(!entry||isCreative(player))return;
 try{
  const stack=entry.stack,d=stack.getComponent('minecraft:durability');if(!d)return;
  const next=(Number(d.damage)||0)+1;
  if(next>=Number(d.maxDurability||0))setHand(player,entry.hand,undefined);
  else{d.damage=next;setHand(player,entry.hand,stack)}
 }catch{}
}
function consumeOne(player,entry){
 if(!entry||isCreative(player))return;
 try{
  const s=entry.stack;if(s.amount<=1)setHand(player,entry.name,undefined);
  else{s.amount-=1;setHand(player,entry.name,s)}
 }catch{}
}
function enchantLevel(stack,id){
 try{return Math.max(0,Number(stack?.getComponent('minecraft:enchantable')?.getEnchantment(id)?.level??0)||0)}catch{return 0}
}

function connectedToPepperLog(start){
 const d=start.dimension,base=start.location,queue=[{x:base.x,y:base.y,z:base.z,dist:0}],seen=new Set([base.x+'|'+base.y+'|'+base.z]);
 while(queue.length){
  const cur=queue.shift();
  if(cur.dist>=LEAF_DECAY_DISTANCE)continue;
  for(const [dx,dy,dz] of DIRS){
   const p={x:cur.x+dx,y:cur.y+dy,z:cur.z+dz},k=p.x+'|'+p.y+'|'+p.z;if(seen.has(k))continue;seen.add(k);
   let b;try{b=d.getBlock(p)}catch{continue}
   if(!b)continue;
   if(b.typeId===PEPPER_LOG_ID)return true;
   if(b.typeId===PEPPER_LEAVES_ID)queue.push({...p,dist:cur.dist+1});
  }
 }
 return false;
}

function leafPermutation(hasPepper=false,persistent=false){
 return BlockPermutation.resolve(PEPPER_LEAVES_ID,{
  [HAS_PEPPER_STATE]:!!hasPepper,
  [PERSISTENT_STATE]:!!persistent
 });
}
function logPermutation(){
 return BlockPermutation.resolve(PEPPER_LOG_ID,{'minecraft:block_face':'up'});
}
function placePepperTree(sapling){
 const h=pepperTreeHeight(Math.random()),d=sapling.dimension,o=sapling.location;
 if(!isDirt(at(d,o,0,-1,0)))return false;
 for(let y=0;y<h+3;y++)if(!isReplaceable(at(d,o,0,y,0),y===0))return false;
 const randomValues=Array.from({length:96},()=>Math.random()),plan=pepperTreePlan(h,randomValues);
 try{
  for(const p of plan.logs)d.setBlockPermutation({x:o.x+p.x,y:o.y+p.y,z:o.z+p.z},logPermutation());
  for(const p of plan.leaves){
   const b=at(d,o,p.x,p.y,p.z);if(!b||b.typeId!=='minecraft:air')continue;
   d.setBlockPermutation(b.location,leafPermutation(p.hasPepper,false));
  }
  return true;
 }catch{return false}
}
function advanceSapling(block){
 const stage=Number(state(block,SAPLING_STAGE_STATE,0))||0;
 if(nextSaplingAction(stage)==='advance')return setState(block,SAPLING_STAGE_STATE,1);
 return placePepperTree(block);
}

function sting(entity){
 if(!entity||entity.typeId==='minecraft:fox'||entity.typeId==='minecraft:bee')return;
 try{entity.addEffect('slowness',10,{amplifier:0,showParticles:false})}catch{}
 const now=system.currentTick;
 try{
  const until=Number(entity.getDynamicProperty(STING_UNTIL)??0);
  if(now<until)return;
  entity.applyDamage(1);
  entity.setDynamicProperty(STING_UNTIL,now+STING_INTERVAL_TICKS);
 }catch{}
}

function breakLeaves(block,player,tool,hasPepper){
 if(!block||block.typeId!==PEPPER_LEAVES_ID)return;
 const creative=isCreative(player);
 try{block.setType('minecraft:air')}catch{return}
 if(creative)return;
 const fortune=enchantLevel(tool,'fortune')||enchantLevel(tool,'minecraft:fortune');
 const silk=(enchantLevel(tool,'silk_touch')||enchantLevel(tool,'minecraft:silk_touch'))>0;
 const plan=pepperLeafBreakPlan({
  shears:tool?.typeId==='minecraft:shears',silkTouch:silk,fortune,hasPepper,
  saplingRandom:Math.random(),stickRandom:Math.random()
 });
 if(plan.leaves)drop(block,PEPPER_LEAVES_ID,plan.leaves);
 if(plan.saplings)drop(block,PEPPER_SAPLING_ID,plan.saplings);
 if(plan.sticks)drop(block,'minecraft:stick',plan.sticks);
 if(plan.pepper)drop(block,SICHUAN_PEPPER_ID,plan.pepper);
 try{block.dimension.playSound('dig.grass',block.location)}catch{}
}

system.beforeEvents.startup.subscribe(init=>{
 init.blockComponentRegistry.registerCustomComponent(LEAVES_COMPONENT_ID,{
  beforeOnPlayerPlace(event){
   try{event.permutationToPlace=event.permutationToPlace.withState(PERSISTENT_STATE,true).withState(HAS_PEPPER_STATE,false)}catch{}
  },
  onRandomTick(event){
   try{
    const block=event.block;
    if(!state(block,PERSISTENT_STATE,false)&&!connectedToPepperLog(block)){block.setType('minecraft:air');return}
    if(!state(block,HAS_PEPPER_STATE,false)&&shouldFruitPepperLeaf(Math.random()))setState(block,HAS_PEPPER_STATE,true);
   }catch{}
  },
  onPlayerInteract(event){
   try{
    const block=event.block,player=event.player;if(!player||getMainHand(player))return;
    if(!state(block,HAS_PEPPER_STATE,false))return;
    drop(block,SICHUAN_PEPPER_ID,harvestedPepperCount(Math.random()));
    setState(block,HAS_PEPPER_STATE,false);
    block.dimension.playSound('block.sweet_berry_bush.pick',block.location,{volume:1,pitch:.8+Math.random()*.4});
   }catch{}
  },
  onStepOn(event){sting(event.entity)}
 });

 init.blockComponentRegistry.registerCustomComponent(SAPLING_COMPONENT_ID,{
  beforeOnPlayerPlace(event){
   try{
    const below=at(event.dimension,event.block.location,0,-1,0);
    if(!isDirt(below)){event.cancel=true;return}
    event.permutationToPlace=event.permutationToPlace.withState(SAPLING_STAGE_STATE,0);
   }catch{event.cancel=true}
  },
  onRandomTick(event){
   try{if(saplingRandomTickSucceeds(lightAbove(event.block),Math.random()))advanceSapling(event.block)}catch{}
  },
  onPlayerInteract(event){
   try{
    const p=event.player;if(!p)return;
    const meal=findHandEntry(p,'minecraft:bone_meal');if(!meal)return;
    consumeOne(p,meal);
    if(saplingBonemealSucceeds(Math.random()))advanceSapling(event.block);
   }catch{}
  }
 });

 init.blockComponentRegistry.registerCustomComponent(LOG_COMPONENT_ID,{
  onPlayerInteract(event){
   try{
    const player=event.player,block=event.block;if(!player)return;
    const axe=heldAxe(player);if(!axe)return;
    const axis=pepperLogAxis(state(block,'minecraft:block_face','up'));
    block.setPermutation(BlockPermutation.resolve('minecraft:stripped_oak_log',{pillar_axis:axis}));
    damageTool(player,axe);
    block.dimension.playSound('dig.wood',block.location,{volume:.8,pitch:1.1});
   }catch{}
  }
 });
});

world.beforeEvents.playerBreakBlock.subscribe(e=>{
 try{
  if(e.block.typeId!==PEPPER_LEAVES_ID)return;
  const loc={...e.block.location},dim=e.block.dimension,p=e.player,tool=e.itemStack?.clone(),hasPepper=!!state(e.block,HAS_PEPPER_STATE,false);
  e.cancel=true;system.run(()=>breakLeaves(dim.getBlock(loc),p,tool,hasPepper));
 }catch{}
});
