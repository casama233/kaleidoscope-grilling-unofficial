#!/usr/bin/env python3
"""Build the A2.7.14 server edition from the in-repo upstream artifact.

Deltas applied (see docs/STATUS-A2.7.14-SERVER.md section 2 for the full table):
  1. Rewire the Cookery dependencies to the UUIDs installed on the target server.
  2. Route stackable-item dynamic properties / lore through itemData.js
     (stable @minecraft/server forbids them on maxAmount > 1 stacks).
  3. Replace block.isSolid with the hasSolidTop() heuristic (blockSupport.js).
  4. Capture seasoning-bottle placement through a block custom component.
  5. a23_oil_world.js: swap the upstream North/South face offsets, keep
     registration rows when a source block is unloaded or compute() throws.
  6. Block JSON: numeric ambient_occlusion; drop the tag:minecraft:crop
     component this BDS build rejects.
  7. Add the unlock data 1.20+ shaped recipes require.
  8. a26 big-vat placement: defer the ItemStack::amount write out of the
     beforeEvents handler (restricted execution threw and was swallowed).
  9. Install the Cookery guidebook extension (guide.js + publisher.js).

Usage:  python tools/build_server_edition.py [OUT_DIR]
"""
import json, shutil, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'artifacts/Kaleidoscope_Grilling_A2.7.14_Houttuynia_Crop.mcaddon'
SHIMS = Path(__file__).resolve().parent / 'server-edition'
PUBLISHER = SHIMS / 'publisher.js'
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'build/server-edition-a2.7.14'
KC_BP, KC_RP = '403f7a4a-a837-42c8-b5d3-76d5079ef269', '8f39983b-00a6-4818-b489-0a73daf3bc87'
UP_BP, UP_RP = '10f37ae2-9ccf-435f-b34b-0eec8191cd94', 'c89dc8df-c3fc-4bc8-8bd0-527abba76681'
INTEG = PUBLISHER

if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir(parents=True)
with zipfile.ZipFile(ART) as z:
    z.extractall(OUT)
bp, rp = OUT / 'behavior_pack', OUT / 'resource_pack'
for d in (bp, rp): assert (d / 'manifest.json').is_file(), d

def sub(path, pairs, label):
    text = path.read_text(encoding='utf-8')
    for old, new, count in pairs:
        n = text.count(old)
        assert n == count, f'{label}: expected {count} of {old[:60]!r}, found {n}'
        text = text.replace(old, new)
    path.write_text(text, encoding='utf-8')

ITEM_IMPORT = "import {getItemProperty,setItemProperty,getItemPropertyIds,getItemLore,setItemLore} from './itemData.js';\n"
SOLID_IMPORT = "import {hasSolidTop} from './blockSupport.js';\n"

# ---------------- manifests: dependency rewiring ----------------
sub(bp / 'manifest.json', [(f'"{UP_BP}"', f'"{KC_BP}"', 1)], 'bp-manifest')
sub(rp / 'manifest.json', [(f'"{UP_RP}"', f'"{KC_RP}"', 1)], 'rp-manifest')

# ---------------- infrastructure scripts ----------------
shutil.copyfile(SHIMS / 'blockSupport.js', bp / 'scripts' / 'blockSupport.js')
shutil.copyfile(SHIMS / 'itemData.js', bp / 'scripts' / 'itemData.js')
rev = INTEG.read_text(encoding='utf-8').replace("'a1_12_0'", "'server_a2_7_14'")
(bp / 'scripts' / 'guidePublisher.js').write_text(rev, encoding='utf-8')

