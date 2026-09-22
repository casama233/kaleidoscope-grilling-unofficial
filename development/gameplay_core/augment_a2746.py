from __future__ import annotations
import json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
SRC=ROOT/'projects/grilling/resource_pack'
VERSION=[2,7,45]
SCRIPTS=(
 'a2746_advanced_rack_core.js','a2746_rack_item_codec.js','a2746_rack_state_adapter.js',
 'a2746_rack_automation_api.js','a2746_advanced_rack_runtime.js'
)
LANG={
'en_US.lang':[
 'tile.kaleidoscope_grilling:advanced_rack.name=Advanced Kitchen Rack',
 'item.kaleidoscope_grilling:advanced_rack.name=Advanced Kitchen Rack',
 'container.kaleidoscope_grilling.advanced_rack=Advanced Kitchen Rack',
 'container.kaleidoscope_grilling.advanced_rack_shortcut=Advanced Rack Shortcut',
 'tooltip.kaleidoscope_grilling.advanced_rack.saved_contents=Saved contents:',
 'ui.kaleidoscope_grilling.advanced_rack.hint=5 seasoning compartments + 4 tool compartments. Empty slots keep their filter.',
 'ui.kaleidoscope_grilling.advanced_rack.deposit=Deposit all matching items',
 'message.kaleidoscope_grilling.rack_swap_failed=Rack swap failed',
 'message.kaleidoscope_grilling.rack_nothing_to_deposit=Nothing matches the rack filters',
 'message.kaleidoscope_grilling.rack_not_found=No Advanced Rack found within 8 blocks'
],
'zh_CN.lang':[
 'tile.kaleidoscope_grilling:advanced_rack.name=高级厨具架',
 'item.kaleidoscope_grilling:advanced_rack.name=高级厨具架',
 'container.kaleidoscope_grilling.advanced_rack=高级厨具架',
 'container.kaleidoscope_grilling.advanced_rack_shortcut=高级厨具架快捷界面',
 'tooltip.kaleidoscope_grilling.advanced_rack.saved_contents=已保存内容：',
 'ui.kaleidoscope_grilling.advanced_rack.hint=前5格为调料，后4格为工具；空槽会保留筛选。',
 'ui.kaleidoscope_grilling.advanced_rack.deposit=存入全部符合筛选的物品',
 'message.kaleidoscope_grilling.rack_swap_failed=厨具架交换失败',
 'message.kaleidoscope_grilling.rack_nothing_to_deposit=没有符合现有筛选的物品',
 'message.kaleidoscope_grilling.rack_not_found=8格内找不到高级厨具架'
],
'zh_TW.lang':[
 'tile.kaleidoscope_grilling:advanced_rack.name=高級廚具架',
 'item.kaleidoscope_grilling:advanced_rack.name=高級廚具架',
 'container.kaleidoscope_grilling.advanced_rack=高級廚具架',
 'container.kaleidoscope_grilling.advanced_rack_shortcut=高級廚具架快捷介面',
 'tooltip.kaleidoscope_grilling.advanced_rack.saved_contents=已保存內容：',
 'ui.kaleidoscope_grilling.advanced_rack.hint=前5格為調料，後4格為工具；空槽會保留篩選。',
 'ui.kaleidoscope_grilling.advanced_rack.deposit=存入全部符合篩選的物品',
 'message.kaleidoscope_grilling.rack_swap_failed=廚具架交換失敗',
 'message.kaleidoscope_grilling.rack_nothing_to_deposit=沒有符合現有篩選的物品',
 'message.kaleidoscope_grilling.rack_not_found=8格內找不到高級廚具架'
]}

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.46 Advanced Rack BP'),(rm,'Kaleidoscope Grilling A2.7.46 Advanced Rack RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 if not any(d.get('module_name')=='@minecraft/server-ui' for d in bm.get('dependencies',[])):
  bm.setdefault('dependencies',[]).append({'module_name':'@minecraft/server-ui','version':'2.2.0'})
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.46 Advanced Rack'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_45_Advanced_Rack';write(P/'config.json',cfg)

def patch_scripts():
 for name in SCRIPTS:shutil.copy2(DEV/name,BP/'scripts'/name)
 main=BP/'scripts/main.js';s=main.read_text(encoding='utf-8')
 anchor="import './a2744_skewer_plate_hud_provider.js';\n"
 if s.count(anchor)!=1:raise RuntimeError('A2.7.46 main import anchor drift')
 if 'a2746_advanced_rack_runtime.js' in s:raise RuntimeError('rack runtime already active')
 main.write_text(s.replace(anchor,anchor+"import './a2746_advanced_rack_runtime.js';\n",1),encoding='utf-8')

def patch_content():
 shutil.copy2(DEV/'a2746_advanced_rack_block.json',BP/'blocks/advanced_rack_block.json')
 shutil.copy2(DEV/'a2746_advanced_rack_item.json',BP/'items/advanced_rack.json')
 shutil.copy2(DEV/'a2746_advanced_rack_recipe.json',BP/'recipes/advanced_rack.json')
 model_dst=RP/'models/blocks';model_dst.mkdir(parents=True,exist_ok=True)
 for i in range(5):shutil.copy2(SRC/f'models/entity/kg_a1/advanced_rack_{i}.geo.json',model_dst/f'advanced_rack_{i}.geo.json')
 tex_dst=RP/'textures/blocks';tex_dst.mkdir(parents=True,exist_ok=True)
 shutil.copy2(SRC/'textures/kg_a1/advanced_rack.png',tex_dst/'advanced_rack.png')
 terrain=load(RP/'textures/terrain_texture.json');terrain['texture_data']['kg_a2746_advanced_rack']={'textures':'textures/blocks/advanced_rack'};write(RP/'textures/terrain_texture.json',terrain)
 item=load(RP/'textures/item_texture.json');item['texture_data']['advanced_rack']={'textures':'textures/blocks/advanced_rack'};write(RP/'textures/item_texture.json',item)

def patch_lang():
 for name,lines in LANG.items():
  p=RP/'texts'/name;s=p.read_text(encoding='utf-8');rows=s.splitlines()
  for line in lines:
   key=line.split('=',1)[0]
   if any(row.startswith(key+'=') for row in rows):raise RuntimeError(f'{name}: duplicate {key}')
  if s and not s.endswith('\n'):s+='\n'
  p.write_text(s+'\n'.join(lines)+'\n',encoding='utf-8')

def report():
 write(P/'reports/a2746-advanced-rack.json',{
  'version':'A2.7.46','scope':'Java Advanced Rack gameplay',
  'java':{'compartments':9,'seasoning_slots':5,'tool_slots':4,'shortcut_range':8,'spice_levels':5,
   'persistent_filters':True,'deposit_matching':True,'hotbar_binding':True,'break_preserves_contents':True,'automation_api':True},
  'bedrock':{'block_container_slots':9,'action_form_ui':True,'custom_command':'kaleidoscope_grilling:rack',
   'itemstack_codec_scope':'rack-legal-items-only','server_ui':'2.2.0','models_reused':True},
  'storage_item_rejected':{'reason':'stable Storage Item weight limit is capped at 64 and cannot represent nine arbitrary non-stackable tools'},
  'parity_boundary':{'java_keybinding_caps_lock':True,'bedrock_custom_keyboard_mapping':False,'replacement':'/kaleidoscope_grilling:rack'},
  'minecraft_tested':False,'bds_tested':False})

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,45]:raise RuntimeError('A2.7.46 must augment published A2.7.44')
 patch_scripts();patch_content();patch_lang();patch_versions();report();print('A2.7.46 Advanced Rack complete')
if __name__=='__main__':main()
