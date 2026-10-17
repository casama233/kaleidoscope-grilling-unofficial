import {world} from '@minecraft/server';
import {configureItemDataWorld} from './itemDataCore.js';
configureItemDataWorld(world);
export {getItemProperty,getItemPropertyIds,setItemProperty,getItemLore,getItemRawLore,setItemLore} from './itemDataCore.js';
