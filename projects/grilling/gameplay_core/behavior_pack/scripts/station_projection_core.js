/** Explicit item-data render providers; helpers remain disposable and never deliver items. */
import {readPublicProjection} from './integration_stack_core.js';
import {projectionDescriptorFor} from './integration_registry_core.js';
const providers=new Map();
export function registerStationProjection(itemId,provider){
 if(!/^[a-z0-9_.-]+:[a-z0-9_./-]+$/.test(itemId)||typeof provider!=='function'||providers.has(itemId))return false;
 providers.set(itemId,provider);return true;
}
export function stationProjection(stack,publicFood){
 const declared=projectionDescriptorFor(stack.typeId),portable=readPublicProjection(stack);
 if(portable.present&&!portable.valid)throw Error('Unreadable public projection metadata');
 if(portable.valid&&(!declared||declared.provider!==portable.state.provider))throw Error('Unregistered projection provider');
 const provider=providers.get(stack.typeId);
 const result=provider?provider(stack.clone()):{data:portable.valid?portable.state.data:declared?.defaultData??publicFood?.nativeVariant??stack.getComponent?.('minecraft:durability')?.damage??0};
 if(!result||!Number.isInteger(result.data)||result.data<0||result.data>32767)throw Error('Unsupported item projection data');
 return {data:result.data};
}
