"""Consolidated A2.8.0 source/data/asset gate. No Minecraft interaction simulation."""
from pathlib import Path
import argparse, hashlib, itertools, json, re, subprocess, sys
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core'; B=P/'behavior_pack'; R=P/'resource_pack'; D=Path(__file__).parent
VERSION=[2,8,0]
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def run(*args):subprocess.run(args,cwd=ROOT,check=True)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def runtime_digest():
 h=hashlib.sha256()
 for pack in (B,R):
  for p in sorted(x for x in pack.rglob('*') if x.is_file() and not x.name.startswith('.')):
   h.update(p.relative_to(P).as_posix().encode()+b'\0'+hashlib.sha256(p.read_bytes()).digest())
 return h.hexdigest()
def catalog_gate():
 import a2771_shared_creative as c
 fixture=c.load(c.FIXTURE);previous=c.load(c.baseline.REPORT);report=c.load(c.REPORT)
 rows=c.baseline.definitions();ids={i for _,doc,kind,i in rows if c.baseline.visible(doc[kind]['description'])}
 expected=c.build_catalog(ids,fixture)
 assert c.load(B/'item_catalog/crafting_item_catalog.json')==expected
 lookup={i:(category,g['group_identifier']['name']) for category,g in c.catalog_groups(expected) for i in g['items']}
 for path,doc,kind,i in rows:
  if c.baseline.visible(doc[kind]['description']):
   menu=doc[kind]['description']['menu_category'];assert (menu['category'],menu.get('group'))==lookup[i],path
 assert sorted(ids)==previous['visible_identifiers']==report['visible_identifiers']
 assert c.baseline.hidden_snapshots(rows)==previous['hidden_file_sha256']
 for p in (R/'texts').glob('*.lang'):
  assert c.remove_own_labels(p.read_bytes())==p.read_bytes()
  assert c.HOST.encode() not in p.read_bytes()
 for category,g in c.catalog_groups(expected):
  assert set(g['group_identifier'])=={'name'}
  for locale in ('en_US','zh_CN','zh_TW'):assert fixture['cookery']['labels'][locale][g['group_identifier']['name']]
 refs=[fixture[x]['catalog'] for x in ('cookery','chinese_food')];original=c.merged_members(refs)
 for order in itertools.permutations([*refs,expected]):
  merged=c.merged_members(order);flat=[i for group in merged.values() for i in group]
  assert set(merged)==set(original) and len(flat)==len(set(flat))
  assert set(flat)==set(i for group in original.values() for i in group)|ids
 return {'host_groups':len(c.ASSIGNMENTS),'visible_items':len(ids),'hidden_definitions':len(previous['hidden_file_sha256']),'catalog_orders':6}
def helper_gate():
 geometries={g['description']['identifier']:g for p in R.rglob('*.geo.json') for g in load(p).get('minecraft:geometry',[])}
 controllers=load(R/'render_controllers/a2770_placed.render_controllers.json')['render_controllers']
 for name in ('seasoning','oil'):
  server=load(B/f'entities/a2770_placed_{name}.json')['minecraft:entity'];client=load(R/f'entity/a2770_placed_{name}.entity.json')['minecraft:client_entity']['description']
  assert server['description']['identifier']==client['identifier'] and not server['description']['is_spawnable']
  components=server['components'];assert 'minecraft:transient' in components
  assert components['minecraft:physics']=={'has_gravity':False,'has_collision':False}
  assert components['minecraft:collision_box']=={'width':0,'height':0}
  assert not any(x in components for x in ('minecraft:loot','minecraft:inventory','minecraft:interact'))
  properties=server['description']['properties'];assert len(properties)<=32 and all(p['client_sync'] for p in properties.values())
  for g in client['geometry'].values():
   assert g in geometries
   for bone in geometries[g]['bones']:
    assert 'binding' not in bone
    for cube in bone.get('cubes',[]):assert min(cube['size'])>0
  for t in client['textures'].values():assert (R/(t+'.png')).is_file()
  for row in client['render_controllers']:
   rc=next(iter(row));assert rc in controllers
   text=json.dumps(row)+json.dumps(controllers[rc])
   for prop in re.findall(r"q\.property\('([^']+)'\)",text):assert prop in properties,(rc,prop)
   for group in ('Geometry','Texture','Material'):
    for alias in re.findall(group+r'\.([a-zA-Z0-9_]+)',text):assert alias in client[{'Geometry':'geometry','Texture':'textures','Material':'materials'}[group]],alias
 special=[g for id,g in geometries.items() if id.startswith('geometry.kg_a2770.seasoning.')]
 assert len(special)==40
 for g in special:
  cubes=g['bones'][0]['cubes'];assert len(cubes)==1 and cubes[0]['origin']==[-2.5,.5,-2.5]
 runtime=(B/'scripts/a2770_placed_visual_runtime.js').read_text()
 for forbidden in ('world.setDynamicProperty','.setType(','.setPermutation('):assert forbidden not in runtime
 assert 'MAX_HELPERS=1024' in runtime and 'BUDGET=12' in runtime and 'RANGE_SQ=48*48' in runtime
 return {'helpers':2,'placed_controllers':len(controllers),'special_fill_geometries':len(special)}
