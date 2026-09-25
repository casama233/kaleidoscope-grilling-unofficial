import assert from 'node:assert/strict';
import {
 JAVA_RECIPE_PATHS,COOKERY_MACHINE,CORE_COOKERY_MACHINE,TAVERN_CONDITIONAL,CREATE_ONLY,VANILLA_DIRECT,GRILLING_CUSTOM,
 recipeClass,recipeCoverageSummary,COLD_HOUTTUYNIA_CONTRACT,CLEAR_SEASONING_INPUTS,CLEAR_BOOK_SUBSTITUTION
} from './a27_recipe_core.js';
let n=0;const t=(name,fn)=>{fn();n++;console.log('PASS',name)};

t('all 61 pinned Java 1.1.1 recipe files are represented',()=>{assert.equal(JAVA_RECIPE_PATHS.length,61);assert.equal(new Set(JAVA_RECIPE_PATHS).size,61)});
t('classification is disjoint and exhaustive',()=>{
 const sets=[COOKERY_MACHINE,CREATE_ONLY,VANILLA_DIRECT,GRILLING_CUSTOM];
 assert.equal(sets.reduce((n,x)=>n+x.length,0),61);
 const all=sets.flat();assert.equal(new Set(all).size,61);
});
t('source classification counts stay locked',()=>assert.deepEqual(recipeCoverageSummary(),{
 total:61,cookeryMachine:24,coreCookeryMachine:22,tavernConditional:2,createOnly:16,vanillaDirect:18,grillingCustom:3
}));
t('two sour-spicy noodle recipes remain Tavern conditional',()=>{
 assert.deepEqual(TAVERN_CONDITIONAL,['stockpot/sour_spicy_noodles.json','flex_stockpot/sour_spicy_noodles.json']);
 for(const p of TAVERN_CONDITIONAL)assert.equal(recipeClass(p),'tavern_conditional');
});
t('Create recipes are optional integration rather than Grilling core loss',()=>{
 for(const p of ['crushing/canola_powder.json','milling/onion_powder.json','filling/canola_oil_bucket.json','mixing/chili_oil_fluid.json'])assert.equal(recipeClass(p),'create_optional');
});
t('22 Cookery machine recipes are core once Tavern conditional pair is excluded',()=>assert.equal(CORE_COOKERY_MACHINE.length,22));
t('custom serializers are exactly the three Java dynamic recipes',()=>assert.deepEqual(GRILLING_CUSTOM,['clear_seasoning.json','cold_houttuynia.json','skewer_recipe_book.json']));
t('cold houttuynia dynamic contract is pinned',()=>assert.deepEqual(COLD_HOUTTUYNIA_CONTRACT,{result:'kaleidoscope_grilling:cold_houttuynia',premiumOilType:'premium_chili',oilPoints:2,houttuynia:3,occupiedSlots:4}));
t('clear seasoning accepts pending/special static cases',()=>assert.deepEqual(CLEAR_SEASONING_INPUTS,['kaleidoscope_grilling:pending_seasoning','kaleidoscope_grilling:special_seasoning']));
t('Bedrock clear-book substitution is explicit',()=>{assert.equal(CLEAR_BOOK_SUBSTITUTION.javaResult,'kaleidoscope_cookery:recipe_item');assert.equal(CLEAR_BOOK_SUBSTITUTION.bedrockResult,'kaleidoscope_grilling:skewer_recipe_book')});
console.log(JSON.stringify({passed:n,failed:0,scope:'A2.7 complete Java 61-recipe inventory and classification'}));
