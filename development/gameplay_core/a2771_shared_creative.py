"""Append Grilling to the real Cookery 1.0.6 groups, as Chinese Food 1.0.2 does.
No new creative groups, host icon/label overrides, or gameplay changes.
"""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import subprocess
import a2770_creative_catalog as baseline

ROOT, PROJECT, BP, RP = baseline.ROOT, baseline.PROJECT, baseline.BP, baseline.RP
DEV = Path(__file__).resolve().parent
FIXTURE = DEV / 'fixtures/a2771-series-catalogs.json'
REPORT = PROJECT / 'reports/a2771-shared-creative-groups.json'
VERSION = [2, 7, 71]
NS = 'kaleidoscope_grilling:'
HOST = 'kaleidoscope_cookery:itemGroup.name.'
CATEGORY = 'equipment'
require, load, encode = baseline.require, baseline.load, baseline.encode
SOURCE_HASHES = {
 'chinese_food': ('2bccb8957ee5f165e72f148860c6acb1478af5b5b42d5e094b6aa8118abcb8bf',
                  'd9cab49ef88d3d316f095a490badf73269f9045746c4975cee80b31db95f9431'),
 'cookery': ('c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351',
             '8b3248ab8216ecf811ff8c873221985f47961c21ebe05389605a21646cbf22f0'),
}
SKEWERS = ('beef','pork_belly','chicken_skin','mid_wing','squid_tentacle','fish',
 'sweet_potato_sheet','potato_slice','caterpillar','mushroom','bun_slice','ender_pearl',
 'meatball','slime','meat_and_bone','fried_egg','gluten','lamb','golden')
# Mappings to existing host groups; no new groups with merely similar labels.
ASSIGNMENTS = {
 'tools': ('empty_seasoning_bottle',),
 'cooking_stations': ('grill','oil_press','big_vat'),
 'storage_utility': ('advanced_rack',),
 'crops': ('canola_seeds','onion','sweet_potato','houttuynia','pepper_sapling'),
 'ingredients': (
    'beef_chunks','chicken_skin','chicken_wing','squid_tentacle','minced_houttuynia',
    'carrot_dice','potato_slice','raw_sweet_potato_sheet','raw_mantou_slice','sweet_potato_powder',
    *('raw_'+s+'_skewer' for s in SKEWERS),
    'special_seasoning','green_chili_powder','red_chili_powder','sichuan_pepper',
    'onion_powder','houttuynia_powder','canola_powder','totem_powder','dragon_egg_powder',
    'canola_oil_bucket','secret_chili_oil_bucket','premium_chili_oil_bucket','oil_cake','oil_residue'),
 'foods': (*('grilled_'+s+'_skewer' for s in SKEWERS),
    'ordinary_skewer','mysterious_skewer','dark_grilling','roasted_sweet_potato',
    'roasted_chicken_wing','cold_houttuynia','wedding_candy','sugared_tomato','pepper_honey',
    'houttuynia_stir_fried_pork','green_pepper_squid_tentacles','braised_chicken_wings',
    'potato_beef_stew','red_sweet_potato_porridge','sour_spicy_noodles'),
 'other_blocks': ('pepper_log','pepper_leaves'),
 'recipe_pages': ('skewer_recipe_book',),
}


