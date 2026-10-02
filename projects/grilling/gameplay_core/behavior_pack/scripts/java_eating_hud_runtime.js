import {javaEatingHudFrame} from './java_eating_hud_core.js';
// Format codes carry a graphical frame only; no printable progress/status text.
// No idle/stop/complete packet: the private factory expires in 75 ms.
export function showJavaEatingHud(player,session,tick){
 const frame=javaEatingHudFrame({id:session.id,elapsed:tick-session.start,duration:session.profile==='THREE'?100:90,tick});
 if(frame)try{player.onScreenDisplay.setActionBar(frame.packet)}catch{}
}
