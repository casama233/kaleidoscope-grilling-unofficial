from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
SOURCE_RP=ROOT/'projects/grilling/resource_pack'
VERSION=[2,7,46]
NEW_SCRIPTS=('a2746_advanced_rack_core.js','a2746_advanced_rack_runtime.js')
GEOS=tuple(f'advanced_rack_{i}.geo.json' for i in range(5))
LANG={
 'en_US.lang':[
  'tile.kaleidoscope_grilling:advanced_rack.name=Advanced Kitchen Rack',
  'container.kaleidoscope_grilling.advanced_rack=Advanced Food Rack',
  'container.kaleidoscope_grilling.advanced_rack_shortcut=Select Compartment',
  'tooltip.kaleidoscope_grilling.advanced_rack.saved_contents=Stored contents:',
 ],
 'zh_CN.lang':[
  'tile.kaleidoscope_grilling:advanced_rack.name=高级厨具架',
  'container.kaleidoscope_grilling.advanced_rack=高级厨具架',
  'container.kaleidoscope_grilling.advanced_rack_shortcut=选择分类仓',
  'tooltip.kaleidoscope_grilling.advanced_rack.saved_contents=已保存内容：',
 ],
 'zh_TW.lang':[
  'tile.kaleidoscope_grilling:advanced_rack.name=高級廚具架',
  'container.kaleidoscope_grilling.advanced_rack=高級廚具架',
  'container.kaleidoscope_grilling.advanced_rack_shortcut=選擇分類倉',
  'tooltip.kaleidoscope_grilling.advanced_rack.saved_contents=已保存內容：',
 ],
}

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.46 Advanced Rack Foundation BP'),(rm,'Kaleidoscope Grilling A2.7.46 Advanced Rack Foundation RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.46 Advanced Rack Foundation'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_46_Advanced_Rack_Foundation'
 write(P/'config.json',cfg)

def patch_scripts():
 scripts=BP/'scripts'
 for name in NEW_SCRIPTS:shutil.copy2(DEV/name,scripts/name)
 main=scripts/'main.js';s=main.read_text(encoding='utf-8')
 anchor="import './a2745_skewer_recipe_hud_provider.js';\n"
 add=anchor+"import './a2746_advanced_rack_runtime.js';\n"
 if s.count(anchor)!=1:raise RuntimeError('A2.7.46 main import anchor drift')
 if 'a2746_advanced_rack_runtime.js' in s:raise RuntimeError('A2.7.46 runtime already active')
 main.write_text(s.replace(anchor,add,1),encoding='utf-8')

def patch_block_assets():
 shutil.copy2(DEV/'a2746_advanced_rack.block.json',BP/'blocks/advanced_rack.json')
 target=RP/'models/blocks';target.mkdir(parents=True,exist_ok=True)
 for name in GEOS:shutil.copy2(SOURCE_RP/'models/entity/kg_a1'/name,target/name)
 tex=RP/'textures/blocks/advanced_rack.png';tex.parent.mkdir(parents=True,exist_ok=True)
 shutil.copy2(SOURCE_RP/'textures/kg_a1/advanced_rack.png',tex)
 terrain=load(RP/'textures/terrain_texture.json')
 data=terrain.setdefault('texture_data',{})
 if 'kg_a2746_advanced_rack' in data:raise RuntimeError('advanced rack terrain alias already exists')
 data['kg_a2746_advanced_rack']={'textures':'textures/blocks/advanced_rack'}
 write(RP/'textures/terrain_texture.json',terrain)

def patch_lang():
 for name,lines in LANG.items():
  p=RP/'texts'/name;s=p.read_text(encoding='utf-8');rows=s.splitlines()
  for line in lines:
   key=line.split('=',1)[0]
   if any(row.startswith(key+'=') for row in rows):raise RuntimeError(f'{name}: duplicate localization key {key}')
  if s and not s.endswith('\n'):s+='\n'
  p.write_text(s+'\n'.join(lines)+'\n',encoding='utf-8')

def report():
 write(P/'reports/a2746-advanced-rack-foundation.json',{
  'version':'A2.7.46',
  'scope':'Advanced Rack native 9-slot container, Java compartment/filter core, and reused converted visuals',
  'java_contract':{
   'compartments':9,'seasoning_slots':5,'tool_slots':4,'spice_level_max':4,
   'auto_filter_on_first_insert':True,'clear_filter_only_when_empty':True
  },
  'reuse':{
   'native_block_container':True,
   'cookery_oil_ids':'a2734_cookery_oil_pot_core',
   'seasoning_ids':'a2743_seasoning_contract_core + data.js',
   'cookery_tool_tags':['kaleidoscope_cookery:kitchen_knife','kaleidoscope_cookery:kitchen_shovel'],
   'preconverted_geometry':'projects/grilling/resource_pack/models/entity/kg_a1/advanced_rack_0..4.geo.json',
   'preconverted_texture':'projects/grilling/resource_pack/textures/kg_a1/advanced_rack.png',
   'duplicate_item_whitelist':False
  },
  'deferred':['menu_screen','shortcut_gui','hotbar_binding','deposit_matching','automation_borrow_return','packed_break_drop','survival_recipe'],
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,45]:raise RuntimeError('A2.7.46 must augment published A2.7.45')
 patch_scripts();patch_block_assets();patch_lang();patch_versions();report()
 print('A2.7.46 Advanced Rack foundation complete')

if __name__=='__main__':main()