def display_gate():
 sys.path.insert(0,str(ROOT/'tools'))
 import apply_skewer_display_parity as source
 expected,count=source.canonical_java_display();index=source.geometry_index()
 animation=load(R/'animations/a2764_skewer_java_display.animation.json')['animations']
 for alias,display in expected.items():
  body=animation[source.ANIM_IDS[alias]]['bones'];assert set(body)=={'display'}
  for java,bedrock in (('translation','position'),('rotation','rotation'),('scale','scale')):assert body['display'][bedrock]==display[java]
 skewers=list((R/'attachables').glob('*_skewer.attachable.json'));assert len(skewers)==39
 refs=set()
 for p in skewers:
  desc=load(p)['minecraft:attachable']['description'];assert desc['animations']==source.ANIM_IDS
  assert desc['scripts']['pre_animation'] and len(desc['scripts']['animate'])==4
  assert desc['render_controllers']==['controller.render.kg_a22.bite']
  for id in desc['geometry'].values():
   refs.add(id);assert id.startswith('geometry.kg_a22.')
   g=next(g for g in load(index[id])['minecraft:geometry'] if g['description']['identifier']==id)
   bones={b['name']:b for b in g['bones']}
   assert bones['root']['binding']==source.ROOT_BINDING and bones['display']=={'name':'display','parent':'root','pivot':[0,0,0]}
   assert all(b.get('parent')!='root' for name,b in bones.items() if name not in ('root','display'))
 assert len(refs)==150
 for p in (R/'attachables').glob('*seasoning*.json'):
  desc=load(p)['minecraft:attachable']['description'];assert len(desc.get('animations',{}))==4
  assert all('a2763.seasoning_' in x for x in desc['animations'].values())
 return {'skewers':len(skewers),'active_bite_geometries':len(refs),'java_display_reports':count}
def source_gate():
 import verify_a2769 as prior
 materials=prior.source_guards(VERSION)
 main=(B/'scripts/main.js').read_text()
 for module in ('guide/main.js','a2770_placed_visual_runtime.js'):assert main.count("import './"+module+"';")==1
 assert 'writeTickState(block,beforeState,state)' in main
 assert not (B/'scripts/interaction_intent.js').exists(),'do not duplicate the shared intent implementation'
 for name in ('a23_oil_world.js','a25_plate_recipe_runtime.js','a26_oil_machine_runtime.js','a2722_cold_houttuynia_runtime.js','a2737_offhand_oil_fill_runtime.js'):
  text=(B/'scripts'/name).read_text();assert 'interactionIntentStillCurrent' in text,name
 assert 'captureInteractionIntent(player,eventStack)' in (B/'scripts/a271_sweet_potato_runtime.js').read_text()
 for path in (ROOT/'.github/workflows').glob('*.yml'):
  assert not any(token in path.name for token in ('bootstrap','integration-source-audit','integration-asset-audit','integration-refresh','grilling-series-reference'))
 assert not (ROOT/'.github/workflows/gameplay-core-canonical.yml').exists()
 assert not (B/'entities/player.json').exists() and not (R/'entity/player.entity.json').exists()
 for side in (B,R):assert load(side/'manifest.json')['header']['version']==VERSION
 assert 'pbr' in load(R/'manifest.json')['capabilities']
 return materials

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--compiled',action='store_true');parser.add_argument('--offline',action='store_true');args=parser.parse_args()
 from verify_a2766 import check_assets
 assets=check_assets(java_display=True);catalog=catalog_gate();helper=helper_gate();display=display_gate();materials=source_gate()
 proof=load(P/'reports/a280-integration-invariants.json')
 assert runtime_digest()==proof['runtime_sha256'],'audited runtime changed; update the reviewed integration manifest intentionally'
 for path,expected in proof['preserved_core_sha256'].items():assert digest(ROOT/path)==expected,path
 for record in load(ROOT/'docs/integration/early-pr-resolutions.json').values():
  for row in record['files']:
   file=ROOT/'history/integrated-pr'/record['archive']/row['path'];data=file.read_bytes()
   assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob']
 scripts=[('a2770_placed_visual_assets.py',['--check']),('a2764_rebake_skewer_hand_geometry.py',['--check']),('test_vibrant_gate.py',[]),('test_a2771_catalog.py',[])]
 for script,flags in scripts:run(sys.executable,str(D/script),*flags)
 for script in ('test_a275_core.mjs','test_a276_core.mjs','test_a277_core.mjs','test_a2762_core.mjs','test_a2769_core.mjs','test_a2770_core.mjs','test_a280_integrated.mjs'):run('node',str(D/script))
 run(sys.executable,str(ROOT/'tools/check_grilling_guide.py'))
 run(sys.executable,str(ROOT/'tools/audit_grilling_render.py'),'--fail-on-error')
 if not args.offline:
  import verify_a2769 as prior
  prior.java_contract();run(sys.executable,str(D/'verify_a2761_java_interaction_contract.py'))
 for p in (B/'scripts').rglob('*.js'):run('node','--check',str(p))
 print(json.dumps({'version':'A2.8.0','catalog':catalog,'helpers':helper,'display':display,'assets':assets,'material_maps':materials,'runtime_sha256':proof['runtime_sha256'],'java_network_contract_checked':not args.offline,'compiled_requested':args.compiled,'minecraft_tested':False,'bds_tested':False,'client_visuals_tested':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