ICON = 'textures/items/grilled_beef_skewer'
rows = [
 ('start', '版本與取得物品', [
  '目前安裝 A2.7.14 核心：烤爐、穿串、調料瓶、熱串、串盤與食譜記錄，並已包含榨油機、大缸、砧板加工與魚腥草作物。',
  '工作台可合成烤爐、空調料瓶、榨油機、大缸與油餅；一根木棍可製成可放副手的空串。',
  '砧板加工使用森羅物語：廚房的砧板與廚房刀。',
 ]),
 ('grill', '烤爐操作', [
  '用打火石點火，放入最多三串生串，再用森羅物語裝油油壺刷油，每串消耗一點油。',
  '空手使用烤爐翻面四次，每次至少隔一秒。用完成的調料瓶撒料，再空手取出；蹲下可一次取完。',
  '不要擱置太久，會烤焦。一般油的熱串保溫一分鐘，熱度隨世界時間流逝。',
 ]),
 ('thread', '手工穿串', [
  '先在工作台把一根木棍做成空串，放入副手；主手持食材使用即可依序穿入。',
  '放入對應順序會形成固定串；其他可食用的三種材料會形成秘制串。',
  '蹲下使用可拆解副手的未烤串並返還材料和木棍。',
 ]),
 ('seasoning', '調料瓶', [
  '空調料瓶放在地上後，持材料使用瓶子；最多八種材料，必須含青辣椒粉、花椒與洋蔥粉。',
  '取回待搖勻調料後，持續使用四秒搖勻；完成瓶共可供十六串調味。',
  '瓶子可疊放至四層；不同瓶子的配方分別保存。',
 ]),
 ('plate', '串盤與保存', [
  '蹲下持串對支撐方塊頂面使用即可擺盤，最多放五串；空手依序取回。',
  '烤串的配料、熱度與秘制內容可隨物品保存。熱度會繼續隨世界時間下降。',
 ]),
 ('book', '烤串食譜', [
  '副手放完整生串，主手持森羅物語空白食譜使用，即可記錄烤串配方。',
  '記錄好的食譜可貼牆；主手持木棍點擊牆上食譜，可依背包材料製作。空手取回食譜。',
 ]),
 ('oil', '榨油機與大缸', [
  '把油餅（工作台用油菜籽等合成）放入榨油機，最多四塊；手持鐵砧對榨油機使用即可壓榨，壓滿後產出四桶油與油渣。',
  '大缸可儲存八桶液體：三種油、水或岩漿。持對應空桶對大缸使用可裝取。',
  '手持森羅物語空油壺對裝油的大缸使用，可為油壺灌油。',
 ]),
 ('board', '砧板加工', [
  '在森羅物語：廚房的砧板上，手持廚房刀（鐵/金/鑽石/獄髓）對食材使用即可切配，多數食材需切四次。',
  '可切胡蘿蔔、馬鈴薯、饅頭與魚腥草等；對生雞使用可取得雞皮、雞翅與小塊生肉。',
  '砧板加工為原版工作台以外的取得途徑，部分烤串專用材料只能由此獲得。',
 ]),
 ('crops', '作物與魚腥草', [
  '魚腥草種子可種在耕地上，成熟後呈紅色變種；破壞成熟植株可取得魚腥草與種子。',
  '魚腥草可在砧板切成魚腥草末，作為調料瓶的duration粉料來源。',
  '油菜作物成熟後取得油菜籽，用於合成油餅。',
 ]),
]
payload = {'api': 1, 'id': 'kg_a1:grilling', 'version': '2.7.14', 'order': 300, 'icon': ICON,
 'titleKey': 'title', 'introKey': 'intro', 'allKey': 'all', 'selectKey': 'select', 'backKey': 'back',
 'showAll': False, 'showIds': False, 'showKinds': False, 'showCategoryOnEntry': False,
 'categories': [{'id': 'play', 'labelKey': 'play', 'fallback': '煙火玩法', 'icon': ICON}],
 'entries': [{'id': 'kg_a1:server_' + i, 'category': 'play', 'icon': ICON, 'kinds': [], 'mechanics': m} for i, _, m in rows],
 'names': {lang: {'kg_a1:server_' + i: name for i, name, _ in rows} for lang in ['zh_TW', 'zh_CN', 'en_US']},
 'text': {lang: {'title': '煙火 · 烤串', 'intro': '烤爐、穿串與調料操作', 'all': '全部', 'select': '選擇說明', 'back': '返回', 'play': '玩法與取得方式'} for lang in ['zh_TW', 'zh_CN', 'en_US']}}
guide = ("import{system}from'@minecraft/server';import{installPublisher}from'./guidePublisher.js';\n"
         'installPublisher(system,' + json.dumps(payload, ensure_ascii=False) + ');\n')
(bp / 'scripts' / 'guide.js').write_text(guide, encoding='utf-8')

