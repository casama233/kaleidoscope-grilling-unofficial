/** Java 1.1.1 event counts and positions; owned instant-one emitters retain Mojang sprite/motion profiles. */
const BURSTS=Object.freeze({
 seasoningFinished:{id:'kaleidoscope_grilling:feedback_villager_happy',count:12,center:[0,1,0],spread:[.25,.35,.25],speed:.05},
 seasoningAdded:{id:'kaleidoscope_grilling:feedback_endrod',count:5,center:[.5,.7,.5],spread:[.12,.12,.12],speed:.01},
 oilPressImpact:{id:'kaleidoscope_grilling:feedback_basic_crit',count:14,center:[.5,.9,.5],spread:[.32,.18,.32],speed:.08},
 invincibleSpark:{id:'kaleidoscope_grilling:feedback_electric_spark',count:8,center:[0,0,0],spread:[.35,.45,.35],speed:.08},
 invincibleRod:{id:'kaleidoscope_grilling:feedback_endrod',count:4,center:[0,0,0],spread:[.25,.35,.25],speed:.03},
 ordinaryShield:{id:'kaleidoscope_grilling:feedback_electric_spark',count:28,center:[0,1,0],spread:[.55,.7,.55],speed:.12}
});
// ServerLevel.sendParticles samples a Gaussian independently for each axis.
// Avoid log(0) while retaining the unbounded Gaussian (do not clamp to a box).
function gaussian(random){return Math.sqrt(-2*Math.log(Math.max(Number.MIN_VALUE,1-random())))*Math.cos(2*Math.PI*random())}
export function interactionParticles(event,random=Math.random){
 const spec=BURSTS[event];if(!spec)return [];
 return Array.from({length:spec.count},()=>({id:spec.id,offset:spec.center.map((value,axis)=>value+gaussian(random)*spec.spread[axis]),velocity:[0,0,0].map(()=>gaussian(random)*spec.speed)}));
}
export function grillParticles(lit,random=Math.random){
 if(!lit)return [];
 const result=[];
 if(random()<1/3)result.push({id:'kaleidoscope_grilling:feedback_basic_smoke',offset:[.25+random()*.5,.22,.25+random()*.5],velocity:[0,.02,0]});
 if(random()<1/8)result.push({id:'kaleidoscope_grilling:feedback_basic_flame',offset:[.3+random()*.4,.18,.3+random()*.4],velocity:[0,.01,0]});
 return result;
}
export function oilImpactPitch(random=Math.random){return .82+random()*.12}
export function goldenSkewerParticles(random=Math.random){
 return Array.from({length:18},(_,i)=>{const angle=2*Math.PI*i/18;return {id:'kaleidoscope_grilling:feedback_electric_spark',offset:[Math.cos(angle)*.65,.25+i*.06+gaussian(random)*.02,Math.sin(angle)*.65],velocity:[0,0,0].map(()=>gaussian(random)*.02)}});
}
export function invincibleAmbientParticle(random=Math.random){
 const angle=random()*Math.PI*2;return [{id:'kaleidoscope_grilling:feedback_electric_spark',offset:[Math.cos(angle)*.45,.3+random()*1.4,Math.sin(angle)*.45],velocity:[0,0,0]}];
}
export function createFeedbackCooldown(ticks=6){
 const deadlines=new Map();
 return {
  claim(id,tick){if(tick<(deadlines.get(id)??-Infinity))return false;deadlines.set(id,tick+ticks);return true},
  sweep(tick){for(const [id,deadline] of deadlines)if(tick>=deadline)deadlines.delete(id)},
  get size(){return deadlines.size}
 };
}
