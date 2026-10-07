import {canonicalFoodId} from './eating_profile_ids.js';
import {RAW_TO_COOKED} from './data.js';
import {GRILL_MODEL_INDEX} from './grill_visual_data.js';
import {decodeSecretVisual} from './secret_visual_state_core.js';

// Reuse the existing eight integer channels per hand; do not add player state.
// Every word is exactly representable by a Molang IEEE-754 single precision value.
export const PLATE_HELD_PALETTE_RADIX=214;
export const PLATE_HELD_PALETTE_MAX=214**3-1;
export const PLATE_HELD_ROW_RADIX=123;
export const PLATE_HELD_OWNER_MIN=10;
export const PLATE_HELD_OWNER_MAX=747;
export const HELD_VISUAL_INVALID_OWNER=748;
const COOKED_TO_RAW=Object.freeze(Object.fromEntries(Object.entries(RAW_TO_COOKED).map(([raw,cooked])=>[cooked,raw])));
const SPECIAL_ROWS=Object.freeze({'kaleidoscope_grilling:ordinary_skewer':120,'kaleidoscope_grilling:mysterious_skewer':121,'kaleidoscope_grilling:dark_grilling':122});

export function packPlatePalette(values){
 if(!Array.isArray(values)||values.length!==3||values.some(v=>!Number.isInteger(v)||v<0||v>=PLATE_HELD_PALETTE_RADIX))throw Error('Invalid held plate palette');
 return values[0]+values[1]*214+values[2]*45796;
}

export function plateHeldRowPlan(stack,readSecretVisual,isDefaultFailedVisual=()=>true){
 const id=canonicalFoodId(stack?.typeId);
 if(id==='kaleidoscope_grilling:secret_skewer'){
  if(typeof readSecretVisual!=='function')throw Error('Held plate secret reader unavailable');
  const packed=readSecretVisual(stack);
  if(!Array.isArray(packed)||packed.length!==3)throw Error('Invalid held plate secret state');
  const cells=packed.map(decodeSecretVisual),style=cells[0].style;
  if(![0,4,6].includes(style)||cells.some(cell=>cell.style!==style))throw Error('Invalid held plate secret style');
  const shape=(cells[0].shape-1)*9+(cells[1].shape-1)*3+cells[2].shape-1;
  return {descriptor:39+shape+27*[0,4,6].indexOf(style),palette:packPlatePalette(cells.map(cell=>cell.food))};
 }
 if(Object.hasOwn(SPECIAL_ROWS,id??'')){
  // Ordinary has one authored fixed mesh. Failed-family source/state variants
  // are a separate repair; do not misrepresent retained non-default metadata.
  const descriptor=id==='kaleidoscope_grilling:ordinary_skewer'||isDefaultFailedVisual(stack)?SPECIAL_ROWS[id]:0;
  return {descriptor,palette:0};
 }
 const raw=COOKED_TO_RAW[id]??id,index=Object.hasOwn(GRILL_MODEL_INDEX,raw??'')?GRILL_MODEL_INDEX[raw]:undefined;
 return {descriptor:index===undefined?0:1+2*index+(COOKED_TO_RAW[id]?1:0),palette:0};
}

// Inputs are temporary restored copies. Only derive presentation; never mutate
// their identity, metadata, aliases or the authoritative plate's stored rows.
export function plateHeldVisualPlan(stacks,readSecretVisual,isDefaultFailedVisual){
 if(!Array.isArray(stacks)||stacks.length>5)throw Error('Invalid held plate row count');
 const rows=Array.from({length:5},(_,i)=>i<stacks.length?plateHeldRowPlan(stacks[i],readSecretVisual,isDefaultFailedVisual):{descriptor:0,palette:0});
 return [...rows.map(row=>row.palette),rows[0].descriptor+123*rows[1].descriptor,rows[2].descriptor+123*rows[3].descriptor,10+rows[4].descriptor+123*stacks.length];
}

// Independent integer decoder used by tests and diagnostics, not item storage.
export function decodePlateHeldVisual(words){
 if(!Array.isArray(words)||words.length!==8||words.some(v=>!Number.isInteger(v)||v<0||v>PLATE_HELD_PALETTE_MAX))return undefined;
 const marker=words[7];if(marker<10||marker>747||words[5]>=123**2||words[6]>=123**2)return undefined;
 const count=Math.floor((marker-10)/123),descriptors=[words[5]%123,Math.floor(words[5]/123),words[6]%123,Math.floor(words[6]/123),(marker-10)%123];
 return {count,rows:words.slice(0,5).map((word,i)=>({descriptor:descriptors[i],palette:[word%214,Math.floor(word/214)%214,Math.floor(word/45796)]}))};
}