# ---------------- main.js ----------------
M = bp / 'scripts' / 'main.js'
text = M.read_text(encoding='utf-8')
assert not text.startswith("import './guide.js';")
M.write_text("import './guide.js';\n" + SOLID_IMPORT + ITEM_IMPORT + text, encoding='utf-8')
sub(M, [
 # block support
 ('supported=!helper&&(below?.isSolid??false)', 'supported=!helper&&hasSolidTop(below)', 1),
 # container transfer helpers
 ('let lore=[];try{lore=from.getLore()}catch{}', 'let lore=[];try{lore=getItemLore(from,)}catch{}', 1),
 ('let ids=[];try{ids=from.getDynamicPropertyIds()}catch{}', 'let ids=[];try{ids=getItemPropertyIds(from,)}catch{}', 1),
 ('try{if(lore.length)to.setLore(lore);else if(ids.length)to.setLore([\'§r\'])}catch{}',
  'try{if(lore.length)setItemLore(to,lore);else if(ids.length)setItemLore(to,[\'§r\'])}catch{}', 1),
 ('for(const id of ids)try{to.setDynamicProperty(id,from.getDynamicProperty(id))}catch{}',
  'for(const id of ids)try{setItemProperty(to,id,getItemProperty(from,id))}catch{}', 1),
 # skewer row snapshot
 ('const out={};let ids=[];try{ids=stack.getDynamicPropertyIds()}catch{}',
  'const out={};let ids=[];try{ids=getItemPropertyIds(stack,)}catch{}', 1),
 ('for(const id of ids)try{const value=stack.getDynamicProperty(id);',
  'for(const id of ids)try{const value=getItemProperty(stack,id);', 1),
 ('let lore=[];try{lore=stack.getLore()}catch{}', 'let lore=[];try{lore=getItemLore(stack,)}catch{}', 2),
 ('try{if(Array.isArray(row.lore)&&row.lore.length)out.setLore(row.lore);else if(keys.length)out.setLore([\'§r\'])}catch{}',
  'try{if(Array.isArray(row.lore)&&row.lore.length)setItemLore(out,row.lore);else if(keys.length)setItemLore(out,[\'§r\'])}catch{}', 1),
 ('for(const id of keys)try{out.setDynamicProperty(id,props[id])}catch{}',
  'for(const id of keys)try{setItemProperty(out,id,props[id])}catch{}', 1),
 ('try{const raw=stack?.getDynamicProperty(key);if(typeof raw!==\'string\')return [];',
  'try{const raw=getItemProperty(stack,key);if(typeof raw!==\'string\')return [];', 1),
 ('stack?.typeId===SECRET_ID&&stack.getDynamicProperty(SECRET_COOKED_KEY)===true',
  'stack?.typeId===SECRET_ID&&getItemProperty(stack,SECRET_COOKED_KEY)===true', 1),
 # hand threading
 ('stack.setLore([\'§8手工穿串 \'+clean.length+\'/3\',...clean.map(x=>\'§7- \'+rowLabel(x))]);',
  'setItemLore(stack,[\'§8手工穿串 \'+clean.length+\'/3\',...clean.map(x=>\'§7- \'+rowLabel(x))]);', 1),
 ('stack.setDynamicProperty(SKEWER_INGREDIENTS_KEY,JSON.stringify(clean));',
  'setItemProperty(stack,SKEWER_INGREDIENTS_KEY,JSON.stringify(clean));', 1),
 ('stack.setDynamicProperty(SECRET_CREATOR_KEY,JSON.stringify(creator));const lore=stack.getLore();lore.push(\'§7製作者: \'+player.name);stack.setLore(lore)',
  'setItemProperty(stack,SECRET_CREATOR_KEY,JSON.stringify(creator));const lore=getItemLore(stack,);lore.push(\'§7製作者: \'+player.name);setItemLore(stack,lore)', 1),
 ('function setCookedIngredientRows(stack,rows){try{stack.setDynamicProperty(SECRET_COOKED_INGREDIENTS_KEY,JSON.stringify(cookedIngredientRows(rows)))}catch{}return stack}',
  'function setCookedIngredientRows(stack,rows){try{setItemProperty(stack,SECRET_COOKED_INGREDIENTS_KEY,JSON.stringify(cookedIngredientRows(rows)))}catch{}return stack}', 1),
 # seasonings
 ('parseList(stack?.getDynamicProperty(SEASON_LIST_KEY))', 'parseList(getItemProperty(stack,SEASON_LIST_KEY))', 1),
 ('stack.setDynamicProperty(SEASON_LIST_KEY,JSON.stringify(list.slice(0,8)))',
  'setItemProperty(stack,SEASON_LIST_KEY,JSON.stringify(list.slice(0,8)))', 1),
 ('Number(stack?.getDynamicProperty(SEASON_USES_KEY)??0)', 'Number(getItemProperty(stack,SEASON_USES_KEY)??0)', 1),
 ('stack.setDynamicProperty(SEASON_USES_KEY,Math.max(0,Math.min(16,n|0)))',
  'setItemProperty(stack,SEASON_USES_KEY,Math.max(0,Math.min(16,n|0)))', 1),
 # hot lore
 ("const lore=stack.getLore().filter(x=>!String(x).startsWith('§c🔥'));lore.push('§c🔥 煙火氣 '+m+':'+ss);",
  "const lore=getItemLore(stack,).filter(x=>!String(x).startsWith('§c🔥'));lore.push('§c🔥 煙火氣 '+m+':'+ss);", 1),
 ('stack.setLore(lore);stack.setDynamicProperty(HOT_UNTIL_KEY,until);',
  'setItemLore(stack,lore);setItemProperty(stack,HOT_UNTIL_KEY,until);', 1),
 ('Number(stack?.getDynamicProperty(HOT_UNTIL_KEY)??0)', 'Number(getItemProperty(stack,HOT_UNTIL_KEY)??0)', 1),
 ("const base=stack.getLore().filter(x=>!String(x).startsWith('§c🔥'));if(until<=0)return stack;",
  "const base=getItemLore(stack,).filter(x=>!String(x).startsWith('§c🔥'));if(until<=0)return stack;", 1),
 ('if(left<=0){stack.setDynamicProperty(HOT_UNTIL_KEY,undefined);stack.setLore(base);return stack}',
  'if(left<=0){setItemProperty(stack,HOT_UNTIL_KEY,undefined);setItemLore(stack,base);return stack}', 1),
 ("base.push('§c🔥 煙火氣 '+m+':'+s);stack.setLore(base);",
  "base.push('§c🔥 煙火氣 '+m+':'+s);setItemLore(stack,base);", 1),
 ('try{stack.setDynamicProperty(SECRET_COOKED_KEY,true)}catch{}',
  'try{setItemProperty(stack,SECRET_COOKED_KEY,true)}catch{}', 1),
 ("try{stack.setDynamicProperty('kaleidoscope_grilling:seasoned',state.seasoned)}catch{}",
  "try{setItemProperty(stack,'kaleidoscope_grilling:seasoned',state.seasoned)}catch{}", 1),
 # cookery oil pot
 ("String(stack?.getDynamicProperty('kaleidoscope_grilling:oil_type')??'')",
  "String(getItemProperty(stack,'kaleidoscope_grilling:oil_type')??'')", 1),
 ('const raw=stack.getDynamicProperty(COOKERY_OIL_KEY);return raw===undefined?cap:',
  'const raw=getItemProperty(stack,COOKERY_OIL_KEY);return raw===undefined?cap:', 1),
 ("next.setLore(['§7Oil: '+remaining+'/'+cap]);next.setDynamicProperty(COOKERY_OIL_KEY,remaining);if(type)next.setDynamicProperty('kaleidoscope_grilling:oil_type',type)",
  "setItemLore(next,['§7Oil: '+remaining+'/'+cap]);setItemProperty(next,COOKERY_OIL_KEY,remaining);if(type)setItemProperty(next,'kaleidoscope_grilling:oil_type',type)", 1),
 ('try{next.setLore([\'§7Uses: \'+(16-nextUses)+\'/16\'])}catch{}',
  'try{setItemLore(next,[\'§7Uses: \'+(16-nextUses)+\'/16\'])}catch{}', 1),
 # seasoning bottle data
 ('Number(stack.getDynamicProperty(SEASON_VARIANT_KEY)??0)',
  'Number(getItemProperty(stack,SEASON_VARIANT_KEY)??0)', 1),
 ("stack.setDynamicProperty(SEASON_VARIANT_KEY,data.variant??0);stack.setLore(['§7Uses: '+(16-(data.uses??0))+'/16','§7Ingredients: '+(data.ingredients?.length??0)+'/8'])",
  "setItemProperty(stack,SEASON_VARIANT_KEY,data.variant??0);setItemLore(stack,['§7Uses: '+(16-(data.uses??0))+'/16','§7Ingredients: '+(data.ingredients?.length??0)+'/8'])", 1),
 ("stack.setLore(['§7Ingredients: '+data.ingredients.length+'/8',",
  "setItemLore(stack,['§7Ingredients: '+data.ingredients.length+'/8',", 1),
 ("try{out.setDynamicProperty(SEASON_VARIANT_KEY,Math.floor(Math.random()*8));out.setLore(['§7Uses: 16/16','§7Ingredients: '+list.length+'/8'])}catch{}",
  "try{setItemProperty(out,SEASON_VARIANT_KEY,Math.floor(Math.random()*8));setItemLore(out,['§7Uses: 16/16','§7Ingredients: '+list.length+'/8'])}catch{}", 1),
], 'main.js')

