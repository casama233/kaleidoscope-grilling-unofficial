/** Java PremiumChiliOilBlock.animateTick positions/chance; server sampling is bounded. */
export function premiumOilParticles(random=Math.random){
 if(random()>=.2)return [];
 const offset=[.15+random()*.7,.75+random()*.2,.15+random()*.7];
 const result=[{id:'kaleidoscope_grilling:feedback_lava',offset,velocity:[0,.05,0]}];
 if(random()<.5)result.push({id:'kaleidoscope_grilling:feedback_basic_flame',offset,velocity:[0,.035,0]});
 return result;
}
