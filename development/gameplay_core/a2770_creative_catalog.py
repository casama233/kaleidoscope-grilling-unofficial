"""Generate Grilling-only creative groups without changing gameplay or exposing state items."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / 'projects/grilling/gameplay_core'
BP, RP = PROJECT / 'behavior_pack', PROJECT / 'resource_pack'
REPORT = PROJECT / 'reports/a2770-creative-catalog.json'
NS = 'kaleidoscope_grilling:'
GROUP_PREFIX = NS + 'itemGroup.'
VERSION = [2, 7, 70]
LOCALES = ('zh_TW', 'zh_CN', 'en_US')
# Preserve the existing raw/cooked pairing rather than alphabetical texture filenames.
SKEWERS = ('beef', 'pork_belly', 'chicken_skin', 'mid_wing', 'squid_tentacle', 'fish',
           'sweet_potato_sheet', 'potato_slice', 'caterpillar', 'mushroom', 'bun_slice',
           'ender_pearl', 'meatball', 'slime', 'meat_and_bone', 'fried_egg', 'gluten', 'lamb', 'golden')
# Absent identifiers are NOT invented: include only existing player-visible registrations.
GROUPS = (
 ('stations', '設備與工作站', '设备与工作站', 'Stations',
  ('grill','skewering_table','oil_press','big_vat','advanced_rack')),
 ('tools', '工具與餐具', '工具与餐具', 'Tools and serving',
  ('skewer_recipe_book','skewer_recipe','skewer_plate','barbecue_blowtorch','stone_mortar','stone_pestle')),
 ('raw_skewers', '生烤串', '生烤串', 'Raw skewers', tuple('raw_'+x+'_skewer' for x in SKEWERS)),
 ('grilled_skewers', '熟烤串', '熟烤串', 'Grilled skewers', tuple('grilled_'+x+'_skewer' for x in SKEWERS)),
 ('special_skewers', '自由與特殊烤串', '自由与特殊烤串', 'Custom and special skewers',
  ('ordinary_skewer','secret_skewer','mysterious_skewer','dark_grilling')),
 ('seasoning', '調料瓶與調味料', '调料瓶与调味料', 'Seasoning',
  ('empty_seasoning_bottle','pending_seasoning','special_seasoning',
   'green_chili_powder','red_chili_powder','sichuan_pepper','onion_powder','houttuynia_powder',
   'canola_powder','totem_powder','dragon_egg_powder','crushed_chili','chili_powder','five_spice_powder',
   'black_pepper_powder','mustard_powder','cumin_powder','rock_salt','barbecue_sauce','ketchup','pickled_chopped_pepper')),
 ('oils', '油品與榨油產物', '油品与榨油产物', 'Oils and pressing products',
  ('canola_oil_bottle','canola_oil_bucket','secret_chili_oil_bucket','premium_chili_oil_bucket','oil_cake','oil_residue')),
 ('ingredients', '食材與加工原料', '食材与加工原料', 'Ingredients',
  ('beef_chunks','raw_lamb_cuts','chicken_skin','chicken_wing','squid_tentacle','minced_houttuynia',
   'carrot_dice','potato_slice','raw_sweet_potato_sheet','fresh_sweet_potato_sheet','sweet_potato_sheet',
   'raw_mantou_slice','unprocessed_starch','starch','sweet_potato_powder')),
 ('dishes', '菜餚與點心', '菜肴与点心', 'Dishes and treats',
  ('roasted_sweet_potato','roasted_chicken_wing','cold_houttuynia','wedding_candy','cup_cake',
   'sugared_tomato','pepper_honey','houttuynia_stir_fried_pork','green_pepper_squid_tentacles',
   'braised_chicken_wings','potato_beef_stew','red_sweet_potato_porridge','sour_spicy_noodles',
   'fragrant_crispy_potato','chicken_fried_rice','cola_chicken_wings','pan_fried_bun','braised_pork_balls','braised_chicken')),
 ('crops', '作物與種植', '作物与种植', 'Crops and planting',
  ('canola_seeds','canola','onion','sweet_potato','houttuynia','garlic','pepper_fruit')),
 ('pepper_tree', '花椒樹與木材', '花椒树与木材', 'Pepper tree and wood',
  ('pepper_sapling','pepper_leaves','pepper_log','pepper_wood')),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def encode(doc):
    return json.dumps(doc, ensure_ascii=False, indent=2) + '\n'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def definitions():
    rows = []
    for folder, kind in ((BP/'items','minecraft:item'), (BP/'blocks','minecraft:block')):
        for path in sorted(folder.rglob('*.json')):
            doc = load(path)
            if kind not in doc:
                continue
            desc = doc[kind]['description']
            identifier = desc['identifier']
            if identifier.startswith(NS):
                rows.append((path, doc, kind, identifier))
    return rows


def visible(desc):
    return desc.get('menu_category', {}).get('category') in ('items','equipment','nature','construction')


def make_groups(ids):
    require(all(i.startswith(NS) for i in ids), 'Foreign namespace in Grilling catalog')
    short_ids = {i[len(NS):] for i in ids}
    expected = [x for row in GROUPS for x in row[4]]
    require(len(expected) == len(set(expected)), 'Duplicate item in grouping specification')
    unknown = sorted(short_ids - set(expected))
    require(not unknown, 'Unclassified visible registrations: ' + ', '.join(unknown))
    result = []
    for key, tw, cn, en, order in GROUPS:
        members = [NS + x for x in order if x in short_ids]
        if members:
            result.append({'group_identifier': {'icon': members[0], 'name': GROUP_PREFIX+key}, 'items': members})
    flat = [x for group in result for x in group['items']]
    require(len(flat) == len(set(flat)) and set(flat) == set(ids), 'Missing or duplicate creative item')
    return result


def expected_catalog(groups):
    return {'format_version': '1.21.60', 'minecraft:crafting_items_catalog': {
        'categories': [{'category_name':'items', 'groups':groups}]}}


def strip_group_lines(text):
    return '\n'.join(line for line in text.splitlines()
                     if not line.split('=',1)[0].startswith(GROUP_PREFIX))


def localized(text, locale, active):
    kept = [line for line in text.splitlines() if line.split('=',1)[0] not in active]
    for key, tw, cn, en, _ in GROUPS:
        if GROUP_PREFIX+key in active:
            label = dict(zip(LOCALES, (tw, cn, en)))[locale]
            prefix = '森羅煙火' if locale == 'zh_TW' else '森罗烟火' if locale == 'zh_CN' else 'Kaleidoscope Grilling'
            kept.append(GROUP_PREFIX+key+'='+prefix+' · '+label)
    newline = '\r\n' if '\r\n' in text else '\n'
    return newline.join(kept) + newline


def immutable_digest():
    """All BP/RP payload, masking ONLY creative metadata and this release's version/name."""
    digest = hashlib.sha256()
    for pack in (BP, RP):
        for path in sorted(p for p in pack.rglob('*') if p.is_file()):
            rel = path.relative_to(PROJECT).as_posix()
            if rel == 'behavior_pack/item_catalog/crafting_item_catalog.json':
                continue
            data = path.read_bytes()
            if path.suffix == '.json':
                doc = load(path)
                if path.name == 'manifest.json' and path.parent in (BP,RP):
                    doc['header'].pop('version',None)
                    doc['header'].pop('name',None)
                    for module in doc.get('modules',[]): module.pop('version',None)
                    for dep in doc.get('dependencies',[]):
                        if dep.get('uuid') == 'bbbd2d60-52e5-53a6-8b9a-c09b0f516389': dep.pop('version',None)
                for kind in ('minecraft:item','minecraft:block'):
                    if kind in doc:
                        menu = doc[kind]['description'].get('menu_category',{})
                        menu.pop('category',None)
                        menu.pop('group',None)
                data = json.dumps(doc,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
            elif path.suffix == '.lang' and path.parent == RP/'texts':
                data = strip_group_lines(path.read_text(encoding='utf-8-sig')).encode()
            digest.update(rel.encode() + b'\0' + hashlib.sha256(data).digest())
    return digest.hexdigest()


def hidden_snapshots(rows):
    return {p.relative_to(PROJECT).as_posix():sha(p.read_bytes())
            for p,doc,kind,_ in rows if not visible(doc[kind]['description'])}


def mapping(groups):
    return {item:group['group_identifier']['name'] for group in groups for item in group['items']}


def check():
    report = load(REPORT)
    rows = definitions()
    ids = {i for _,doc,kind,i in rows if visible(doc[kind]['description'])}
    groups = make_groups(ids)
    require(load(BP/'item_catalog/crafting_item_catalog.json') == expected_catalog(groups), 'Creative catalog drift')
    by_id = mapping(groups)
    for path,doc,kind,identifier in rows:
        desc=doc[kind]['description']
        if visible(desc):
            require(desc['menu_category']['category']=='items' and desc['menu_category'].get('group')==by_id[identifier], f'Menu/catalog mismatch: {path}')
    require(sorted(ids)==report['visible_identifiers'], 'Creative visibility changed')
    require(hidden_snapshots(rows)==report['hidden_file_sha256'], 'Internal/hidden definition modified')
    require(immutable_digest()==report['non_creative_payload_sha256'], 'Gameplay/resource data changed outside creative metadata')
    for locale in LOCALES:
        text=(RP/f'texts/{locale}.lang').read_text(encoding='utf-8-sig')
        for group in groups:
            key=group['group_identifier']['name']
            values=[line.partition('=')[2] for line in text.splitlines() if line.partition('=')[0]==key]
            require(len(values)==1 and bool(values[0].strip()), f'Missing/duplicate group label: {locale}/{key}')
    require(all(group['group_identifier']['icon'] in group['items'] for group in groups), 'Invalid group icon')
    raw=next((g['items'] for g in groups if g['group_identifier']['name'].endswith('.raw_skewers')),[])
    cooked=next((g['items'] for g in groups if g['group_identifier']['name'].endswith('.grilled_skewers')),[])
    require([x.replace(':raw_',':',1) for x in raw]==[x.replace(':grilled_',':',1) for x in cooked], 'Raw/cooked skewers are not paired')
    for pack in (BP,RP): require(load(pack/'manifest.json')['header']['version']==VERSION, 'Manifest version mismatch')
    result={'version':'A2.7.70','groups':len(groups),'visible_items':len(ids),
            'hidden_definitions_unchanged':len(report['hidden_file_sha256']),
            'raw_cooked_pairs':len(raw),'gameplay_unchanged':True,'client_visuals_tested':False}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return result


def apply():
    require(not REPORT.exists(), 'Already migrated; use --check (never overwrite the baseline evidence)')
    require(load(BP/'manifest.json')['header']['version']==[2,7,69], 'Expected A2.7.69 base; stop on concurrent version change')
    rows=definitions()
    ids={i for _,doc,kind,i in rows if visible(doc[kind]['description'])}
    groups=make_groups(ids)
    catalog=load(BP/'item_catalog/crafting_item_catalog.json')
    previous={i for cat in catalog['minecraft:crafting_items_catalog']['categories'] for g in cat['groups'] for i in g.get('items',[])}
    require(not previous-ids, 'Old catalog has missing/hidden references: '+', '.join(sorted(previous-ids)))
    before=immutable_digest()
    hidden=hidden_snapshots(rows)
    by_id=mapping(groups)
    pending={BP/'item_catalog/crafting_item_catalog.json': encode(expected_catalog(groups))}
    for path,doc,kind,identifier in rows:
        if visible(doc[kind]['description']):
            new=deepcopy(doc)
            new[kind]['description']['menu_category'].update(category='items',group=by_id[identifier])
            pending[path]=encode(new)
    active={g['group_identifier']['name'] for g in groups}
    for locale in LOCALES:
        path=RP/f'texts/{locale}.lang'
        pending[path]=localized(path.read_bytes().decode('utf-8-sig'),locale,active)
    for pack,suffix in ((BP,'BP'),(RP,'RP')):
        path=pack/'manifest.json';doc=load(path)
        doc['header']['name']='Kaleidoscope Grilling A2.7.70 Creative Groups '+suffix
        doc['header']['version']=VERSION
        for module in doc['modules']: module['version']=VERSION
        for dep in doc.get('dependencies',[]):
            if dep.get('uuid')=='bbbd2d60-52e5-53a6-8b9a-c09b0f516389': dep['version']=VERSION
        pending[path]=encode(doc)
    config=load(PROJECT/'config.json')
    config['name']='Kaleidoscope Grilling A2.7.70 Creative Groups'
    for plugin in config.get('compiler',{}).get('plugins',[]):
        if isinstance(plugin,list) and plugin[0]=='simpleRewrite':
            plugin[1]['packName']='Kaleidoscope_Grilling_A2_7_70_Creative_Groups'
    pending[PROJECT/'config.json']=encode(config)
    verifier=ROOT/'development/gameplay_core/verify_current.py'
    text=verifier.read_text(encoding='utf-8-sig')
    marker='    (2, 7, 69): "verify_a2769.py",'
    require(text.count(marker)==1,'Current verifier registry differs')
    pending[verifier]=text.replace(marker,marker+'\n    (2, 7, 70): "verify_a2770.py",')
    old=ROOT/'development/gameplay_core/verify_a2769.py';text=old.read_text(encoding='utf-8-sig')
    require(text.count('def source_guards():')==1,'A2.7.69 guard layout changed')
    require(text.count("for side in (BP,RP):assert load(side/'manifest.json')['header']['version']==[2,7,69]")==1,'A2.7.69 version guard changed')
    text=text.replace('def source_guards():','def source_guards(expected_version=(2,7,69)):')
    text=text.replace("for side in (BP,RP):assert load(side/'manifest.json')['header']['version']==[2,7,69]",
                      "for side in (BP,RP):assert load(side/'manifest.json')['header']['version']==list(expected_version)")
    pending[old]=text
    report={
      'version':'A2.7.70','base_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
      'scope':'Grilling BP/RP creative metadata only; Tavern and Cookery remain unchanged',
      'category':'items','groups':[{'key':g['group_identifier']['name'],'icon':g['group_identifier']['icon'],'count':len(g['items']),'items':g['items']} for g in groups],
      'visible_identifiers':sorted(ids),'previous_catalog_count':len(previous),
      'already_visible_missing_from_old_catalog':sorted(ids-previous),
      'hidden_file_sha256':hidden,'non_creative_payload_sha256':before,
      'gameplay_changed':False,'minecraft_tested':False,'bds_tested':False,'client_visuals_tested':False,
    }
    # All inputs validated before writing. Only UI metadata/version fields were changed.
    for path,text in pending.items(): path.write_text(text,encoding='utf-8',newline='\n')
    require(before==immutable_digest(),'Non-creative data changed during generation')
    REPORT.write_text(encode(report),encoding='utf-8')
    check()


def main():
    parser=argparse.ArgumentParser();mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--apply',action='store_true');mode.add_argument('--check',action='store_true')
    args=parser.parse_args()
    if args.apply: apply()
    else: check()

if __name__=='__main__': main()
