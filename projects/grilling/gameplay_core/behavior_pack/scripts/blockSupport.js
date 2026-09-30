// Block.isSolid is not exposed by this stable BDS, despite appearing in mocks.
// Preserve the port's approximate top-support rule on the stable block API.
export function hasSolidTop(block){
 if(!block||block.isAir||block.isLiquid)return false;
 if(typeof block.isSolid==='boolean')return block.isSolid;
 const id=block.typeId,states=block.permutation.getAllStates();
 if(Object.hasOwn(states,'kaleidoscope_cookery:table_axis'))return true;
 if(id.includes('double_slab'))return true;
 if(id.endsWith('_slab'))return states['minecraft:vertical_half']==='top'||states['top_slot_bit']===true;
 if(id.endsWith('_stairs'))return states['upside_down_bit']===true;
 if(id==='minecraft:snow_layer')return Number(states.height??0)>=7;
 if(/(?:air|water|lava)$/.test(id))return false;
 if(id.endsWith('_block'))return true;
 if(['minecraft:farmland','minecraft:dirt_path','minecraft:grass_path','minecraft:soul_sand','minecraft:enchanting_table','minecraft:daylight_detector'].includes(id))return false;
 if(/(?:sapling|flower|tulip|orchid|mushroom|torch|carpet|rail|vine|roots|grass|fern|bush|button|pressure_plate|fence|wall|door|trapdoor|sign|banner|ladder|candle|fire|wire|web|sugar_cane|wheat|carrots|potatoes|beetroot|seagrass|kelp)/.test(id))return false;
 return true;
}
