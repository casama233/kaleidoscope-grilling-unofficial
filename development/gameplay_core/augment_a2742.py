from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,42]
NEW_FILES=('a2742_big_vat_hud_core.js','a2742_big_vat_hud_provider.js')
LANG={
 'en_US.lang':[
  'hud.kaleidoscope_grilling.vat.title=Vat · Storage',
  'hud.kaleidoscope_grilling.vat.content.empty=Contents: Empty',
  'hud.kaleidoscope_grilling.vat.content.water=Contents: Water',
  'hud.kaleidoscope_grilling.vat.content.lava=Contents: Lava',
  'hud.kaleidoscope_grilling.vat.content.canola=Contents: Canola Oil',
  'hud.kaleidoscope_grilling.vat.content.secret_chili=Contents: Chili Oil',
  'hud.kaleidoscope_grilling.vat.content.premium_chili=Contents: Magma Chili Oil',
  'hud.kaleidoscope_grilling.vat.capacity=Capacity: %1$s/%2$s buckets',
  'hud.kaleidoscope_grilling.vat.accepts=One fluid type only · No mixing',
 ],
 'zh_CN.lang':[
  'hud.kaleidoscope_grilling.vat.title=大缸 · 储存状态',
  'hud.kaleidoscope_grilling.vat.content.empty=内容：空',
  'hud.kaleidoscope_grilling.vat.content.water=内容：水',
  'hud.kaleidoscope_grilling.vat.content.lava=内容：熔岩',
  'hud.kaleidoscope_grilling.vat.content.canola=内容：菜籽油',
  'hud.kaleidoscope_grilling.vat.content.secret_chili=内容：辣椒油',
  'hud.kaleidoscope_grilling.vat.content.premium_chili=内容：熔岩辣椒油',
  'hud.kaleidoscope_grilling.vat.capacity=容量：%1$s/%2$s 桶',
  'hud.kaleidoscope_grilling.vat.accepts=仅可装一种流体 · 不可混装',
 ],
 'zh_TW.lang':[
  'hud.kaleidoscope_grilling.vat.title=大缸 · 儲存狀態',
  'hud.kaleidoscope_grilling.vat.content.empty=內容：空',
  'hud.kaleidoscope_grilling.vat.content.water=內容：水',
  'hud.kaleidoscope_grilling.vat.content.lava=內容：熔岩',
  'hud.kaleidoscope_grilling.vat.content.canola=內容：菜籽油',
  'hud.kaleidoscope_grilling.vat.content.secret_chili=內容：辣椒油',
  'hud.kaleidoscope_grilling.vat.content.premium_chili=內容：熔岩辣椒油',
  'hud.kaleidoscope_grilling.vat.capacity=容量：%1$s/%2$s 桶',
  'hud.kaleidoscope_grilling.vat.accepts=僅可裝一種流體 · 不可混裝',
 ],
}

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.42 Big Vat HUD Provider BP'),(rm,'Kaleidoscope Grilling A2.7.42 Big Vat HUD Provider RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.42 Big Vat HUD Provider'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_42_Big_Vat_HUD_Provider'
 write(P/'config.json',cfg)

def patch_scripts():
 scripts=BP/'scripts'
 for name in NEW_FILES:shutil.copy2(DEV/name,scripts/name)
 main=scripts/'main.js';s=main.read_text(encoding='utf-8')
 anchor="import './a2741_oil_press_hud_provider.js';\n"
 add=anchor+"import './a2742_big_vat_hud_provider.js';\n"
 if s.count(anchor)!=1:raise RuntimeError('A2.7.42 main provider anchor drift')
 if 'a2742_big_vat_hud_provider.js' in s:raise RuntimeError('A2.7.42 Big Vat provider already active')
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
 write(P/'reports/a2742-big-vat-hud-provider.json',{
  'version':'A2.7.42',
  'scope':'attach Big Vat to A2.7.39 shared crosshair HUD using the existing A2.6 vat reader',
  'java_contract':{
   'capacity_buckets':8,
   'machine_hud':['title','content_name','capacity','single_fluid_hint'],
   'backend':'FluidTank / IFluidHandler'
  },
  'reuse':{
   'shared_crosshair_runtime':'a2739_crosshair_hud_runtime.js',
   'vat_state_reader':'a26ReadVat',
   'single_poll_loop':True,
   'duplicate_vat_state_parser':False,
   'direct_dynamic_property_access':False
  },
  'bedrock_fluid_types':['water','lava','canola','secret_chili','premium_chili'],
  'parity_boundary':{
   'java_generic_registered_fluids':True,
   'bedrock_generic_fluid_api':False,
   'reason':'A2.6 VAT_TYPES intentionally implements five concrete fluid types; HUD reflects actual Bedrock support'
  },
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,41]:raise RuntimeError('A2.7.42 must augment published A2.7.41')
 patch_scripts();patch_lang();patch_versions();report()
 print('A2.7.42 Big Vat HUD provider complete')

if __name__=='__main__':main()
