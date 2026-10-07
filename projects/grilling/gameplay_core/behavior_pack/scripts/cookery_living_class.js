// Class-only native mapping for Cookery's Java LivingEntity damage gates.
// Reuses the reviewed World Liquor isLivingCombatEntity contract: health plus
// player, armor stand or native mob family. Health-bearing vehicles are not
// thereby living. Arbitrary custom Java inheritance is not exposed by this API.
// Do not add a current-health/positive-damage gate absent from HinderEvent.
export function isCookeryLivingEntity(actor){
 try{return !!actor?.getComponent?.('minecraft:health')&&(actor.typeId==='minecraft:player'||actor.typeId==='minecraft:armor_stand'||actor.getComponent('minecraft:type_family')?.hasTypeFamily('mob')===true);}catch{return false;}
}
