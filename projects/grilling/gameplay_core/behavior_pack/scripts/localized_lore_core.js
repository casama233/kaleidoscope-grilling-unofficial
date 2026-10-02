export const HEAT_NAME_KEY='tooltip.kaleidoscope_grilling.smoky_warmth';
export function heatLore(seconds){
 const sec=Math.max(1,Math.ceil(seconds)),m=Math.floor(sec/60),s=String(sec%60).padStart(2,'0');
 return {rawtext:[{text:'§c🔥 '},{translate:HEAT_NAME_KEY},{text:' '+m+':'+s}]};
}
export function isHeatLore(line){
 if(typeof line==='string')return line.startsWith('§c🔥');
 if(typeof line?.text==='string')return line.text.startsWith('§c🔥');
 const parts=line?.rawtext;
 return Array.isArray(parts)&&parts[0]?.text==='§c🔥 '&&parts[1]?.translate===HEAT_NAME_KEY;
}
