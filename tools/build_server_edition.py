#!/usr/bin/env python3
"""Build the Senluo Grilling server edition from the in-repo upstream artifact.

Deltas over the upstream artifact (see docs/STATUS-A2.7.14-SERVER.md):
  1. Rewire the Cookery dependencies to the UUIDs installed on the target server.
  2. Route item dynamic properties / lore through itemData.js (stable
     @minecraft/server forbids them on stacks with maxAmount > 1).
  3. Replace block.isSolid with hasSolidTop() (not exposed on stable BDS).
  4. Capture seasoning-bottle placement through a block custom component.
  5. a23_oil_world.js: swap the upstream North/South face offsets; keep rows
     when a source block is unloaded or compute() throws.
  6. Block JSON: numeric ambient_occlusion; drop tag:minecraft:crop (rejected
     by this BDS block schema).
  7. Add the unlock data that 1.20+ crafting recipes require.
  8. a26 big-vat placement: defer the ItemStack::amount write out of the
     beforeEvents handler (restricted execution; the throw was swallowed).
  9. Preserve the canonical, single Cookery guide publisher and three languages.

Usage:  python tools/build_server_edition.py [--artifact PATH] [--version X.Y.Z] [OUT_DIR]
"""
import json, re, shutil, sys, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SHIMS = HERE / 'server-edition'
KC_BP, KC_RP = '403f7a4a-a837-42c8-b5d3-76d5079ef269', '8f39983b-00a6-4818-b489-0a73daf3bc87'
UP_BP, UP_RP = '10f37ae2-9ccf-435f-b34b-0eec8191cd94', 'c89dc8df-c3fc-4bc8-8bd0-527abba76681'

argv = list(sys.argv[1:])
def take(flag, default=None):
    if flag in argv:
        i = argv.index(flag); argv.pop(i); return argv.pop(i)
    return default