# bottle placement: world.beforeEvents.playerPlaceBlock -> startup block component
OLD_PLACE = "world.beforeEvents.playerPlaceBlock.subscribe(e=>{try{if(e.permutationToPlace?.type?.id!==SEASONING_BLOCK)return;const held=heldMain(e.player);if(!held||![EMPTY_SEASONING_ID,PENDING_SEASONING,SEASONING_ID].includes(held.typeId))return;SEASON_PLACE_CACHE.set(e.player.id,{tick:system.currentTick,data:bottleDataFromItem(held)})}catch{}});"
NEW_PLACE = """// Capture the item while native placement still has its original hand stack.
// Stable 2.9 exposes this on the block component, not world.beforeEvents.
system.beforeEvents.startup.subscribe(({blockComponentRegistry})=>{
 blockComponentRegistry.registerCustomComponent('senluo:grilling_bottle_place',{
  beforeOnPlayerPlace(e){try{const held=heldMain(e.player);if(!held||![EMPTY_SEASONING_ID,PENDING_SEASONING,SEASONING_ID].includes(held.typeId))return;SEASON_PLACE_CACHE.set(e.player.id,{tick:system.currentTick,data:bottleDataFromItem(held)})}catch(error){console.error('[Grilling bottle placement] '+error);}}
 });
});"""
sub(M, [(OLD_PLACE, NEW_PLACE, 1)], 'main.js-bottle-place')

