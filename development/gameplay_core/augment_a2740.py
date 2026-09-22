from __future__ import annotations
import json,re,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,40]
NEW_FILES=(
 'a2740_grill_state_adapter.js',
 'a2740_grill_hud_core.js',
 'a2740_grill_hud_provider.js',
)

LANG={
 'en_US.lang':[
  'hud.kaleidoscope_grilling.grill.title=Grill · Cooking Status',
  'hud.kaleidoscope_grilling.grill.timer=Stage time: %1$s/%2$s ticks',
  'hud.kaleidoscope_grilling.grill.flips=Flips: %1$s/%2$s',
  'hud.kaleidoscope_grilling.grill.seasoning.added=Seasoned · Ready to take out',
  'hud.kaleidoscope_grilling.grill.seasoning.none=Not seasoned · Normal takeout locked',
  'message.kaleidoscope_grilling.grill_ready_to_take=Cooking complete; ready to take out!',
  'jade.kaleidoscope_grilling.grill.need_heat=Waiting for the grill charcoal to be lit',
  'jade.kaleidoscope_grilling.grill.empty=Waiting for skewers',
  'jade.kaleidoscope_grilling.grill.need_oil=Waiting to be brushed with oil',
  'jade.kaleidoscope_grilling.grill.flipping=Flipping... (%1$s/%2$s)',
  'jade.kaleidoscope_grilling.grill.need_flip=Waiting to flip (%1$s/%2$s)',
  'jade.kaleidoscope_grilling.grill.need_seasoning=Cooking complete; waiting for seasoning',
  'jade.kaleidoscope_grilling.grill.ready=Cooking complete; ready to take out',
  'jade.kaleidoscope_grilling.grill.burning=The food is burning; act quickly',
 ],
 'zh_CN.lang':[
  'hud.kaleidoscope_grilling.grill.title=烧烤架 · 烹饪状态',
  'hud.kaleidoscope_grilling.grill.timer=阶段时间：%1$s/%2$s tick',
  'hud.kaleidoscope_grilling.grill.flips=翻面：%1$s/%2$s',
  'hud.kaleidoscope_grilling.grill.seasoning.added=已撒调料 · 可以取出',
  'hud.kaleidoscope_grilling.grill.seasoning.none=未撒调料 · 暂不可正常取出',
  'message.kaleidoscope_grilling.grill_ready_to_take=烹饪已完成，等待取出！',
  'jade.kaleidoscope_grilling.grill.need_heat=待点燃烧烤架的炭火',
  'jade.kaleidoscope_grilling.grill.empty=等待放入烤串',
  'jade.kaleidoscope_grilling.grill.need_oil=等待刷油',
  'jade.kaleidoscope_grilling.grill.flipping=翻面中...（%1$s/%2$s）',
  'jade.kaleidoscope_grilling.grill.need_flip=等待翻面（%1$s/%2$s）',
  'jade.kaleidoscope_grilling.grill.need_seasoning=烹饪已完成，等待撒料',
  'jade.kaleidoscope_grilling.grill.ready=烹饪已完成，可以取出',
  'jade.kaleidoscope_grilling.grill.burning=烧烤正在焦化，请尽快处理',
 ],
 'zh_TW.lang':[
  'hud.kaleidoscope_grilling.grill.title=燒烤架 · 烹飪狀態',
  'hud.kaleidoscope_grilling.grill.timer=階段時間：%1$s/%2$s tick',
  'hud.kaleidoscope_grilling.grill.flips=翻面：%1$s/%2$s',
  'hud.kaleidoscope_grilling.grill.seasoning.added=已撒調料 · 可以取出',
  'hud.kaleidoscope_grilling.grill.seasoning.none=未撒調料 · 暫不可正常取出',
  'message.kaleidoscope_grilling.grill_ready_to_take=烹飪已完成，等待取出！',
  'jade.kaleidoscope_grilling.grill.need_heat=待點燃燒烤架的炭火',
  'jade.kaleidoscope_grilling.grill.empty=等待放入烤串',
  'jade.kaleidoscope_grilling.grill.need_oil=等待刷油',
  'jade.kaleidoscope_grilling.grill.flipping=翻面中...（%1$s/%2$s）',
  'jade.kaleidoscope_grilling.grill.need_flip=等待翻面（%1$s/%2$s）',
  'jade.kaleidoscope_grilling.grill.need_seasoning=烹飪已完成，等待撒料',
  'jade.kaleidoscope_grilling.grill.ready=烹飪已完成，可以取出',
  'jade.kaleidoscope_grilling.grill.burning=燒烤正在焦化，請儘快處理',
 ],
}

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.40 Grill HUD Provider BP'),(rm,'Kaleidoscope Grilling A2.7.40 Grill HUD Provider RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.40 Grill HUD Provider'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_40_Grill_HUD_Provider'
 write(P/'config.json',cfg)

