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

// Stable Script API has no collision-shape/face-sturdiness query. Resolve the
// vanilla shape families needed by plates and wall recipes separately from the
// bottle's top-support rule. Unknown add-on geometry is not proof of support;
// undefined keeps an existing attachment intact while denying a new placement.
const NON_CUBE_IDS=new Set([
 'farmland','dirt_path','grass_path','soul_sand','enchanting_table','daylight_detector',
 'daylight_detector_inverted','cactus','honey_block','snow_layer','powder_snow','brewing_stand',
 'cauldron','water_cauldron','lava_cauldron','composter','hopper','lectern','stonecutter_block',
 'grindstone','bell','dragon_egg','end_portal_frame','end_portal','nether_portal','portal',
 'piston_arm_collision','sticky_piston_arm_collision','moving_block','scaffolding',
 'bamboo','bamboo_sapling','pointed_dripstone','cocoa','cake','turtle_egg','sniffer_egg',
 'conduit','sea_pickle','flower_pot','decorated_pot','heavy_core','light_block','structure_void',
 'azalea','flowering_azalea','pink_petals','wildflowers','leaf_litter','tripwire_hook','trip_wire',
 'powered_repeater','unpowered_repeater','powered_comparator','unpowered_comparator','repeater','comparator',
 'lever','waterlily','lily_pad','nether_sprouts','nether_wart','resin_clump','mud'
]);
const NON_CUBE_NAME=/(?:^|_)(?:slab|stairs|sapling|flower|tulip|orchid|mushroom|torch|carpet|rail|vine|vines|roots|grass|fern|bush|button|pressure_plate|fence|fence_gate|wall|door|trapdoor|sign|banner|ladder|candle|fire|wire|web|sugar_cane|wheat|carrots|potatoes|beetroot|seagrass|kelp|pane|chain|lantern|bed|chest|anvil|skull|head|coral_fan|coral_wall_fan|amethyst_cluster|amethyst_bud|dripleaf|hanging_roots)(?:_|$)/;
const FULL_CUBE_IDS=new Set([
 'stone','granite','diorite','andesite','polished_granite','polished_diorite','polished_andesite','smooth_stone',
 'cobblestone','mossy_cobblestone','bedrock','dirt','coarse_dirt','podzol','rooted_dirt','dirt_with_roots','grass_block','mycelium',
 'sand','red_sand','gravel','clay','terracotta','hardened_clay','snow','snow_block','ice','packed_ice','blue_ice','frosted_ice',
 'glass','tinted_glass','obsidian','crying_obsidian','netherrack','end_stone','soul_soil','basalt','smooth_basalt','polished_basalt',
 'blackstone','gilded_blackstone','polished_blackstone','deepslate','cobbled_deepslate','polished_deepslate','calcite','tuff','polished_tuff','packed_mud',
 'sandstone','cut_sandstone','smooth_sandstone','chiseled_sandstone','red_sandstone','cut_red_sandstone','smooth_red_sandstone','chiseled_red_sandstone',
 'prismarine','dark_prismarine','sponge','wet_sponge','glowstone','sea_lantern','shroomlight','slime','slime_block',
 'mushroom_stem','brown_mushroom_block','red_mushroom_block','crimson_stem','warped_stem','stripped_crimson_stem','stripped_warped_stem',
 'moss_block','pale_moss_block','muddy_mangrove_roots','melon_block','melon','pumpkin','carved_pumpkin','lit_pumpkin','jack_o_lantern',
 'crafting_table','cartography_table','fletching_table','smithing_table','loom','barrel','bookshelf','chiseled_bookshelf',
 'furnace','lit_furnace','blast_furnace','lit_blast_furnace','smoker','lit_smoker','dispenser','dropper','observer',
 'noteblock','jukebox','target','dried_kelp_block','hay_block','bone_block','beehive','bee_nest','tnt',
 'brick_block','nether_brick','red_nether_brick','stonebrick','end_bricks','quartz_block','quartz_pillar','chiseled_quartz_block','smooth_quartz','purpur_block','purpur_pillar',
 'coal_block','iron_block','raw_iron_block','gold_block','raw_gold_block','diamond_block','emerald_block','lapis_block','redstone_block','netherite_block','raw_copper_block',
 'amethyst_block','budding_amethyst','dripstone_block','nether_wart_block','warped_wart_block','honeycomb_block'
]);
const FULL_CUBE_NAME=/(?:_planks|_log|_wood|_hyphae|_leaves|_ore|_bricks|_tiles|_terracotta|_concrete|_concrete_powder|_wool|_stained_glass|_nylium|_froglight|_coral_block)$/;
export function hasFullCubeCollision(block){
 if(!block)return undefined;
 const id=block.typeId,states=block.permutation.getAllStates();
 if(block.isAir||block.isLiquid||/^minecraft:(?:air|water|flowing_water|lava|flowing_lava)$/.test(id))return false;
 if(id==='kaleidoscope_grilling:pepper_log')return true;
 if(id==='kaleidoscope_grilling:pepper_leaves')return false;
 if(id==='kaleidoscope_cookery:table')return false;
 if(!id.startsWith('minecraft:'))return undefined;
 const name=id.slice(10);
 if(name.includes('double_slab'))return true;
 if(NON_CUBE_IDS.has(name))return false;
 if(FULL_CUBE_IDS.has(name))return true;
 if(/^(?:waxed_)?(?:(?:exposed|weathered|oxidized)_)?(?:copper|copper_block|cut_copper|chiseled_copper)$/.test(name))return true;
 if(NON_CUBE_NAME.test(name))return false;
 if(FULL_CUBE_NAME.test(name))return true;
 // Do not infer an arbitrary future vanilla/add-on shape from solidity or a
 // generic "_block" suffix. Stateful shapes (e.g. pistons) need their own proof.
 return undefined;
}

