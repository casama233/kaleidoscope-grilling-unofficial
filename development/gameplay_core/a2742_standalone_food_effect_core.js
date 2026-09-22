import {
 ROASTED_ID,WARMTH_EFFECT,WARMTH_TICKS,nextWarmthUntil
} from './a2720_roasted_sweet_potato_core.js';
import {
 COLD_ID,FIRE_RESISTANCE_TICKS
} from './a2722_cold_houttuynia_core.js';

export const FX_KEY='kaleidoscope_grilling:a21_fx';
export const SUGARED_TOMATO_ID='kaleidoscope_grilling:sugared_tomato';
export const PEPPER_HONEY_ID='kaleidoscope_grilling:pepper_honey';
export const PEPPER_HONEY_NUMB_TICKS=1200;

const ROWS=Object.freeze([
 Object.freeze({
  itemId:ROASTED_ID,
  effects:Object.freeze([
   Object.freeze({
    kind:'persistent_fx',
    effect:WARMTH_EFFECT,
    ticks:WARMTH_TICKS,
    amplifier:0,
    stacking:'max_until'
   })
  ])
 }),
 Object.freeze({
  itemId:COLD_ID,
  effects:Object.freeze([
   Object.freeze({
    kind:'native',
    effect:'fire_resistance',
    ticks:FIRE_RESISTANCE_TICKS,
    options:Object.freeze({showParticles:true})
   })
  ])
 }),
 Object.freeze({
  itemId:PEPPER_HONEY_ID,
  effects:Object.freeze([
   Object.freeze({
    kind:'persistent_fx',
    effect:'numb',
    ticks:PEPPER_HONEY_NUMB_TICKS,
    amplifier:0,
    stacking:'max_until'
   })
  ])
 })
]);

export function standaloneFoodEffectTable(){
 return ROWS.map(row=>({
  itemId:row.itemId,
  effects:row.effects.map(effect=>JSON.parse(JSON.stringify(effect)))
 }));
}

export function effectsForStandaloneFood(itemId){
 const row=ROWS.find(x=>x.itemId===String(itemId??''));
 return row?row.effects.map(effect=>JSON.parse(JSON.stringify(effect))):[];
}

export function nextPersistentUntil(nowTick,currentUntil,duration){
 return nextWarmthUntil(nowTick,currentUntil,duration);
}
