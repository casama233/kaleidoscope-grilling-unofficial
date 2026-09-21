from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,39]
NEW_FILES=(
 'a2739_cookery_oil_pot_block_adapter.js',
 'a2739_crosshair_hud_core.js',
 'a2739_crosshair_hud_runtime.js',
 'a2739_oil_pot_hud_provider.js',
)
REFACTORED='a2739_refactored_a2736_typed_oil_pot_block_runtime.js'

LANG={
 'en_US.lang':[
  'hud.kaleidoscope_grilling.oil_pot.title=Oil Pot · Storage',
  'hud.kaleidoscope_grilling.oil_pot.capacity=Capacity %1$s/%2$s · %3$s remaining',
  'tooltip.kaleidoscope_grilling.oil_pot.empty=Any oil: %s points',
  'tooltip.kaleidoscope_grilling.oil_pot.fat=Fat: %s items',
  'tooltip.kaleidoscope_grilling.oil_pot.canola=Canola oil: %s points',
  'tooltip.kaleidoscope_grilling.oil_pot.secret_chili=Chili oil: %s points',
  'tooltip.kaleidoscope_grilling.oil_pot.premium_chili=Magma chili oil: %s points',
 ],
 'zh_CN.lang':[
  'hud.kaleidoscope_grilling.oil_pot.title=油壶 · 储油状态',
  'hud.kaleidoscope_grilling.oil_pot.capacity=容量 %1$s/%2$s · 剩余 %3$s 点',
  'tooltip.kaleidoscope_grilling.oil_pot.empty=任意油：%s 点',
  'tooltip.kaleidoscope_grilling.oil_pot.fat=油脂：%s 个',
  'tooltip.kaleidoscope_grilling.oil_pot.canola=菜籽油：%s 点',
  'tooltip.kaleidoscope_grilling.oil_pot.secret_chili=辣椒油：%s 点',
  'tooltip.kaleidoscope_grilling.oil_pot.premium_chili=熔岩辣椒油：%s 点',
 ],
 'zh_TW.lang':[
  'hud.kaleidoscope_grilling.oil_pot.title=油壺 · 儲油狀態',
  'hud.kaleidoscope_grilling.oil_pot.capacity=容量 %1$s/%2$s · 剩餘 %3$s 點',
  'tooltip.kaleidoscope_grilling.oil_pot.empty=任意油：%s 點',
  'tooltip.kaleidoscope_grilling.oil_pot.fat=油脂：%s 個',
  'tooltip.kaleidoscope_grilling.oil_pot.canola=菜籽油：%s 點',
  'tooltip.kaleidoscope_grilling.oil_pot.secret_chili=辣椒油：%s 點',
  'tooltip.kaleidoscope_grilling.oil_pot.premium_chili=熔岩辣椒油：%s 點',
 ],
}

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.39 Shared Crosshair HUD BP'),(rm,'Kaleidoscope Grilling A2.7.39 Shared Crosshair HUD RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.39 Shared Crosshair HUD'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_39_Shared_Crosshair_HUD'
 write(P/'config.json',cfg)

def patch_scripts():
 scripts=BP/'scripts'
 for name in NEW_FILES:shutil.copy2(DEV/name,scripts/name)
 shutil.copy2(DEV/REFACTORED,scripts/'a2736_typed_oil_pot_block_runtime.js')
 main=scripts/'main.js';s=main.read_text(encoding='utf-8')
 anchor="import './a2737_offhand_oil_fill_runtime.js';\n"
 add=anchor+"import './a2739_crosshair_hud_runtime.js';\nimport './a2739_oil_pot_hud_provider.js';\n"
 if s.count(anchor)!=1:raise RuntimeError('A2.7.39 main import anchor drift')
 if 'a2739_crosshair_hud_runtime.js' in s or 'a2739_oil_pot_hud_provider.js' in s:
  raise RuntimeError('A2.7.39 HUD already active')
 main.write_text(s.replace(anchor,add,1),encoding='utf-8')

def patch_lang():
 for name,lines in LANG.items():
  p=RP/'texts'/name;s=p.read_text(encoding='utf-8')
  for line in lines:
   key=line.split('=',1)[0]
   if any(row.startswith(key+'=') for row in s.splitlines()):
    raise RuntimeError(f'{name}: duplicate localization key {key}')
  if s and not s.endswith('\n'):s+='\n'
  p.write_text(s+'\n'.join(lines)+'\n',encoding='utf-8')

def report():
 write(P/'reports/a2739-shared-crosshair-hud.json',{
  'version':'A2.7.39',
  'scope':'shared crosshair HUD runtime + Cookery oil-pot provider',
  'shared_hud':{
   'poll_ticks':4,'max_distance':6,'provider_registry':True,
   'publishes_only_when_signature_changes':True,
   'actionbar_rawmessage_localized':True,
   'clears_cache_when_target_missing':True,
   'no_per_provider_poll_loop':True
  },
  'oil_pot_provider':{
   'uses_cookery_host_block':True,
   'empty_state':True,'native_fat_state':True,
   'typed_oil_states':['canola','secret_chili','premium_chili'],
   'capacity_and_remaining':True,
   'uses_shared_block_state_adapter':True
  },
  'dedupe':{
   'a2736_world_property_io_moved_to_adapter':True,
   'hud_does_not_read_host_dynamic_properties_directly':True,
   'duplicate_oil_pot_block_created':False
  },
  'api':{
   'minecraft_server':'2.9.0',
   'view_raycast':'Entity.getBlockFromViewDirection',
   'display':'ScreenDisplay.setActionBar'
  },
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,38]:raise RuntimeError('A2.7.39 must augment published A2.7.38')
 patch_scripts();patch_lang();patch_versions();report()
 print('A2.7.39 shared crosshair HUD complete')

if __name__=='__main__':main()
