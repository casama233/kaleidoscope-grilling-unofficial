/** Public, portable oil payload. No cross-pack private-property access or lore inference. */
export const OIL_API_VERSION='0.1.0';
export const OIL_CAPABILITIES=Object.freeze(['oil_pot_portable_v1','oil_pot_snapshot_v1','oil_pot_placed_v1']);
export const EMPTY_POT='kaleidoscope_cookery:oil_pot',FILLED_POT='kaleidoscope_cookery:oil_pot_filled';
export const OIL_PAYLOAD_PREFIX='§r§0§r§3§r§6';
export const OIL_KINDS=Object.freeze(['','canola','secret_chili','premium_chili']);
export const oilCapacity=type=>type===''?256:64;
const hash=s=>{let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return(h>>>0).toString(16).padStart(8,'0')};
const lineText=x=>typeof x==='string'?x:x&&typeof x.text==='string'?x.text:'';
export const isOilPayloadLine=x=>lineText(x).startsWith(OIL_PAYLOAD_PREFIX);
export function normalizePublicOil(raw){
 if(!raw||raw.v!==1||!OIL_KINDS.includes(raw.type)||!Number.isSafeInteger(raw.count)||raw.count<0||raw.count>oilCapacity(raw.type)||!Number.isSafeInteger(raw.revision)||raw.revision<0)return undefined;
 if(raw.count===0&&raw.type!=='')return undefined;
 return {v:1,type:raw.type,count:raw.count,revision:raw.revision};
}
export function encodePublicOil(raw){
 const s=normalizePublicOil(raw);if(!s)throw Error('invalid oil payload');
 const body='1|'+s.type+'|'+s.count+'|'+s.revision,data=body+'|'+hash(body);
 return OIL_PAYLOAD_PREFIX+[...data].map(c=>c.charCodeAt(0).toString(16).padStart(2,'0')).join('').split('').map(x=>'§'+x).join('')+'§r';
}
export function decodePublicOil(line){
 const text=lineText(line);if(!text.startsWith(OIL_PAYLOAD_PREFIX)||!text.endsWith('§r'))return undefined;
 const encoded=text.slice(OIL_PAYLOAD_PREFIX.length,-2);if(!/^(?:§[0-9a-f]){2,256}$/.test(encoded))return undefined;
 const hex=encoded.replaceAll('§','');if(hex.length%2)return undefined;
 let data='';for(let i=0;i<hex.length;i+=2)data+=String.fromCharCode(parseInt(hex.slice(i,i+2),16));
 const parts=data.split('|');if(parts.length!==5||parts[0]!=='1'||hash(parts.slice(0,4).join('|'))!==parts[4]||!/^(0|[1-9]\d*)$/.test(parts[2])||!/^(0|[1-9]\d*)$/.test(parts[3]))return undefined;
 return normalizePublicOil({v:1,type:parts[1],count:Number(parts[2]),revision:Number(parts[3])});
}
export function readPublicOil(stack){
 if(![EMPTY_POT,FILLED_POT].includes(stack?.typeId))return {handled:false,valid:false,reason:'not_pot'};
 let rows;try{rows=stack.getRawLore().filter(isOilPayloadLine)}catch{return {handled:true,valid:false,reason:'item_unreadable'}}
 if(rows.length===0)return {handled:true,valid:stack.typeId===EMPTY_POT,reason:stack.typeId===EMPTY_POT?'empty':'host_snapshot_required',state:stack.typeId===EMPTY_POT?{v:1,type:'',count:0,revision:0}:undefined};
 const state=rows.length===1?decodePublicOil(rows[0]):undefined;
 if(!state||stack.typeId===EMPTY_POT&&state.count!==0||stack.typeId===FILLED_POT&&state.count===0)return {handled:true,valid:false,reason:'payload_invalid'};
 return {handled:true,valid:true,state,source:'public_api'};
}
export function writePublicOil(stack,raw,{presentation=true}={}){
 const state=normalizePublicOil(raw);if(!state)throw Error('invalid oil payload');
 if(stack.typeId!==(state.count?FILLED_POT:EMPTY_POT))throw Error('oil item identity mismatch');
 const lore=stack.getRawLore().filter(x=>!isOilPayloadLine(x)&&(!presentation||!lineText(x).startsWith('§7Oil: ')&&lineText(x)!=='§7Empty'));
 if(lore.length+(presentation?2:1)>20)throw Error('oil payload has no lore space');
 if(presentation)lore.push(state.count?'§7Oil: '+state.count+'/'+oilCapacity(state.type):'§7Empty');
 lore.push(encodePublicOil(state));stack.setLore(lore);
 const actual=readPublicOil(stack);if(!actual.valid||JSON.stringify(actual.state)!==JSON.stringify(state))throw Error('oil payload readback');return stack;
}
export function createPublicOilPot(ItemStack,type,count,template,revision){
 const state=normalizePublicOil({v:1,type:count?type:'',count,revision:revision??((readPublicOil(template).state?.revision??0)+1)});if(!state)throw Error('invalid oil amount/type');
 const id=count?FILLED_POT:EMPTY_POT;let out;
 if(template?.typeId===id)out=template.clone();else{
  out=new ItemStack(id,1);
  if(template){out.nameTag=template.nameTag;out.setLore(template.getRawLore().filter(x=>!isOilPayloadLine(x)));if(template.keepOnDeath!==undefined)out.keepOnDeath=template.keepOnDeath;if(template.lockMode!==undefined)out.lockMode=template.lockMode;if(template.getCanDestroy)out.setCanDestroy(template.getCanDestroy());if(template.getCanPlaceOn)out.setCanPlaceOn(template.getCanPlaceOn());}
 }
 out.amount=1;return writePublicOil(out,state);
}
export function planPublicOilAddition(state,type,points=8){
 const s=normalizePublicOil(state);if(!s||!OIL_KINDS.includes(type)||!type||!Number.isSafeInteger(points)||points<1)return {ok:false,reason:'invalid'};
 if(s.count>0&&s.type!==type)return {ok:false,reason:'different_content'};
 if(s.count+points>64)return {ok:false,reason:'full'};
 return {ok:true,state:{v:1,type,count:s.count+points,revision:s.revision+1}};
}
export function planPublicOilConsumption(state,points){
 const s=normalizePublicOil(state);if(!s||!Number.isSafeInteger(points)||points<1)return {ok:false,reason:'invalid'};
 if(s.count<points)return {ok:false,reason:'insufficient'};const count=s.count-points;
 return {ok:true,state:{v:1,type:count?s.type:'',count,revision:s.revision+1}};
}