# ---------------- a23_hot_runtime.js ----------------
F = bp / 'scripts' / 'a23_hot_runtime.js'
F.write_text(ITEM_IMPORT + F.read_text(encoding='utf-8'), encoding='utf-8')
sub(F, [
 ("function baseLore(stack){try{return stack.getLore().filter(x=>!String(x).startsWith('§c🔥'))}catch{return []}}",
  "function baseLore(stack){try{return getItemLore(stack,).filter(x=>!String(x).startsWith('§c🔥'))}catch{return []}}", 1),
 ('let ids=[];try{ids=stack.getDynamicPropertyIds()}catch{}', 'let ids=[];try{ids=getItemPropertyIds(stack,)}catch{}', 1),
 ('v=stack.getDynamicProperty(k)}catch{}', 'v=getItemProperty(stack,k)}catch{}', 1),
 ('Number(stack?.getDynamicProperty(HOT)??0)', 'Number(getItemProperty(stack,HOT)??0)', 1),
 ('stack.setLore(lore);', 'setItemLore(stack,lore);', 1),
 ('if(remaining>0)stack.setDynamicProperty(HOT,bucket(t+remaining));', 'if(remaining>0)setItemProperty(stack,HOT,bucket(t+remaining));', 1),
 ('else stack.setDynamicProperty(HOT,undefined);', 'else setItemProperty(stack,HOT,undefined);', 1),
], 'a23_hot_runtime.js')