const SIDE_OFFSET={north:{x:0,y:0,z:-1},south:{x:0,y:0,z:1},west:{x:-1,y:0,z:0},east:{x:1,y:0,z:0}};
const OPPOSITE_SIDE={north:'south',south:'north',west:'east',east:'west'};
function stairState(block){
 if(!block?.typeId?.startsWith('minecraft:')||!block.typeId.endsWith('_stairs'))return undefined;
 const states=block.permutation.getAllStates(),facing=states['minecraft:cardinal_direction']??['east','west','south','north'][states.weirdo_direction];
 return SIDE_OFFSET[facing]?{facing,top:states.upside_down_bit===true||states['minecraft:vertical_half']==='top',corner:states['minecraft:corner']}:undefined;
}
function sideNeighbor(block,face){
 const off=SIDE_OFFSET[face];return block.dimension.getBlock({x:block.x+off.x,y:block.y,z:block.z+off.z});
}
function stairSturdySide(block,side){
 const own=stairState(block);if(!own)return undefined;
 // Use a resolved corner when available; otherwise derive it from neighboring
 // stairs with Java StairBlock's front outer / back inner decisions.
 if(own.corner!==undefined){
  if(own.corner==='none')return side===own.facing;
  if(own.corner==='outer_left'||own.corner==='outer_right')return false;
  const clockwise={north:'east',east:'south',south:'west',west:'north'},counterclockwise={north:'west',west:'south',south:'east',east:'north'};
  if(own.corner==='inner_left')return side===own.facing||side===counterclockwise[own.facing];
  if(own.corner==='inner_right')return side===own.facing||side===clockwise[own.facing];
  return undefined;
 }
 const parallel=(a,b)=>a===b||a===OPPOSITE_SIDE[b];
 const mayTurn=direction=>{const next=sideNeighbor(block,direction);if(!next)return undefined;const stair=stairState(next);return !stair||stair.facing!==own.facing||stair.top!==own.top};
 const front=sideNeighbor(block,own.facing);if(!front)return undefined;
 const outer=stairState(front);
 if(outer&&outer.top===own.top&&!parallel(outer.facing,own.facing)){
  const turn=mayTurn(OPPOSITE_SIDE[outer.facing]);if(turn===undefined)return undefined;
  if(turn)return false; // An outer corner has no complete vertical face.
 }
 const back=sideNeighbor(block,OPPOSITE_SIDE[own.facing]);if(!back)return undefined;
 const inner=stairState(back);
 if(inner&&inner.top===own.top&&!parallel(inner.facing,own.facing)){
  const turn=mayTurn(inner.facing);if(turn===undefined)return undefined;
  if(turn)return side===own.facing||side===inner.facing;
 }
 return side===own.facing;
}
export function hasSturdySide(block,face){
 const side=String(face??'').toLowerCase();if(!SIDE_OFFSET[side])return false;
 if(!block)return undefined;
 const id=block.typeId;
 // Java support shapes differ from collision shapes: leaves expose no support,
 // soul sand overrides support to a full cube, and a composter's four outside
 // walls are complete even though its hollow collision is not a full cube.
 if(id==='kaleidoscope_grilling:pepper_leaves'||/^minecraft:(?:.*_leaves|leaves|leaves2)$/.test(id))return false;
 if(id==='minecraft:soul_sand'||id==='minecraft:composter')return true;
 if(id==='minecraft:trapdoor'||(id?.startsWith('minecraft:')&&id.endsWith('_trapdoor'))){
  const states=block.permutation.getAllStates();
  if(states.open_bit===false)return false;
  if(states.open_bit!==true)return undefined;
  // Official Intrinsic Block States List includes trapdoors in the direction
  // domain (0 south, 1 west, 2 north, 3 east). Native four-facing acceptance is
  // still required; an unreadable/unknown direction never detaches a recipe.
  const facing=states['minecraft:cardinal_direction']??['south','west','north','east'][states.direction];
  return SIDE_OFFSET[facing]?side===OPPOSITE_SIDE[facing]:undefined;
 }
 if(block.typeId?.endsWith('_stairs'))return stairSturdySide(block,side);
 return hasFullCubeCollision(block);
}
