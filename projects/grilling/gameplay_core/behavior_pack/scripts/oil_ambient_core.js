/** Java PremiumChiliOilBlock.animateTick positions/chance; server sampling is bounded. */
export function premiumOilParticles(random=Math.random){
 if(random()>=.2)return [];
 const offset=[.15+random()*.7,.75+random()*.2,.15+random()*.7];
 const result=[{id:'kaleidoscope_grilling:feedback_lava',offset,velocity:[0,.05,0]}];
 if(random()<.5)result.push({id:'kaleidoscope_grilling:feedback_basic_flame',offset,velocity:[0,.035,0]});
 return result;
}
/** Java ClientSoundHandler.spawnPremiumOilPotParticles, distinct from ground oil. */
export function premiumOilPotParticles(random=Math.random){
 if(random()>=.2)return [];
 const offset=[.42+random()*.16,.72,.42+random()*.16];
 return [
  {id:'kaleidoscope_grilling:feedback_lava',offset,velocity:[0,.14,0]},
  {id:'kaleidoscope_grilling:feedback_basic_flame',offset,velocity:[0,.11,0]}
 ];
}
export function premiumOilPotInRange(station,player){
 const p=player.location;
 return station.dimensionId===player.dimension.id&&Math.abs(station.x-Math.floor(p.x))<=8&&
  Math.abs(station.y-Math.floor(p.y))<=4&&Math.abs(station.z-Math.floor(p.z))<=8;
}
