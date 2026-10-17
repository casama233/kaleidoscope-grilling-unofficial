from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core'
BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,31]

OLD_IMPORTS=(
 "import './a2715_canola_crop_runtime.js';",
 "import './a2717_onion_crop_runtime.js';",
 "import './a2719_sweet_potato_crop_runtime.js';",
)
NEW_IMPORT="import './a2731_farmland_crop_host_runtime.js';"

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text((json.dumps(d,ensure_ascii=False,indent=2)+'\n') if isinstance(d,(dict,list)) else d,encoding='utf-8')

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in (
  (bm,'Kaleidoscope Grilling A2.7.31 Farmland Crop Host BP'),
  (rm,'Kaleidoscope Grilling A2.7.31 Farmland Crop Host RP'),
 ):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json')
 cfg['name']='Kaleidoscope Grilling A2.7.31 Farmland Crop Host'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_31_Farmland_Crop_Host'
 write(P/'config.json',cfg)

def patch_runtime():
 shutil.copy2(DEV/'a2731_farmland_crop_host_core.js',BP/'scripts/a2731_farmland_crop_host_core.js')
 shutil.copy2(DEV/'a2731_farmland_crop_host_runtime.js',BP/'scripts/a2731_farmland_crop_host_runtime.js')

 path=BP/'scripts/main.js';s=path.read_text(encoding='utf-8')
 for line in OLD_IMPORTS:
  if s.count(line)!=1:
   raise RuntimeError('A2.7.31 expected one legacy crop runtime import: '+line)
  s=s.replace(line+'\n','',1)

 anchor="import './a2714_houttuynia_crop_runtime.js';"
 if s.count(anchor)!=1:raise RuntimeError('A2.7.31 crop host import anchor drift')
 s=s.replace(anchor,anchor+'\n'+NEW_IMPORT,1)
 path.write_text(s,encoding='utf-8')

def report():
 write(P/'reports/a2731-crop-host.json',{
  'version':'A2.7.31',
  'scope':'consolidate ordinary Grilling farmland crop runtimes without changing crop semantics',
  'design_reference':{
   'cookery_java_base_crop_block_blob':'fd8c6aa62714043c42535027818ce6dd03b48b84',
   'principle':'share crop lifecycle machinery; keep per-crop data/overrides separate',
   'behavior_copied_from_cookery_base_crop_block':False,
   'reason':'Java Grilling canola/onion/sweet-potato classes extend vanilla CropBlock, so Cookery mature right-click harvest semantics must not be imported.'
  },
  'cookery_bedrock':{
   'version':'1.0.6',
   'archive_sha256':'c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351',
   'public_crop_extension_detected':False
  },
  'before':{
   'ordinary_farmland_runtime_modules':3,
   'ordinary_farmland_startup_subscribers':3,
   'duplicated_helper_sets':3,
   'grass_acquisition_subscribers':1
  },
  'after':{
   'ordinary_farmland_runtime_modules':1,
   'ordinary_farmland_startup_subscribers':1,
   'shared_helper_sets':1,
   'registered_crop_components':3,
   'grass_acquisition_subscribers':1
  },
  'hosted_crops':['canola','onion','sweet_potato'],
  'houttuynia_special_runtime_retained':True,
  'component_ids_unchanged':True,
  'block_json_unchanged':True,
  'old_runtime_files_retained_for_historical_slice_rebuilds':True,
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,30]:
  raise RuntimeError('A2.7.31 must augment verified A2.7.30')
 patch_versions();patch_runtime();report()
 print('A2.7.31 farmland crop host refactor complete')

if __name__=='__main__':
 main()
