// Generated from reviewed public source; unknown actor categories use an explicit neutral adaptation.
export const TELEPORT_ORIGIN_SOUND_ID="kg_java21.teleport";
export const FLATULENCE_SOUND_ID="kg_cookery.flatulence";
const REVIEWED_DESTINATION_SOUNDS=Object.freeze({"minecraft:bat":"kg_java21.teleport_neutral","minecraft:cow":"kg_java21.teleport_neutral","minecraft:player":"kg_java21.teleport","minecraft:zombie":"kg_java21.teleport_hostile"});
export function teleportDestinationAudio(typeId){
 const known=Object.hasOwn(REVIEWED_DESTINATION_SOUNDS,typeId);
 return {soundId:known?REVIEWED_DESTINATION_SOUNDS[typeId]:"kg_java21.teleport_neutral",categoryReviewed:known};
}
