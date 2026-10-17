export const JAVA_RECIPE_PATHS=Object.freeze([
'advanced_rack.json','big_vat.json',
'chopping_board/carrot_dice.json','chopping_board/minced_houttuynia.json','chopping_board/potato_slice.json','chopping_board/raw_mantou_slice.json','chopping_board/raw_sweet_potato_sheet.json',
'clear_seasoning.json','clear_skewer_recipe_book.json','cold_houttuynia.json','crushing/canola_powder.json','empty_seasoning_bottle.json',
'filling/canola_oil_bucket.json','filling/canola_oil_pot.json','filling/chili_oil_bucket.json','filling/chili_oil_pot.json','filling/lava_chili_oil_bucket.json','filling/lava_chili_oil_pot.json',
'flex_pot/braised_chicken_wings.json','flex_pot/green_pepper_squid_tentacles.json','flex_pot/houttuynia_stir_fried_pork.json',
'flex_stockpot/potato_beef_stew.json','flex_stockpot/red_sweet_potato_porridge.json','flex_stockpot/sour_spicy_noodles.json',
'grill.json',
'milling/canola_powder.json','milling/green_chili_powder.json','milling/houttuynia_powder.json','milling/onion_powder.json','milling/red_chili_powder.json','milling/sweet_potato_powder.json','milling/totem_powder.json',
'millstone/canola_powder.json','millstone/green_chili_powder.json','millstone/houttuynia_powder.json','millstone/onion_powder.json','millstone/red_chili_powder.json','millstone/sweet_potato_powder.json','millstone/totem_powder.json',
'mixing/chili_oil_fluid.json','mixing/lava_chili_oil_fluid.json','oak_planks_from_pepper_log.json','oil_cake.json','oil_press.json','pepper_honey.json',
'pot/braised_chicken_wings.json','pot/green_pepper_squid_tentacles.json','pot/houttuynia_stir_fried_pork.json',
'premium_chili_oil.json','roasted_chicken_wing.json','roasted_chicken_wing_campfire.json','roasted_chicken_wing_smoking.json',
'roasted_sweet_potato.json','roasted_sweet_potato_campfire.json','roasted_sweet_potato_smoking.json',
'secret_chili_oil.json','skewer_recipe_book.json',
'stockpot/potato_beef_stew.json','stockpot/red_sweet_potato_porridge.json','stockpot/sour_spicy_noodles.json','sugared_tomato.json'
]);

export const COOKERY_MACHINE=Object.freeze(JAVA_RECIPE_PATHS.filter(p=>/^(chopping_board|millstone|pot|flex_pot|stockpot|flex_stockpot)\//.test(p)));
export const CREATE_ONLY=Object.freeze(JAVA_RECIPE_PATHS.filter(p=>/^(crushing|milling|filling|mixing)\//.test(p)));
export const GRILLING_CUSTOM=Object.freeze(['clear_seasoning.json','cold_houttuynia.json','skewer_recipe_book.json']);
export const VANILLA_DIRECT=Object.freeze(JAVA_RECIPE_PATHS.filter(p=>!COOKERY_MACHINE.includes(p)&&!CREATE_ONLY.includes(p)&&!GRILLING_CUSTOM.includes(p)));
export const TAVERN_CONDITIONAL=Object.freeze(['stockpot/sour_spicy_noodles.json','flex_stockpot/sour_spicy_noodles.json']);
export const CORE_COOKERY_MACHINE=Object.freeze(COOKERY_MACHINE.filter(p=>!TAVERN_CONDITIONAL.includes(p)));
export const DEFERRED_OUTPUT=Object.freeze({
 'advanced_rack.json':'A2.9',
 'oak_planks_from_pepper_log.json':'A2.8'
});

export function recipeClass(path){
 if(TAVERN_CONDITIONAL.includes(path))return 'tavern_conditional';
 if(CREATE_ONLY.includes(path))return 'create_optional';
 if(GRILLING_CUSTOM.includes(path))return 'grilling_custom';
 if(COOKERY_MACHINE.includes(path))return 'cookery_machine';
 if(VANILLA_DIRECT.includes(path))return 'vanilla_direct';
 return null;
}

export function recipeCoverageSummary(){
 return {
  total:JAVA_RECIPE_PATHS.length,
  cookeryMachine:COOKERY_MACHINE.length,
  coreCookeryMachine:CORE_COOKERY_MACHINE.length,
  tavernConditional:TAVERN_CONDITIONAL.length,
  createOnly:CREATE_ONLY.length,
  vanillaDirect:VANILLA_DIRECT.length,
  grillingCustom:GRILLING_CUSTOM.length
 };
}

export const COLD_HOUTTUYNIA_CONTRACT=Object.freeze({
 result:'kaleidoscope_grilling:cold_houttuynia',
 premiumOilType:'premium_chili',oilPoints:2,houttuynia:3,occupiedSlots:4
});
export const CLEAR_SEASONING_INPUTS=Object.freeze([
 'kaleidoscope_grilling:pending_seasoning','kaleidoscope_grilling:special_seasoning'
]);
export const CLEAR_BOOK_SUBSTITUTION=Object.freeze({
 javaResult:'kaleidoscope_cookery:recipe_item',
 bedrockResult:'kaleidoscope_grilling:skewer_recipe_book',
 reason:'Cookery Bedrock 1.0.6 observed item registry does not expose recipe_item; clear dynamic recipe data in-place.'
});
