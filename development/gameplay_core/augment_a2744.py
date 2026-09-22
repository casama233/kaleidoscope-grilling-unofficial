from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,44]
NEW_FILES=('a2744_skewer_plate_hud_core.js','a2744_skewer_plate_hud_provider.js')
LANG={
 'en_US.lang':[
  'jade.kaleidoscope_grilling.skewer_plate.count=Skewers placed: %1$s/%2$s',
  'jade.kaleidoscope_grilling.skewer_plate.empty=Empty plate; right-click with a skewer to add it',
  'jade.kaleidoscope_grilling.skewer_plate.take=Right-click with an empty hand to take the last skewer',
  'jade.kaleidoscope_grilling.skewer_plate.pack=Break to pack and carry the whole plate',
 ],
 'zh_CN.lang':[
  'jade.kaleidoscope_grilling.skewer_plate.count=已放置烤串：%1$s/%2$s',
  'jade.kaleidoscope_grilling.skewer_plate.empty=空盘，手持烤串右键放入',
  'jade.kaleidoscope_grilling.skewer_plate.take=空手右键取回最后放入的烤串',
  'jade.kaleidoscope_grilling.skewer_plate.pack=左键破坏，整体打包携带',
 ],
 'zh_TW.lang':[
  'jade.kaleidoscope_grilling.skewer_plate.count=已放置烤串：%1$s/%2$s',
  'jade.kaleidoscope_grilling.skewer_plate.empty=空盤，手持烤串右鍵放入',
  'jade.kaleidoscope_grilling.skewer_plate.take=空手右鍵取回最後放入的烤串',
  'jade.kaleidoscope_grilling.skewer_plate.pack=左鍵破壞，整體打包攜帶',
 ],
}

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.44 Skewer Plate HUD Provider BP'),(rm,'Kaleidoscope Grilling A2.7.44 Skewer Plate HUD Provider RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.44 Skewer Plate HUD Provider'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_44_Skewer_Plate_HUD_Provider'
 write(P/'config.json',cfg)

def patch_plate_runtime():
 p=BP/'scripts/a25_plate_recipe_runtime.js';s=p.read_text(encoding='utf-8')
 anchor='export function a25PlateRows(stack){return plateRowsFromItem(stack)}\n'
 add='export function a25ReadPlateBlock(block){return readPlateBlock(block)}\n'+anchor
 if s.count(anchor)!=1:raise RuntimeError('A2.7.44 plate export anchor drift')
 if 'a25ReadPlateBlock' in s:raise RuntimeError('A2.7.44 plate reader already exported')
 p.write_text(s.replace(anchor,add,1),encoding='utf-8')

def patch_scripts():
 scripts=BP/'scripts'
 for name in NEW_FILES:shutil.copy2(DEV/name,scripts/name)
 main=scripts/'main.js';s=main.read_text(encoding='utf-8')
 anchor="import './a2743_seasoning_hud_provider.js';\n"
 add=anchor+"import './a2744_skewer_plate_hud_provider.js';\n"
 if s.count(anchor)!=1:raise RuntimeError('A2.7.44 main provider anchor drift')
 if 'a2744_skewer_plate_hud_provider.js' in s:raise RuntimeError('A2.7.44 provider already active')
 main.write_text(s.replace(anchor,add,1),encoding='utf-8')

def patch_lang():
 for name,lines in LANG.items():
  p=RP/'texts'/name;s=p.read_text(encoding='utf-8');rows=s.splitlines()
  for line in lines:
   key=line.split('=',1)[0]
   if any(row.startswith(key+'=') for row in rows):raise RuntimeError(f'{name}: duplicate localization key {key}')
  if s and not s.endswith('\n'):s+='\n'
  p.write_text(s+'\n'.join(lines)+'\n',encoding='utf-8')

def report():
 write(P/'reports/a2744-skewer-plate-hud-provider.json',{
  'version':'A2.7.44',
  'scope':'attach Skewer Plate Java Jade status to shared crosshair HUD using A2.5 plate state',
  'java_contract':{
   'capacity':5,
   'jade':['count','empty','take','pack','item_elements']
  },
  'reuse':{
   'shared_crosshair_runtime':'a2739_crosshair_hud_runtime.js',
   'plate_reader':'a25ReadPlateBlock -> existing readPlateBlock',
   'plate_capacity':'PLATE_CAPACITY',
   'plate_normalizer':'normalizePlateRows',
   'single_poll_loop':True,
   'duplicate_plate_state_parser':False,
   'direct_dynamic_property_access':False
  },
  'ui_boundary':{
   'java_item_icons':True,
   'bedrock_actionbar_item_icons':False,
   'content_signature_tracks_item_ids':True
  },
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,43]:raise RuntimeError('A2.7.44 must augment published A2.7.43')
 patch_plate_runtime();patch_scripts();patch_lang();patch_versions();report()
 print('A2.7.44 Skewer Plate HUD provider complete')

if __name__=='__main__':main()
