/** Native ItemStack snapshots; no lossy serialization or inventory.addItem writes.
 * Plans run synchronously. commitSteps supplies best-effort rollback, not crash safety.
 */
export function slotWrite(container,slot,after){
 const before=container.getItem(slot)?.clone(),next=after?.clone();
 return {apply:()=>container.setItem(slot,next?.clone()),rollback:()=>container.setItem(slot,before?.clone())};
}
export function remainderOf(stack,moved){
 if(moved>=stack.amount)return undefined;
 const remaining=stack.clone();remaining.amount=stack.amount-moved;return remaining;
}
export function planInventoryInsert(container,stack,excluded=-1){
 let remaining=stack.amount;const changes=[],size=Math.min(36,container.size);
 for(const empty of [false,true])for(let slot=0;slot<size&&remaining>0;slot++){
  if(slot===excluded)continue;
  const before=container.getItem(slot);
  if(empty?!!before:!before||!before.isStackableWith(stack))continue;
  const moved=Math.min(remaining,before?before.maxAmount-before.amount:stack.maxAmount);
  if(moved<=0)continue;
  const after=(before??stack).clone();after.amount=(before?.amount??0)+moved;
  changes.push(slotWrite(container,slot,after));remaining-=moved;
 }
 return {steps:changes,moved:stack.amount-remaining,remainder:remainderOf(stack,stack.amount-remaining)};
}
