// Disabled adapter: world dynamic properties do not cross behavior-pack UUIDs.
// Keep exports for existing consumers, but never fabricate a zero host oil count
// or let a local readback authorize mutation of Cookery's shared block.
export function placedOilPotLocation(block){return {x:block.x,y:block.y,z:block.z};}
export function capturePlacedOilPotSnapshot(_block){return undefined;}
export function placedOilPotSnapshotMatches(_block,_snapshot){return false;}
export function restorePlacedOilPotSnapshot(_block,_snapshot){return false;}
export function readPlacedOilPotState(_block){return undefined;}
export function writePlacedOilPotState(_block,_type,_count){return false;}
export function clearPlacedOilPotState(_block){return false;}