artifact = take('--artifact')
version = take('--version')
out = Path(argv[0]) if argv else ROOT / 'build/server-edition'
if artifact is None:
    def ver(path):
        m = re.search(r'A2\.(\d+)\.(\d+)', path.name)
        return (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    candidates = [p for p in (ROOT / 'artifacts').glob('Kaleidoscope_Grilling_A2.*.mcaddon')
                  if ver(p) >= (7, 0)]
    assert candidates, 'no A2.7+ artifact found'
    artifact = max(candidates, key=ver)
ART = Path(artifact)
if version is None:
    m = re.search(r'A2\.(?P<major>\d+)\.(?P<minor>\d+)', ART.name)
    assert m, ART.name
    version = f'2.{m.group("major")}.{m.group("minor")}'

if out.exists(): shutil.rmtree(out)
out.mkdir(parents=True)
with zipfile.ZipFile(ART) as z:
    z.extractall(out)
bp, rp = out / 'behavior_pack', out / 'resource_pack'
for d in (bp, rp): assert (d / 'manifest.json').is_file(), d
print(f'artifact {ART.name} -> server edition {version}')

def sub(path, pairs, label):
    text = path.read_text(encoding='utf-8')
    for old, new, count in pairs:
        n = text.count(old)
        assert n == count, f'{label}: expected {count} of {old[:70]!r}, found {n}'
        text = text.replace(old, new)
    path.write_text(text, encoding='utf-8')

ITEM_IMPORT = "import {getItemProperty,setItemProperty,getItemPropertyIds,getItemLore,setItemLore} from './itemData.js';\n"
SOLID_IMPORT = "import {hasSolidTop} from './blockSupport.js';\n"

# 1. manifests
sub(bp / 'manifest.json', [(f'"{UP_BP}"', f'"{KC_BP}"', 1)], 'bp-manifest')
sub(rp / 'manifest.json', [(f'"{UP_RP}"', f'"{KC_RP}"', 1)], 'rp-manifest')

pack_version = [int(v) for v in version.split('.')]
assert len(pack_version) == 3 and all(v >= 0 for v in pack_version), version
for side in (bp, rp):
    manifest = json.loads((side / 'manifest.json').read_text())
    manifest['header']['version'] = pack_version
    manifest['header']['name'] = f'Kaleidoscope Grilling A{version} Server Edition ' + ('BP' if side == bp else 'RP')
    manifest['header']['description'] = manifest['header']['description'].replace('Cookery 1.0.6', 'Cookery 1.0.7')
    for module in manifest['modules']: module['version'] = pack_version
    for dep in manifest.get('dependencies', []):
        if dep.get('uuid') in (KC_BP, KC_RP): dep['version'] = [1, 0, 7]
        if dep.get('uuid') == 'bbbd2d60-52e5-53a6-8b9a-c09b0f516389': dep['version'] = pack_version
    (side / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')

# 2. shims
shutil.copyfile(SHIMS / 'blockSupport.js', bp / 'scripts/blockSupport.js')
shutil.copyfile(SHIMS / 'itemData.js', bp / 'scripts/itemData.js')
# 3. item-property rewrite, per file, restricted to known ItemStack variable names
ITEM_VARS = {
    'main.js': ['from', 'next', 'out', 'stack', 'to'],
    'a23_hot_runtime.js': ['stack'],
    'a23_oil_world.js': ['nextPot'],
    'a25_plate_recipe_runtime.js': ['stack', 'out', 'output', 'book'],
    'a26_oil_machine_runtime.js': ['out', 'stack'],
    'a279_beef_board_runtime.js': ['stack'],
    'a2730_cookery_oil_pot_adapter.js': ['out', 'stack'],
    'a2734_cookery_oil_pot_adapter.js': ['out', 'stack'],
    'a2746_rack_item_codec.js': ['stack'],
    'a2750_cookery_cuisine_runtime.js': ['stack', 'next'],
    'a2750_food_state_adapter.js': ['stack'],
    # A2.8.7 additions.
    'a2762_interaction_intent_core.js': ['stack'],
    'a2766_special_seasoning_visual_runtime.js': ['stack', 'out', 'from', 'to'],
    'a2769_food_tooltip_core.js': ['stack'],
    'a285_eating_transaction.js': ['stack'],
}
rewritten = {}
for name, vars_ in ITEM_VARS.items():
    p = bp / 'scripts' / name
    t = p.read_text(encoding='utf-8')
    before_world = len(re.findall(r'\b(world|entity|p)\.(?:get|set)DynamicProperty', t))
    total = 0
    for v in vars_:
        for pat, rep in [
            (rf'\b{v}\?\.getDynamicPropertyIds\?\.\(\)', f'getItemPropertyIds({v})'),
            (rf'\b{v}\.getDynamicPropertyIds\?\.\(\)', f'getItemPropertyIds({v})'),
            (rf'\b{v}\?\.getDynamicPropertyIds\(\)', f'getItemPropertyIds({v})'),
            (rf'\b{v}\.getDynamicPropertyIds\(\)', f'getItemPropertyIds({v})'),
            (rf'\b{v}\?\.getDynamicProperty\(', f'getItemProperty({v},'),
            (rf'\b{v}\.getDynamicProperty\(', f'getItemProperty({v},'),
            (rf'\b{v}\?\.setDynamicProperty\(', f'setItemProperty({v},'),
            (rf'\b{v}\.setDynamicProperty\(', f'setItemProperty({v},'),
            (rf'\b{v}\?\.getLore\?\.\(\)', f'getItemLore({v})'),
            (rf'\b{v}\?\.getLore\(\)', f'getItemLore({v})'),
            (rf'\b{v}\.getLore\(\)', f'getItemLore({v})'),
            (rf'\b{v}\?\.setLore\(', f'setItemLore({v},'),
            (rf'\b{v}\.setLore\(', f'setItemLore({v},'),
        ]:
            t, n = re.subn(pat, rep, t)
            total += n
    if not total:
        # Upstream absorbed this file's item-property calls; nothing to rewrite.
        print(name, ': no item-property calls (already absorbed upstream)')
        p.write_text(t, encoding='utf-8')
        rewritten[name] = 0
        continue
    after_world = len(re.findall(r'\b(world|entity|p)\.(?:get|set)DynamicProperty', t))
    assert before_world == after_world, f'{name}: world/entity/player calls changed'
    for v in vars_:
        assert not re.search(rf'\b{v}\??\.(get|set)DynamicProperty|{v}\??\.(get|set)Lore', t), f'{name}: {v} call left'
    if 'itemData.js' not in t:
        t = ITEM_IMPORT + t
    p.write_text(t, encoding='utf-8')
    rewritten[name] = total
print('item-property calls rewritten:', rewritten)

# 4. block support: isSolid -> hasSolidTop
for name in ['main.js', 'a25_plate_recipe_runtime.js']:
    p = bp / 'scripts' / name
    t = p.read_text(encoding='utf-8')
    t = t.replace('below?.isSolid??false', 'hasSolidTop(below)')
    t = t.replace('!(support.isSolid??false)', '!hasSolidTop(support)')
    t = t.replace('if(support?.isSolid)return;', 'if(hasSolidTop(support))return;')
    # A2.8.7 adds a teleport-footing check on the stable block API.
    t = t.replace('if(below?.isSolid){', 'if(hasSolidTop(below)){')
    assert '.isSolid' not in t, name
    if 'blockSupport.js' not in t:
        lines = t.splitlines(True)
        nl = 1 if lines and lines[0].startswith('import') else 0
        t = ''.join(lines[:nl]) + SOLID_IMPORT + ''.join(lines[nl:])
    p.write_text(t, encoding='utf-8')
print('isSolid replaced with hasSolidTop')

# 5. seasoning bottle placement through a block custom component
M = bp / 'scripts/main.js'
t = M.read_text(encoding='utf-8')
if 'senluo:grilling_bottle_place' in t:
    # A2.8.7 upstream absorbed this server delta (block component + per-block cache).
    print('seasoning bottle placement absorbed upstream; skipped handler rewrite')
else:
    old_place = re.search(r"world\.beforeEvents\.playerPlaceBlock\.subscribe\(e=>\{try\{if\(e\.permutationToPlace\?\.type\?\.id!==SEASONING_BLOCK\).*?\}\);\n", t, re.S)
    assert old_place, 'seasoning placeBlock handler not found'
    t = t[:old_place.start()] + """// Capture the item while native placement still has its original hand stack.
// Stable 2.9 exposes this on the block component, not world.beforeEvents.
system.beforeEvents.startup.subscribe(({blockComponentRegistry})=>{
 blockComponentRegistry.registerCustomComponent('senluo:grilling_bottle_place',{
  beforeOnPlayerPlace(e){try{const held=heldMain(e.player);if(!held||![EMPTY_SEASONING_ID,PENDING_SEASONING,SEASONING_ID].includes(held.typeId))return;SEASON_PLACE_CACHE.set(e.player.id,{tick:system.currentTick,data:bottleDataFromItem(held)})}catch(error){console.error('[Grilling bottle placement] '+error);}}
 });
});
""" + t[old_place.end():]
t = t.replace("import './guide.js';\n", '')
M.write_text(t, encoding='utf-8')

# 6. a23 oil world: face offsets + robustness
# A2.8.7 absorbed some of these deltas upstream; apply whatever is still missing
# and assert that each pattern is either absent upstream or applied by us.
p23 = bp / 'scripts/a23_oil_world.js'
t23 = p23.read_text(encoding='utf-8')
for old23, new23 in [
    ('North:[0,0,1],South:[0,0,-1]', 'North:[0,0,-1],South:[0,0,1]'),
    ('const rows=readReg(),keep=[];', 'const rows=readReg(),before=JSON.stringify(rows),keep=[];'),
    ('if(JSON.stringify(keep)!==JSON.stringify(rows))saveReg(keep);else saveReg(rows);',
     'if(JSON.stringify(keep)!==before)saveReg(keep);'),
]:
    if old23 in t23:
        t23 = t23.replace(old23, new23, 1)
        print('a23 patched:', old23[:44])
    elif new23 in t23:
        print('a23 absorbed upstream:', old23[:44])
    else:
        raise AssertionError('a23 pattern drifted: ' + old23[:70])
for old23, new23 in [
    ('if(!source||source.typeId!==def.block||level(source)!==0){clearCells(row,rows);return false}',
     'if(!source)return true;if(source.typeId!==def.block||level(source)!==0){clearCells(row,rows);return false}'),
    ('if(compute(row,rows))keep.push(row);', 'try{if(compute(row,rows))keep.push(row)}catch{keep.push(row)}'),
]:
    n23 = t23.count(old23)
    assert n23 == 1, f'a23_oil_world.js: expected 1 of {old23[:60]!r}, found {n23}'
    t23 = t23.replace(old23, new23)
    print('a23 patched:', old23[:44])
p23.write_text(t23, encoding='utf-8')

# 7. a26 big-vat placement: keep the mutation out of restricted execution
# 7. a26 big-vat placement: keep the mutation out of restricted execution.
p26 = bp / 'scripts/a26_oil_machine_runtime.js'
t26 = p26.read_text(encoding='utf-8')
old26 = 'copy.amount=1;system.run(()=>placePackedVat(dim.getBlock(loc),face,p,copy));return}'
new26 = 'system.run(()=>{copy.amount=1;placePackedVat(dim.getBlock(loc),face,p,copy)});return}'
if old26 in t26:
    t26 = t26.replace(old26, new26, 1)
    print('a26 vat placement patched')
elif re.search(r'defer\(\(\)=>\{[^}]*placePackedVat', t26):
    print('a26 vat placement absorbed upstream (defer(...) wrapper present)')
else:
    raise AssertionError('a26 vat placement pattern drifted')
p26.write_text(t26, encoding='utf-8')

# 8. blocks: bottle component, numeric AO, unsupported crop tag
for name in ['seasoning_bottle.json', 'seasoning_bottle_1.json', 'seasoning_bottle_2.json',
             'seasoning_bottle_3.json', 'seasoning_bottle_4.json']:
    p = bp / 'blocks' / name
    if not p.exists(): continue
    t = p.read_text(encoding='utf-8')
    if 'senluo:grilling_bottle_place' in t: continue
    anchor = '"minecraft:destructible_by_mining"'
    idx = t.index(anchor); close = t.index('}', t.index('{', idx))
    t = t[:close + 1] + ',\n      "senluo:grilling_bottle_place": {}' + t[close + 1:]
    json.loads(t)
    p.write_text(t, encoding='utf-8')
ao = 0
for p in sorted((bp / 'blocks').glob('*.json')):
    t = p.read_text(encoding='utf-8')
    if '"ambient_occlusion": false' not in t: continue
    n = t.count('"ambient_occlusion": false')
    t = t.replace('"ambient_occlusion": false', '"ambient_occlusion": 0.0')
    json.loads(t); p.write_text(t, encoding='utf-8'); ao += n
print('ambient_occlusion fixes:', ao)
tagged = []
for p in sorted((bp / 'blocks').glob('*.json')):
    t = p.read_text(encoding='utf-8')
    if '"tag:minecraft:crop": {},' not in t: continue
    t = t.replace('"tag:minecraft:crop": {},', '')
    json.loads(t); p.write_text(t, encoding='utf-8'); tagged.append(p.name)
# A2.8.7 upstream no longer ships the unsupported crop tag; tolerate zero removals.
print('tag:minecraft:crop removed from:', tagged) if tagged else print('tag:minecraft:crop absent upstream (absorbed)')

# 8b. The A2.7.58 pepper-tree worldgen ships an acacia_trunk whose trunk_lean is
# missing the two children this BDS requires (lean_height, lean_steps), so the
# whole feature fails to register and the rule reports "No definition found".
for p in sorted((bp / 'features').glob('*.json')):
    j = json.loads(p.read_text(encoding='utf-8'))
    trunk = j.get('minecraft:tree_feature', {}).get('acacia_trunk', {}).get('trunk_lean')
    if not isinstance(trunk, dict): continue
    missing = [k for k in ('lean_height', 'lean_steps') if k not in trunk]
    if not missing: continue
    trunk.setdefault('lean_height', {'base': 1, 'intervals': [1], 'min_height_for_canopy': 2})
    trunk.setdefault('lean_steps', {'base': 1, 'intervals': [1]})
    p.write_text(json.dumps(j, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(p.name, 'trunk_lean completed:', missing)

# Preserve the installed fence-connection and nature-tab repairs. These deltas
# are part of the server edition rather than the public gameplay source.
NO_CONNECTION_BLOCKS = (
    'advanced_rack_block', 'canola_crop', 'canola_oil', 'grill', 'grill_legs',
    'houttuynia_crop', 'onion_crop', 'pepper_leaves', 'pepper_leaves_fruiting_bridge',
    'pepper_sapling', 'premium_chili_oil', 'seasoning_bottle', 'seasoning_bottle_1',
    'seasoning_bottle_2', 'seasoning_bottle_3', 'seasoning_bottle_4', 'secret_chili_oil',
    'skewer_plate_block', 'skewer_recipe', 'sweet_potato_crop',
)
for name in NO_CONNECTION_BLOCKS:
    p = bp / 'blocks' / (name + '.json')
    j = json.loads(p.read_text())
    j['minecraft:block']['components']['minecraft:connection_rule'] = {'accepts_connections_from': 'none'}
    p.write_text(json.dumps(j, ensure_ascii=False, indent=2) + '\n')
for folder, name in [('blocks', 'pepper_sapling')] + [('items', n) for n in ('canola_seeds', 'houttuynia', 'onion', 'sweet_potato')]:
    p = bp / folder / (name + '.json')
    j = json.loads(p.read_text())
    j['minecraft:' + ('block' if folder == 'blocks' else 'item')]['description']['menu_category']['category'] = 'nature'
    p.write_text(json.dumps(j, ensure_ascii=False, indent=2) + '\n')

# 9. recipes: unlock data (1.20+ crafting recipes are rejected without it;
# furnace recipes do not need any)
PREFERENCE = ['minecraft:iron_ingot', 'minecraft:brick_block', 'minecraft:bucket']
for p in sorted((bp / 'recipes').glob('*.json')):
    j = json.loads(p.read_text(encoding='utf-8'))
    r = j.get('minecraft:recipe_shaped') or j.get('minecraft:recipe_shapeless')
    if r is None or 'unlock' in r: continue
    items = [v.get('item') for v in r.get('key', {}).values() if isinstance(v, dict) and v.get('item')]
    items += [i.get('item') for i in r.get('ingredients', []) if isinstance(i, dict) and i.get('item')]
    assert items, p.name
    gate = next((w for w in PREFERENCE if w in items), items[0])
    r['unlock'] = [{'item': gate}]
    p.write_text(json.dumps(j, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(p.name, 'unlock ->', gate)

# 10. Use the upstream guide exactly once. A second publisher with the same
# source/module ID races the canonical 76-entry payload and replaces languages.
assert (bp / 'scripts/guide/main.js').is_file(), 'canonical guide required (A2.8.7+)'
assert (bp / 'scripts/main.js').read_text().count("import './guide/main.js';") == 1
for legacy in ['guide.js', 'guidePublisher.js']:
    (bp / 'scripts' / legacy).unlink(missing_ok=True)
print('canonical guide preserved; one publisher')

# 11. creative catalog: shared-group entries appended without an icon override
# Cookery's icon-carrying definitions depending on stack order, collapsing the
# creative "equipment" page to flat items (2026-09-25 incident; recurred when
# A2.8.7 reverted the server-side patch). Fill canonical Cookery group icons so
# the merge is order-independent. Only None icons are filled; an upstream icon
# is never overwritten, and an unknown name-only group fails loudly.
CATALOG_ICONS = {
    'kaleidoscope_cookery:itemGroup.name.tools': 'kaleidoscope_cookery:iron_kitchen_knife',
    'kaleidoscope_cookery:itemGroup.name.cooking_stations': 'kaleidoscope_cookery:stove',
    'kaleidoscope_cookery:itemGroup.name.storage_utility': 'kaleidoscope_cookery:fruit_basket',
    'kaleidoscope_cookery:itemGroup.name.crops': 'kaleidoscope_cookery:rice',
    'kaleidoscope_cookery:itemGroup.name.ingredients': 'kaleidoscope_cookery:flour',
    'kaleidoscope_cookery:itemGroup.name.foods': 'kaleidoscope_cookery:mantou',
    'kaleidoscope_cookery:itemGroup.name.other_blocks': 'kaleidoscope_cookery:oil_block',
    'kaleidoscope_cookery:itemGroup.name.recipe_pages': 'kaleidoscope_cookery:master_recipe_page',
}
cat = bp / 'item_catalog/crafting_item_catalog.json'
if cat.is_file():
    cj = json.loads(cat.read_text(encoding='utf-8-sig'))
    filled = 0
    for category in cj['minecraft:crafting_items_catalog']['categories']:
        for group in category['groups']:
            gi = group['group_identifier']
            if gi.get('icon') is None:
                icon = CATALOG_ICONS.get(gi['name'])
                assert icon, 'no canonical icon for name-only group ' + str(gi['name'])
                gi['icon'] = icon
                filled += 1
    # Appended shared groups must also sit in Cookery's category: crops live
    # under "nature" (the vanilla nature tab), not under equipment. Upstream
    # ships crops under equipment, which renders a second duplicate "crops"
    # group on the equipment page.
    moved = 0
    cats = cj['minecraft:crafting_items_catalog']['categories']
    for category in cats:
        if category['category_name'] != 'equipment':
            continue
        keep = []
        for group in category['groups']:
            if group['group_identifier']['name'] == 'kaleidoscope_cookery:itemGroup.name.crops':
                nature = next((c for c in cats if c['category_name'] == 'nature'), None)
                if nature is None:
                    nature = {'category_name': 'nature', 'groups': []}
                    cats.append(nature)
                nature['groups'].append(group)
                moved += 1
            else:
                keep.append(group)
        category['groups'] = keep
    cat.write_text(json.dumps(cj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('creative catalog icons filled:', filled, 'crops moved to nature:', moved)

# verification
INFRA = {'blockSupport.js', 'itemData.js'}
bad = []
for f in sorted((bp / 'scripts').glob('*.js')):
    if f.name in INFRA: continue
    t = f.read_text(encoding='utf-8')
    for pat in ['.isSolid', 'stack.getDynamicProperty', 'stack.setDynamicProperty', 'stack.getLore', 'stack.setLore',
                'out.setDynamicProperty', 'out.setLore', 'output.setDynamicProperty', 'output.getLore',
                'next.setDynamicProperty', 'next.setLore', 'from.getLore', 'to.setLore', 'nextPot.setDynamicProperty']:
        if pat in t: bad.append((f.name, pat))
assert not bad, bad
json.load(open(bp / 'manifest.json')); json.load(open(rp / 'manifest.json'))
print('OK server edition', version, '->', out)
