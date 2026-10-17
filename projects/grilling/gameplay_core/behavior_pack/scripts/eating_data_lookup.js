export * from './data.js';
import {FOOD_DATA as food,RAW_TO_COOKED as raw,COOKED_EFFECTS as effects,RAW_NAUSEA as nausea,PROFILE_BY_ITEM as profiles} from './data.js';
import {foodLookup} from './eating_profile_ids.js';
export const FOOD_DATA=foodLookup(food),RAW_TO_COOKED=foodLookup(raw),COOKED_EFFECTS=foodLookup(effects),RAW_NAUSEA=foodLookup(nausea),PROFILE_BY_ITEM=foodLookup(profiles);
