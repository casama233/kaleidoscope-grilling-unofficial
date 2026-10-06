/** BDS exposes pre-absorption provisional health in the before-hurt callback.
 * Remaining native absorption is not exposed by stable Script API. Its effect
 * maximum is only an upper bound: do not consume rescue on an ambiguous hit.
 * A partially spent shield can therefore still hide a lethal hit; not Java parity.
 */
export function definitelyLethalProvisionalHealth(health,absorption){
 const hp=Number(health);if(!Number.isFinite(hp)||hp>0)return false;
 if(!absorption)return true;
 const amp=Number(absorption.amplifier);
 if(!Number.isInteger(amp)||amp<0||amp>255)return false;
 return hp+4*(amp+1)<=0;
}