# ---------------- a23_oil_world.js ----------------
F = bp / 'scripts' / 'a23_oil_world.js'
F.write_text(ITEM_IMPORT + F.read_text(encoding='utf-8'), encoding='utf-8')
sub(F, [
 ('North:[0,0,1],South:[0,0,-1]', 'North:[0,0,-1],South:[0,0,1]', 1),
 ('if(!source||source.typeId!==def.block||level(source)!==0){clearCells(row,rows);return false}',
  'if(!source)return true;if(source.typeId!==def.block||level(source)!==0){clearCells(row,rows);return false}', 1),
 ("String(stack?.getDynamicProperty('kaleidoscope_grilling:oil_type')??'')", "String(getItemProperty(stack,'kaleidoscope_grilling:oil_type')??'')", 1),
 ('Number(stack?.getDynamicProperty(\'kc_oil_count\')??0)|0)', 'Number(getItemProperty(stack,\'kc_oil_count\')??0)|0)', 1),
 ("nextPot.setLore(['§7Oil: '+next+'/'+FLUID_CAPACITY]);", "setItemLore(nextPot,['§7Oil: '+next+'/'+FLUID_CAPACITY]);", 1),
 ("nextPot.setDynamicProperty('kc_oil_count',next);", "setItemProperty(nextPot,'kc_oil_count',next);", 1),
 ("nextPot.setDynamicProperty('kaleidoscope_grilling:oil_type',type);", "setItemProperty(nextPot,'kaleidoscope_grilling:oil_type',type);", 1),
 ('const rows=readReg(),keep=[];', 'const rows=readReg(),before=JSON.stringify(rows),keep=[];', 1),
 ('if(compute(row,rows))keep.push(row);', 'try{if(compute(row,rows))keep.push(row)}catch{keep.push(row)}', 1),
 ('if(JSON.stringify(keep)!==JSON.stringify(rows))saveReg(keep);else saveReg(rows);', 'if(JSON.stringify(keep)!==before)saveReg(keep);', 1),
], 'a23_oil_world.js')

# ---------------- a25_plate_recipe_runtime.js ----------------
F = bp / 'scripts' / 'a25_plate_recipe_runtime.js'
F.write_text(SOLID_IMPORT + ITEM_IMPORT + F.read_text(encoding='utf-8'), encoding='utf-8')
sub(F, [
 ('const out={};let ids=[];try{ids=stack.getDynamicPropertyIds()}catch{}', 'const out={};let ids=[];try{ids=getItemPropertyIds(stack,)}catch{}', 1),
 ('const value=stack.getDynamicProperty(id);', 'const value=getItemProperty(stack,id);', 1),
 ("const raw=stack?.getDynamicProperty(key);if(typeof raw!=='string')return [];", "const raw=getItemProperty(stack,key);if(typeof raw!=='string')return [];", 1),
 ('cooked=stack.getDynamicProperty(SECRET_COOKED_KEY)===true', 'cooked=getItemProperty(stack,SECRET_COOKED_KEY)===true', 1),
 ('try{lore=stack.getLore()}catch{}try{name=stack.nameTag??\'\'}catch{}', 'try{lore=getItemLore(stack,)}catch{}try{name=stack.nameTag??\'\'}catch{}', 1),
 ("try{if(Array.isArray(row.lore)&&row.lore.length)out.setLore(row.lore);else if(keys.length)out.setLore(['§r'])}catch{}",
  "try{if(Array.isArray(row.lore)&&row.lore.length)setItemLore(out,row.lore);else if(keys.length)setItemLore(out,['§r'])}catch{}", 1),
 ('for(const id of keys)try{out.setDynamicProperty(id,props[id])}catch{}', 'for(const id of keys)try{setItemProperty(out,id,props[id])}catch{}', 1),
 ("lore=out.getLore().filter(x=>!String(x).startsWith('§7Skewers:'))", "lore=getItemLore(out,).filter(x=>!String(x).startsWith('§7Skewers:'))", 1),
 ('try{out.setLore(lore);out.setDynamicProperty(PLATE_SKEWERS_KEY,JSON.stringify(clean))}catch{}', 'try{setItemLore(out,lore);setItemProperty(out,PLATE_SKEWERS_KEY,JSON.stringify(clean))}catch{}', 1),
 ('const raw=book?.getDynamicProperty(BOOK_RECORD_KEY);if(typeof raw!==\'string\')return null;', "const raw=getItemProperty(book,BOOK_RECORD_KEY);if(typeof raw!=='string')return null;", 1),
 ("lore=out.getLore().filter(x=>!String(x).startsWith('§7Recipe:'))", "lore=getItemLore(out,).filter(x=>!String(x).startsWith('§7Recipe:'))", 1),
 ('try{out.setLore(lore);out.setDynamicProperty(BOOK_RECORD_KEY,value?JSON.stringify(value):undefined)}catch{}', 'try{setItemLore(out,lore);setItemProperty(out,BOOK_RECORD_KEY,value?JSON.stringify(value):undefined)}catch{}', 1),
 ('!(support.isSolid??false)', '!hasSolidTop(support)', 1),
 ('if(support?.isSolid)return;', 'if(hasSolidTop(support))return;', 1),
 ('try{output.setDynamicProperty(SECRET_COOKED_KEY,false);output.setDynamicProperty(SECRET_CREATOR_KEY,player.name)}catch{}', 'try{setItemProperty(output,SECRET_COOKED_KEY,false);setItemProperty(output,SECRET_CREATOR_KEY,player.name)}catch{}', 1),
 ("const lore=output.getLore().filter(x=>!String(x).startsWith('§7製作者:'));lore.push('§7製作者: '+player.name);output.setLore(lore)", "const lore=getItemLore(output,).filter(x=>!String(x).startsWith('§7製作者:'));lore.push('§7製作者: '+player.name);setItemLore(output,lore)", 1),
], 'a25_plate_recipe_runtime.js')