def patch_core_logic():
 p=BP/'scripts/core_logic.js';s=p.read_text(encoding='utf-8')
 anchor='export const FLIP_COOLDOWN=20;\n'
 if s.count(anchor)!=1:raise RuntimeError('core flip constant anchor drift')
 if 'REQUIRED_FLIPS' in s:raise RuntimeError('REQUIRED_FLIPS already present')
 s=s.replace(anchor,anchor+'export const REQUIRED_FLIPS=4;\n',1)
 if s.count('s.flips<=4')!=1:raise RuntimeError('validState flips upper bound drift')
 s=s.replace('s.flips<=4','s.flips<=REQUIRED_FLIPS',1)
 if s.count('phase:flips>=4?2:1')!=1:raise RuntimeError('flip phase threshold drift')
 s=s.replace('phase:flips>=4?2:1','phase:flips>=REQUIRED_FLIPS?2:1',1)
 p.write_text(s,encoding='utf-8')

def patch_main():
 p=BP/'scripts/main.js';s=p.read_text(encoding='utf-8')
 core_anchor="import {initialState,normalizeState,tickState,light,brush,flip,season,canInsert,canExtract,breakDisposition,outputKind} from './core_logic.js';\n"
 state_import="import {grillStateKey as stateKey,readGrillState as readState,occupiedGrillSlots as occupied} from './a2740_grill_state_adapter.js';\n"
 if s.count(core_anchor)!=1:raise RuntimeError('main core import drift')
 if state_import in s:raise RuntimeError('grill state adapter already imported')
 s=s.replace(core_anchor,core_anchor+state_import,1)

 patterns=(
  (r"function stateKey\(block\)\{[^\n]*\}\n",'stateKey'),
  (r"function occupied\(block\)\{[^\n]*\}\n",'occupied'),
  (r"function readState\(block\)\{\n.*?\n\}\n",'readState'),
 )
 for pattern,label in patterns:
  s,n=re.subn(pattern,'',s,count=1,flags=re.S if label=='readState' else 0)
  if n!=1:raise RuntimeError(f'main {label} helper drift: {n}')

 hud_anchor="import './a2739_oil_pot_hud_provider.js';\n"
 add=hud_anchor+"import './a2740_grill_hud_provider.js';\n"
 if s.count(hud_anchor)!=1:raise RuntimeError('main HUD provider anchor drift')
 if 'a2740_grill_hud_provider.js' in s:raise RuntimeError('grill HUD provider already active')
 s=s.replace(hud_anchor,add,1)
 p.write_text(s,encoding='utf-8')

def patch_lang():
 for name,lines in LANG.items():
  p=RP/'texts'/name;s=p.read_text(encoding='utf-8')
  rows=s.splitlines()
  for line in lines:
   key=line.split('=',1)[0]
   if any(row.startswith(key+'=') for row in rows):
    raise RuntimeError(f'{name}: duplicate localization key {key}')
  if s and not s.endswith('\n'):s+='\n'
  p.write_text(s+'\n'.join(lines)+'\n',encoding='utf-8')

def report():
 write(P/'reports/a2740-grill-hud-provider.json',{
  'version':'A2.7.40',
  'scope':'attach Grill to A2.7.39 shared crosshair HUD without another poll loop',
  'java_contract':{
   'finished_ticks':800,'burnt_ticks':400,'required_flips':4,'flip_cooldown':20,
   'machine_hud':['title','timer','flips','seasoning','ready_to_take'],
   'jade_states':['need_heat','empty','need_oil','flipping','need_flip','need_seasoning','ready','burning']
  },
  'reuse':{
   'shared_crosshair_runtime':'a2739_crosshair_hud_runtime.js',
   'single_poll_loop':True,
   'shared_grill_state_adapter':'a2740_grill_state_adapter.js',
   'main_uses_shared_read_state':True,
   'main_uses_shared_state_key':True,
   'main_uses_shared_occupied_slots':True,
   'duplicate_state_machine':False
  },
  'bedrock_adaptation':{
   'timer_sample_ticks':20,
   'reason':'actionbar should not overwrite interaction feedback every 4 ticks',
   'state_flip_and_seasoning_changes_immediate':True
  },
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,39]:raise RuntimeError('A2.7.40 must augment published A2.7.39')
 patch_core_logic()
 for name in NEW_FILES:shutil.copy2(DEV/name,BP/'scripts'/name)
 patch_main();patch_lang();patch_versions();report()
 print('A2.7.40 Grill HUD provider complete')

if __name__=='__main__':main()
