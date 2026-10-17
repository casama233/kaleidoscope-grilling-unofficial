// Java 1.1.1 DragonEggPowderHandler: a knife shaves powder; the egg is not consumed.
export function dragonPowderCount(looting=0,random=0){
 const level=Math.max(0,Math.floor(Number(looting)||0));
 const roll=Math.max(0,Math.min(.999999999999,Number(random)||0));
 return 1+Math.floor(roll*(level+1));
}
export function knifeDamagePlan(damage,max,unbreaking=0,random=0,creative=false){
 if(creative)return {mutate:false,broken:false,damage};
 if(!Number.isFinite(damage)||!Number.isFinite(max)||max<=0)throw Error('Knife durability unavailable');
 const level=Math.max(0,Math.floor(Number(unbreaking)||0));
 if(random>=1/(level+1))return {mutate:false,broken:false,damage};
 const next=damage+1;return {mutate:true,broken:next>=max,damage:Math.min(max,next)};
}