# ---------------- a26_oil_machine_runtime.js ----------------
F = bp / 'scripts' / 'a26_oil_machine_runtime.js'
F.write_text(ITEM_IMPORT + F.read_text(encoding='utf-8'), encoding='utf-8')
sub(F, [
 ("type=String(stack?.getDynamicProperty(VAT_ITEM_TYPE)??'');buckets=Number(stack?.getDynamicProperty(VAT_ITEM_BUCKETS)??0)|0",
  "type=String(getItemProperty(stack,VAT_ITEM_TYPE)??'');buckets=Number(getItemProperty(stack,VAT_ITEM_BUCKETS)??0)|0", 1),
 ('for(const line of stack?.getLore?.()??[]){', 'for(const line of getItemLore(stack)){', 1),
 ('if(lore.length)out.setLore(lore);', 'if(lore.length)setItemLore(out,lore);', 1),
 ('out.setDynamicProperty(VAT_ITEM_TYPE,state.type||undefined);out.setDynamicProperty(VAT_ITEM_BUCKETS,state.buckets||undefined);',
  'setItemProperty(out,VAT_ITEM_TYPE,state.type||undefined);setItemProperty(out,VAT_ITEM_BUCKETS,state.buckets||undefined);', 1),
 ("String(stack?.getDynamicProperty('kaleidoscope_grilling:oil_type')??'')", "String(getItemProperty(stack,'kaleidoscope_grilling:oil_type')??'')", 1),
 ("Number(stack?.getDynamicProperty('kc_oil_count')??0)|0)", "Number(getItemProperty(stack,'kc_oil_count')??0)|0)", 1),
 ("try{out.setLore(['§7Oil: '+count+'/'+OIL_POT_CAPACITY]);out.setDynamicProperty('kaleidoscope_grilling:oil_type',type);out.setDynamicProperty('kc_oil_count',count)}catch{}",
  "try{setItemLore(out,['§7Oil: '+count+'/'+OIL_POT_CAPACITY]);setItemProperty(out,'kaleidoscope_grilling:oil_type',type);setItemProperty(out,'kc_oil_count',count)}catch{}", 1),
], 'a26_oil_machine_runtime.js')

# ItemStack::amount cannot be written inside world.beforeEvents handlers (restricted
# execution); the throw is swallowed by the handler's empty catch, so placing a big
# vat silently did nothing. Defer the mutation into system.run like the sibling
# placement paths do.
sub(F, [
 ('const dim=b.dimension,loc={...b.location},face=e.blockFace,copy=item.clone();copy.amount=1;system.run(()=>placePackedVat(dim.getBlock(loc),face,p,copy));return}',
  'const dim=b.dimension,loc={...b.location},face=e.blockFace,copy=item.clone();system.run(()=>{copy.amount=1;placePackedVat(dim.getBlock(loc),face,p,copy)});return}', 1),
], 'a26_oil_machine_runtime.js-vat-placement')

# ---------------- a279_beef_board_runtime.js ----------------
F = bp / 'scripts' / 'a279_beef_board_runtime.js'
F.write_text(ITEM_IMPORT + F.read_text(encoding='utf-8'), encoding='utf-8')
sub(F, [
 ('const out={};let ids=[];try{ids=stack.getDynamicPropertyIds()}catch{}', 'const out={};let ids=[];try{ids=getItemPropertyIds(stack,)}catch{}', 1),
 ('const v=stack.getDynamicProperty(id);', 'const v=getItemProperty(stack,id);', 1),
 ('let lore=[];try{lore=stack.getLore()}catch{}', 'let lore=[];try{lore=getItemLore(stack,)}catch{}', 1),
], 'a279_beef_board_runtime.js')