def canonical_sha(doc):
    data=json.dumps(doc,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
    return hashlib.sha256(data).hexdigest()


def catalog_groups(doc):
    for cat in doc['minecraft:crafting_items_catalog']['categories']:
        for group in cat['groups']:
            yield cat['category_name'], group


def make_fixture(audit):
    result={}
    for key, (pack_sha, cat_sha) in SOURCE_HASHES.items():
        source=audit[key]
        require(source['pack_sha256']==pack_sha, key+': wrong public reference pack')
        require(len(source['catalogs'])==1, key+': ambiguous source catalog')
        path,row=next(iter(source['catalogs'].items()))
        require(canonical_sha(row['content'])==cat_sha,key+': source catalog changed')
        group_names={g['group_identifier']['name'] for _,g in catalog_groups(row['content'])}
        labels={p.rsplit('/',1)[-1][:-5]:{k:v for k,v in values.items() if k in group_names}
          for p,values in source['group_labels'].items()
          if '[RP]' in p and p.endswith(('/en_US.lang','/zh_CN.lang','/zh_TW.lang'))}
        result[key]={k:source[k] for k in ('version','curseforge_file_id','download_url','pack_sha256')}
        result[key].update(catalog_path=path,catalog_file_sha256=row['sha256'],
          catalog_canonical_sha256=cat_sha,catalog=row['content'],labels=labels)
    return result


def validate_fixture(fixture):
    for key,(pack_sha,cat_sha) in SOURCE_HASHES.items():
        require(fixture[key]['pack_sha256']==pack_sha, key+': pack fingerprint mismatch')
        require(canonical_sha(fixture[key]['catalog'])==cat_sha,key+': catalog fingerprint mismatch')
    host={(c,g['group_identifier']['name']) for c,g in catalog_groups(fixture['cookery']['catalog'])}
    shared={(c,g['group_identifier']['name']) for c,g in catalog_groups(fixture['chinese_food']['catalog'])
            if g['group_identifier']['name'].startswith(HOST)}
    require(len(shared)==10 and shared<=host, 'Chinese Food no longer proves the shared-group pattern')
    return host


def build_catalog(ids, fixture):
    host=validate_fixture(fixture)
    planned=[NS+x for members in ASSIGNMENTS.values() for x in members]
    require(len(planned)==len(set(planned)), 'Duplicate Grilling assignment')
    require(set(planned)==set(ids), 'Visible item set differs: '+str(sorted(set(planned)^set(ids))))
    groups=[]
    for key,members in ASSIGNMENTS.items():
        name=HOST+key
        require((CATEGORY,name) in host, 'Not an existing host group: '+name)
        # Omitting icon is deliberate: inherit the host-defined group icon.
        groups.append({'group_identifier':{'name':name},'items':[NS+x for x in members]})
    return {'format_version':'1.21.60','minecraft:crafting_items_catalog':{
        'categories':[{'category_name':CATEGORY,'groups':groups}]}}


def merged_members(catalogs):
    """Catalog data comparison only; NOT a Minecraft client/GUI simulation."""
    merged={}
    for catalog in catalogs:
        for category,group in catalog_groups(catalog):
            key=(category,group['group_identifier']['name'])
            merged.setdefault(key,[]).extend(group['items'])
    return merged


def remove_own_labels(data):
    # Preserve every other byte, non-creative translation, and CRLF/LF choice.
    return b''.join(line for line in data.splitlines(keepends=True)
      if not line.split(b'=',1)[0].startswith(b'kaleidoscope_grilling:itemGroup.'))


def check():
    fixture=load(FIXTURE)
    report=load(REPORT)
    previous=load(baseline.REPORT)
    rows=baseline.definitions()
    ids={i for _,doc,kind,i in rows if baseline.visible(doc[kind]['description'])}
    catalog=build_catalog(ids,fixture)
    require(load(BP/'item_catalog/crafting_item_catalog.json')==catalog,'Shared catalog drift')
    by_id={i:(cat,g['group_identifier']['name']) for cat,g in catalog_groups(catalog) for i in g['items']}
    for path,doc,kind,identifier in rows:
        desc=doc[kind]['description']
        if baseline.visible(desc):
            menu=desc['menu_category']
            require((menu['category'],menu.get('group'))==by_id[identifier], 'Menu/catalog mismatch: '+str(path))
    require(sorted(ids)==previous['visible_identifiers']==report['visible_identifiers'],'Visibility changed')
    require(baseline.hidden_snapshots(rows)==previous['hidden_file_sha256'],'Internal definitions changed')
    require(baseline.immutable_digest()==previous['non_creative_payload_sha256'],'Non-creative payload changed')
    for path in RP.joinpath('texts').glob('*.lang'):
        data=path.read_bytes()
        require(remove_own_labels(data)==data, 'Obsolete own group label: '+str(path))
        require(HOST.encode() not in data, 'Do not override host localization: '+str(path))
    for category,group in catalog_groups(catalog):
        require(set(group['group_identifier'])=={'name'},'Do not override host group icon')
        key=group['group_identifier']['name']
        for locale in ('zh_TW','zh_CN','en_US'):
            require(bool(fixture['cookery']['labels'][locale].get(key)), 'Missing host label: '+key)
    ref_catalogs=[fixture[k]['catalog'] for k in ('cookery','chinese_food')]
    original=merged_members(ref_catalogs)
    orders=0
    for packs in itertools.permutations([*ref_catalogs,catalog]):
        merged=merged_members(packs)
        require(set(merged)==set(original), 'Grilling created a new series group')
        flat=[i for members in merged.values() for i in members]
        require(len(flat)==len(set(flat)), 'Duplicate catalog entries across packs')
        require(set(flat)==set(i for v in original.values() for i in v)|ids, 'Merge lost items')
        orders+=1
    for pack in (BP,RP): require(load(pack/'manifest.json')['header']['version']==VERSION,'Version mismatch')
    require(report['version']=='A2.7.71' and report['new_groups_created']==0,'Report mismatch')
    result={'version':'A2.7.71','shared_host_groups':len(ASSIGNMENTS),'new_groups_created':0,
      'category':CATEGORY,'visible_items':len(ids),'hidden_definitions_unchanged':len(previous['hidden_file_sha256']),
      'catalog_merge_orders_checked':orders,'non_creative_payload_unchanged':True,
      'minecraft_tested':False,'client_visuals_tested':False}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return result


def apply(reference_file):
    require(not REPORT.exists(),'Already applied; use --check')
    baseline.check()  # Refuse an unexpected or concurrent base.
    fixture=make_fixture(load(reference_file))
    previous=load(baseline.REPORT)
    rows=baseline.definitions()
    ids={i for _,doc,kind,i in rows if baseline.visible(doc[kind]['description'])}
    catalog=build_catalog(ids,fixture)
    by_id={i:(cat,g['group_identifier']['name']) for cat,g in catalog_groups(catalog) for i in g['items']}
    pending={BP/'item_catalog/crafting_item_catalog.json':encode(catalog).encode(),FIXTURE:encode(fixture).encode()}
    for path,doc,kind,identifier in rows:
        if baseline.visible(doc[kind]['description']):
            new=deepcopy(doc);category,name=by_id[identifier]
            new[kind]['description']['menu_category'].update(category=category,group=name)
            pending[path]=encode(new).encode()
    for path in RP.joinpath('texts').glob('*.lang'):pending[path]=remove_own_labels(path.read_bytes())
    for pack,suffix in ((BP,'BP'),(RP,'RP')):
        path=pack/'manifest.json';doc=load(path)
        doc['header']['name']='Kaleidoscope Grilling A2.7.71 Shared Series Groups '+suffix
        doc['header']['version']=VERSION
        for module in doc['modules']:module['version']=VERSION
        for dep in doc.get('dependencies',[]):
            if dep.get('uuid')=='bbbd2d60-52e5-53a6-8b9a-c09b0f516389':dep['version']=VERSION
        pending[path]=encode(doc).encode()
    path=PROJECT/'config.json';doc=load(path)
    doc['name']='Kaleidoscope Grilling A2.7.71 Shared Series Groups'
    for plugin in doc.get('compiler',{}).get('plugins',[]):
        if isinstance(plugin,list) and plugin[0]=='simpleRewrite':
            plugin[1]['packName']='Kaleidoscope_Grilling_A2_7_71_Shared_Series_Groups'
    pending[path]=encode(doc).encode()
    path=DEV/'verify_current.py';text=path.read_text(encoding='utf-8-sig')
    marker='    (2, 7, 70): "verify_a2770.py",'
    require(text.count(marker)==1,'Verifier registry changed')
    pending[path]=text.replace(marker,marker+'\n    (2, 7, 71): "verify_a2771.py",').encode()
    report={'version':'A2.7.71','supersedes':'A2.7.70 independent groups (incorrect requirement interpretation)',
      'base_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
      'reference_sources':{k:{n:v[n] for n in ('version','curseforge_file_id','pack_sha256','catalog_file_sha256','catalog_canonical_sha256')} for k,v in fixture.items()},
      'category':CATEGORY,'new_groups_created':0,'host_icons_and_localization_overridden':False,
      'visible_identifiers':sorted(ids),'non_creative_payload_sha256':previous['non_creative_payload_sha256'],
      'hidden_definitions_unchanged':len(previous['hidden_file_sha256']),
      'groups':[{'name':g['group_identifier']['name'],'count':len(g['items']),'items':g['items']} for _,g in catalog_groups(catalog)],
      'minecraft_tested':False,'bds_tested':False,'client_visuals_tested':False}
    pending[REPORT]=encode(report).encode()
    for path,data in pending.items():path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    check()


def main():
    parser=argparse.ArgumentParser();mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--apply',action='store_true');mode.add_argument('--check',action='store_true')
    parser.add_argument('--references',type=Path)
    args=parser.parse_args()
    if args.apply:
        require(args.references is not None,'--references is required for apply')
        apply(args.references)
    else:check()

if __name__=='__main__':main()
