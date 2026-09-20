import assert from 'node:assert/strict';
import {
  UNFINISHED_ID,SECRET_ID,FAT_CAPACITY,FLUID_CAPACITY,OIL_BUCKET_POINTS,
  recipeTable,completedRecipe,appendOutcome,secretFood,oilPotCapacity,clampOilCount,canFillTypedOil,
  isDisassemblableRaw
} from './a24_skewering_core.js';

let n=0;
const t=(name,fn)=>{fn();n++;console.log('PASS',name)};

t('ships all 20 Java configured skewer recipes',()=>assert.equal(recipeTable().length,20));
t('fixed beef recipe resolves exactly',()=>{
  const r=completedRecipe(['kaleidoscope_grilling:beef_chunks','kaleidoscope_cookery:red_chili','kaleidoscope_grilling:beef_chunks']);
  assert.equal(r?.id,'kaleidoscope_grilling:raw_beef_skewer');
});
t('fish alternatives resolve the one-slot fish skewer',()=>{
  for(const id of ['minecraft:cod','minecraft:salmon','minecraft:tropical_fish','minecraft:pufferfish'])
    assert.equal(appendOutcome([],id,true).id,'kaleidoscope_grilling:raw_fish_skewer');
});
t('ordinary skewer is an exact three-item configured result',()=>{
  const x=appendOutcome([{id:'minecraft:poisonous_potato'},{id:'minecraft:spider_eye'}],'minecraft:pufferfish',true);
  assert.deepEqual({ok:x.ok,kind:x.kind,id:x.id},{ok:true,kind:'fixed',id:'kaleidoscope_grilling:ordinary_skewer'});
});
t('unmatched edible ingredients become unfinished then secret',()=>{
  const a=appendOutcome([],'minecraft:apple',true);
  const b=appendOutcome([{id:'minecraft:apple'}],'minecraft:carrot',true);
  const c=appendOutcome([{id:'minecraft:apple'},{id:'minecraft:carrot'}],'minecraft:bread',true);
  assert.equal(a.id,UNFINISHED_ID);assert.equal(b.id,UNFINISHED_ID);assert.equal(c.id,SECRET_ID);
});
t('non-food non-configured item is rejected',()=>assert.equal(appendOutcome([],'minecraft:cobblestone',false).ok,false));
t('fourth ingredient is rejected',()=>assert.equal(appendOutcome([{id:'minecraft:apple'},{id:'minecraft:carrot'},{id:'minecraft:bread'}],'minecraft:melon_slice',true).ok,false));
t('fixed raw, unfinished and raw secret are disassemblable',()=>{
  assert.equal(isDisassemblableRaw(UNFINISHED_ID),true);
  assert.equal(isDisassemblableRaw('kaleidoscope_grilling:raw_beef_skewer'),true);
  assert.equal(isDisassemblableRaw(SECRET_ID,false),true);
  assert.equal(isDisassemblableRaw(SECRET_ID,true),false);
});
t('secret cooked food uses Java 0.6 coefficient',()=>{
  assert.deepEqual(secretFood([
    {id:'minecraft:apple',nutrition:4,saturation:.3},
    {id:'minecraft:bread',nutrition:5,saturation:.6},
    {id:'minecraft:carrot',nutrition:3,saturation:.6}
  ],true),{nutrition:7,saturation:.5,duplicate:false});
});
t('secret duplicate penalty is Java 0.6 x 0.8',()=>{
  const x=secretFood([
    {id:'minecraft:apple',signature:'apple',nutrition:4,saturation:.3},
    {id:'minecraft:apple',signature:'apple',nutrition:4,saturation:.3},
    {id:'minecraft:bread',signature:'bread',nutrition:5,saturation:.6}
  ],true);
  assert.equal(x.nutrition,6);assert.equal(x.duplicate,true);
});
t('raw secret halves cooked nutrition and saturation',()=>{
  const cooked=secretFood([{id:'a',nutrition:5,saturation:.4},{id:'b',nutrition:5,saturation:.6},{id:'c',nutrition:5,saturation:.8}],true);
  const raw=secretFood([{id:'a',nutrition:5,saturation:.4},{id:'b',nutrition:5,saturation:.6},{id:'c',nutrition:5,saturation:.8}],false);
  assert.equal(cooked.nutrition,9);assert.equal(raw.nutrition,4);assert.equal(raw.saturation,cooked.saturation*.5);
});
t('typed Grilling oils are 64 points while Cookery fat remains 256',()=>{
  assert.equal(FAT_CAPACITY,256);assert.equal(FLUID_CAPACITY,64);assert.equal(OIL_BUCKET_POINTS,8);
  assert.equal(oilPotCapacity(''),256);assert.equal(oilPotCapacity('canola'),64);
  assert.equal(clampOilCount('secret_chili',256),64);
});
t('typed bucket transactions are eight points and stop at 64',()=>{
  assert.equal(canFillTypedOil('',0,'canola',8),true);
  assert.equal(canFillTypedOil('canola',56,'canola',8),true);
  assert.equal(canFillTypedOil('canola',57,'canola',8),false);
  assert.equal(canFillTypedOil('canola',64,'canola',8),false);
});
t('typed oil cannot mix with fat or another fluid oil',()=>{
  assert.equal(canFillTypedOil('',1,'canola',8),false);
  assert.equal(canFillTypedOil('canola',8,'secret_chili',8),false);
});

console.log(JSON.stringify({passed:n,failed:0,scope:'A2.4 Java 1.1.1 threading, Secret Skewer nutrition, and OilPot capacity parity'}));
