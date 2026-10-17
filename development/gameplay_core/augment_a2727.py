from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core'
BP=P/'behavior_pack'
RP=P/'resource_pack'
DEV=Path(__file__).parent
VERSION=[2,7,27]

OLD_RUNTIME_IMPORTS=(
 "import './a272_cookery_processing_runtime.js';",
 "import './a278_basic_chopping_runtime.js';",
 "import './a2711_mantou_chopping_runtime.js';",
 "import './a2713_houttuynia_processing_runtime.js';",
 "import './a2716_canola_processing_runtime.js';",
 "import './a2718_onion_processing_runtime.js';",
 "import './a2724_red_chili_processing_runtime.js';",
)
NEW_RUNTIME_IMPORT="import './a2727_cookery_host_recipes_runtime.js';"

def load(p):
 return json.loads(p.read_text(encoding='utf-8-sig'))

def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(
  (json.dumps(d,ensure_ascii=False,indent=2)+'\n') if isinstance(d,(dict,list)) else d,
  encoding='utf-8'
 )

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in (
  (bm,'Kaleidoscope Grilling A2.7.27 Cookery Host Reuse BP'),
  (rm,'Kaleidoscope Grilling A2.7.27 Cookery Host Reuse RP'),
 ):
  doc['header']['version']=VERSION
  doc['header']['name']=name
  for module in doc.get('modules',[]):
   module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:
   dep['version']=VERSION
 write(BP/'manifest.json',bm)
 write(RP/'manifest.json',rm)

 cfg=load(P/'config.json')
 cfg['name']='Kaleidoscope Grilling A2.7.27 Cookery Host Reuse'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_27_Cookery_Host_Reuse'
 write(P/'config.json',cfg)

def patch_runtime():
 shutil.copy2(
  DEV/'a2727_cookery_host_recipes_core.js',
  BP/'scripts/a2727_cookery_host_recipes_core.js'
 )
 shutil.copy2(
  DEV/'a2727_cookery_host_recipes_runtime.js',
  BP/'scripts/a2727_cookery_host_recipes_runtime.js'
 )

 path=BP/'scripts/main.js'
 s=path.read_text(encoding='utf-8')

 for line in OLD_RUNTIME_IMPORTS:
  if s.count(line)!=1:
   raise RuntimeError('A2.7.27 expected one historical Cookery runtime import: '+line)
  s=s.replace(line+'\n','',1)

 anchor="import './a26_oil_machine_runtime.js';"
 if s.count(anchor)!=1:
  raise RuntimeError('A2.7.27 main import anchor drift')
 s=s.replace(anchor,anchor+'\n'+NEW_RUNTIME_IMPORT,1)
 path.write_text(s,encoding='utf-8')

def report():
 write(P/'reports/a2727-host-reuse.json',{
  'version':'A2.7.27',
  'scope':'consolidate Cookery-hosted recipe registration and remove duplicated active listeners',
  'cookery_host':{
   'bedrock_reference':'Kaleidoscope Cookery v1.0.6 (Unofficial)',
   'curseforge_project_id':1673664,
   'archive_sha256':'c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351',
   'public_extension_api':1,
   'events':[
    'kaleidoscope_cookery:api_ready',
    'kaleidoscope_cookery:api_ping',
    'kaleidoscope_cookery:register_recipe'
   ],
   'host_owned_station_mechanics':['chopping_board','millstone']
  },
  'before':{
   'active_recipe_runtime_modules':7,
   'startup_api_pings':2,
   'ready_listeners':7
  },
  'after':{
   'active_recipe_runtime_modules':1,
   'startup_api_pings':1,
   'ready_listeners':1,
   'hosted_recipe_rows':9,
   'chopping_board_rows':5,
   'millstone_rows':4
  },
  'historical_modules_retained_for_slice_rebuilds':True,
  'beef_board_override_retained':True,
  'beef_board_reason':(
   'Cookery 1.0.6 resolves BOARD_RECIPES[id] before getExtensionBoardRecipe(id), '
   'so minecraft:beef cannot be overridden through the public extension API.'
  ),
  'guide_already_uses_cookery_host_api':True,
  'next_reuse_targets':[
   'centralize Cookery oil-pot compatibility used by main.js and a26_oil_machine_runtime.js',
   'replace canola/onion/sweet-potato duplicate crop runtimes with a data-driven crop host',
   'replace per-food itemCompleteUse listeners with one food-effect table and handler',
   'replace future per-slice CI boilerplate with shared helpers while retaining old rebuild inputs'
  ],
  'minecraft_tested':False,
  'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,26]:
  raise RuntimeError('A2.7.27 must augment verified A2.7.26')
 patch_versions()
 patch_runtime()
 report()
 print('A2.7.27 Cookery host reuse refactor complete')

if __name__=='__main__':
 main()