# ---------------- block JSONs ----------------
for name in ['seasoning_bottle.json', 'seasoning_bottle_1.json', 'seasoning_bottle_2.json', 'seasoning_bottle_3.json', 'seasoning_bottle_4.json']:
    p = bp / 'blocks' / name
    t = p.read_text(encoding='utf-8')
    assert 'senluo:grilling_bottle_place' not in t, name
    anchor = '"minecraft:destructible_by_mining"'
    idx = t.index(anchor)
    close = t.index('}', t.index('{', idx))  # end of the seconds_to_destroy object
    t = t[:close + 1] + ',\n      "senluo:grilling_bottle_place": {}' + t[close + 1:]
    json.loads(t)  # still valid
    p.write_text(t, encoding='utf-8')
for name in ['skewer_recipe.json', 'houttuynia_crop.json']:
    p = bp / 'blocks' / name
    t = p.read_text(encoding='utf-8')
    n = t.count('"ambient_occlusion": false')
    assert n >= 1, name
    json.loads(t.replace('"ambient_occlusion": false', '"ambient_occlusion": 0.0'))
    p.write_text(t.replace('"ambient_occlusion": false', '"ambient_occlusion": 0.0'), encoding='utf-8')
    print(name, 'ambient_occlusion fixes:', n)

# tag:minecraft:crop is not in this BDS's block schema (Content Log error on load);
# scripts key off block type, so the tag is dropped rather than replaced.
p = bp / 'blocks' / 'houttuynia_crop.json'
t = p.read_text(encoding='utf-8')
assert t.count('"tag:minecraft:crop": {},') == 1
t = t.replace('"tag:minecraft:crop": {},', '')
json.loads(t); p.write_text(t, encoding='utf-8')
print('houttuynia_crop: removed unsupported tag:minecraft:crop component')

# 1.20+ shaped recipes require unlock data; upstream ships none for the A2.6 machines.
UNLOCK = {'oil_press.json': 'minecraft:iron_ingot', 'oil_cake.json': 'kaleidoscope_grilling:canola_powder', 'big_vat.json': 'minecraft:brick_block'}
for name, gate in UNLOCK.items():
    p = bp / 'recipes' / name
    j = json.loads(p.read_text(encoding='utf-8'))
    r = j['minecraft:recipe_shaped']
    assert 'unlock' not in r, name
    r['unlock'] = [{'item': gate}]
    p.write_text(json.dumps(j, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(name, 'unlock ->', gate)

# ---------------- verification ----------------
bad = []
INFRA = {'blockSupport.js', 'itemData.js'}
for f in sorted((bp / 'scripts').glob('*.js')):
    if f.name in INFRA: continue  # these two implement the shims themselves
    t = f.read_text(encoding='utf-8')
    for pat in ['stack.getDynamicProperty', 'stack.setDynamicProperty', 'stack.getLore', 'stack.setLore',
                'next.setDynamicProperty', 'next.setLore', 'out.setDynamicProperty', 'out.setLore',
                'nextPot.setDynamicProperty', 'nextPot.setLore', 'output.setDynamicProperty', 'output.getLore', 'output.setLore',
                'from.getLore', 'from.getDynamicProperty', 'to.setLore', 'to.setDynamicProperty', 'book?.getDynamicProperty',
                '.isSolid']:
        if pat in t: bad.append((f.name, pat))
for f in ['main.js', 'a23_hot_runtime.js', 'a23_oil_world.js', 'a25_plate_recipe_runtime.js', 'a26_oil_machine_runtime.js', 'a279_beef_board_runtime.js']:
    t = (bp / 'scripts' / f).read_text(encoding='utf-8')
    assert 'itemData.js' in t, f
assert 'guide.js' in (M.read_text(encoding='utf-8'))[:120]
assert not bad, bad
json.load(open(bp / 'manifest.json')); json.load(open(rp / 'manifest.json'))
print('OK build at', OUT)
print('scripts:', sorted(f.name for f in (bp / 'scripts').glob('*.js')))
