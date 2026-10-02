/** Heat belongs to the finish tick, including native Cookery dishes. */
export function finishedFoodMeta(meta,time){
 return {...meta,hot:!!meta?.hot&&Number(meta.hotUntil)>Number(time)};
}
