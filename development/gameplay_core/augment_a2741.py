from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,41]
NEW_FILES=(
 'a2741_oil_press_hud_core.js',
 'a2741_oil_press_hud_provider.js',
)
LANG={
 'en_US.lang':[
  'hud.kaleidoscope_grilling.press.title=Oil Press · Status',
  'hud.kaleidoscope_grilling.press.cakes=Oil cakes: %1$s/%2$s',
  'hud.kaleidoscope_grilling.press.progress=Progress: %1$s/%2$s',
  'hud.kaleidoscope_grilling.press.vat.none=No nearby vat can accept canola oil',
  'hud.kaleidoscope_grilling.press.vat.found=Collection vat: %1$s/%2$s buckets',
  'hud.kaleidoscope_grilling.press.vat.wrong=Nearby vat contains an incompatible fluid',
  'hud.kaleidoscope_grilling.press.vat.full=Nearby vat lacks capacity: %1$s/%2$s buckets',
 ],
 'zh_CN.lang':[
  'hud.kaleidoscope_grilling.press.title=榨油器 · 压榨状态',
  'hud.kaleidoscope_grilling.press.cakes=油饼：%1$s/%2$s',
  'hud.kaleidoscope_grilling.press.progress=压榨进度：%1$s/%2$s',
  'hud.kaleidoscope_grilling.press.vat.none=附近没有可接收菜籽油的大缸',
  'hud.kaleidoscope_grilling.press.vat.found=集油大缸：%1$s/%2$s 桶',
  'hud.kaleidoscope_grilling.press.vat.wrong=附近大缸内容不符：仅可接收菜籽油',
  'hud.kaleidoscope_grilling.press.vat.full=附近大缸容量不足：%1$s/%2$s 桶',
 ],
 'zh_TW.lang':[
  'hud.kaleidoscope_grilling.press.title=榨油器 · 壓榨狀態',
  'hud.kaleidoscope_grilling.press.cakes=油餅：%1$s/%2$s',
  'hud.kaleidoscope_grilling.press.progress=壓榨進度：%1$s/%2$s',
  'hud.kaleidoscope_grilling.press.vat.none=附近沒有可接收菜籽油的大缸',
  'hud.kaleidoscope_grilling.press.vat.found=集油大缸：%1$s/%2$s 桶',
  'hud.kaleidoscope_grilling.press.vat.wrong=附近大缸內容不符：僅可接收菜籽油',
  'hud.kaleidoscope_grilling.press.vat.full=附近大缸容量不足：%1$s/%2$s 桶',
 ],
}

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.41 Oil Press HUD Provider BP'),(rm,'Kaleidoscope Grilling A2.7.41 Oil Press HUD Provider RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.41 Oil Press HUD Provider'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_41_Oil_Press_HUD_Provider'
 write(P/'config.json',cfg)

def patch_oil_runtime():
 p=BP/'scripts/a26_oil_machine_runtime.js';s=p.read_text(encoding='utf-8')
 anchor='export function a26ReadPress(block){return readPress(block)}\n'
 add=anchor+'export function a26ProbePressContainer(block){return scanVat(block)}\n'
 if s.count(anchor)!=1:raise RuntimeError('A2.7.41 a26ReadPress export anchor drift')
 if 'a26ProbePressContainer' in s:raise RuntimeError('A2.7.41 press container probe already exported')
 s=s.replace(anchor,add,1)
 p.write_text(s,encoding='utf-8')

def patch_scripts():
 scripts=BP/'scripts'
 for name in NEW_FILES:shutil.copy2(DEV/name,scripts/name)
 main=scripts/'main.js';s=main.read_text(encoding='utf-8')
 anchor="import './a2740_grill_hud_provider.js';\n"
 add=anchor+"import './a2741_oil_press_hud_provider.js';\n"
 if s.count(anchor)!=1:raise RuntimeError('A2.7.41 main provider anchor drift')
 if 'a2741_oil_press_hud_provider.js' in s:raise RuntimeError('A2.7.41 Oil Press provider already active')
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
 write(P/'reports/a2741-oil-press-hud-provider.json',{
  'version':'A2.7.41',
  'scope':'attach Oil Press to the shared crosshair HUD using existing A2.6 press/vat state and scan logic',
  'java_contract':{
   'max_cakes':4,'required_progress':16,'vat_capacity_buckets':8,
   'hud':['cakes','progress','vat_none','vat_incompatible','vat_full','vat_ready']
  },
  'reuse':{
   'shared_crosshair_runtime':'a2739_crosshair_hud_runtime.js',
   'press_state_reader':'a26ReadPress',
   'vat_state_reader':'a26ReadVat',
   'container_probe':'a26ProbePressContainer -> existing scanVat',
   'single_poll_loop':True,'duplicate_nearby_scan':False,'duplicate_press_state_parser':False
  },
  'parity_boundary':{
   'big_vat':True,
   'generic_fluid_handler':False,
   'create_tank':False,
   'reason':'Bedrock A2.6 currently implements Big Vat as the press output host; do not invent a second fake fluid API in HUD'
  },
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,40]:raise RuntimeError('A2.7.41 must augment published A2.7.40')
 patch_oil_runtime();patch_scripts();patch_lang();patch_versions();report()
 print('A2.7.41 Oil Press HUD provider complete')

if __name__=='__main__':main()
