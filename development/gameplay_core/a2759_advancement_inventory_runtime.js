import {RAW_TO_COOKED} from './data.js';
import {playerInventory,getOffHand} from './a2735_player_io.js';
import {awardOneShotAdvancement} from './a2753_advancement_runtime.js';
import {INVENTORY_ADVANCEMENTS,inventoryAdvancementIds} from './a2759_advancement_inventory_core.js';

const RAW_SKEWER_IDS=Object.freeze(Object.keys(RAW_TO_COOKED));

function inventoryItemIds(player){
 const out=[],container=playerInventory(player);
 if(container)for(let i=0;i<container.size;i++){const stack=container.getItem(i);if(stack)out.push(stack.typeId)}
 const off=getOffHand(player);if(off)out.push(off.typeId);
 return out;
}

export function awardInventoryAdvancements(player){
 if(!player)return 0;
 const ids=inventoryAdvancementIds(inventoryItemIds(player),RAW_SKEWER_IDS,player.dimension?.id);
 let granted=0;
 for(const id of ids)if(awardOneShotAdvancement(player,INVENTORY_ADVANCEMENTS[id]))granted++;
 return granted;
}
