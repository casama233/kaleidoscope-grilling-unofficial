"""A2.7.69: localized food lore and typed-oil transaction safety.
Static/source and pure-data verification only; no simulated Minecraft player.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import urllib.request

ROOT=Path(__file__).resolve().parents[2]
PROJECT=ROOT/'projects/grilling/gameplay_core'
BP=PROJECT/'behavior_pack'
RP=PROJECT/'resource_pack'
DEV=Path(__file__).resolve().parent
BASE='09d6b6d596e021326b2cb20299c23f3d3c950d0b'
ITEMS=('sugared_tomato','pepper_honey','houttuynia_stir_fried_pork','green_pepper_squid_tentacles','braised_chicken_wings','potato_beef_stew','red_sweet_potato_porridge','sour_spicy_noodles')
CHANGED={
 'behavior_pack/manifest.json','resource_pack/manifest.json',
 'behavior_pack/scripts/a2734_cookery_oil_pot_adapter.js',
 'behavior_pack/scripts/a2736_typed_oil_pot_block_runtime.js',
 'behavior_pack/scripts/a2739_cookery_oil_pot_block_adapter.js',
 'behavior_pack/scripts/a2750_food_state_adapter.js',
}
ADDED={
 'behavior_pack/scripts/a2769_food_tooltip_core.js',
 'behavior_pack/scripts/a2769_food_tooltip_runtime.js',
}
JAVA_COMMIT='9a1acdab27698457bec16c9362678e574895a28c'
JAVA={
 'food/FoodTooltip.java':('9560c9242a488708ce718a8f7917c56855aed037',('Component.translatable(key)','ChatFormatting.DARK_GRAY, ChatFormatting.ITALIC')),
 'mixin/OilPotBlockMixin.java':('3007b402ae527618652ce5b4e2d20c670f5ea7e4',('access.grilling$setOilType(OilPotCompat.getType(stack))','OilPotCompat.setType(stack, access.grilling$getOilType())')),
}

def load(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def blob(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)

def baseline_guard():
 try:git('cat-file','-e',BASE+'^{commit}')
 except subprocess.CalledProcessError:
  subprocess.run(['git','fetch','--depth=1','origin',BASE],cwd=ROOT,check=True)
 prefix='projects/grilling/gameplay_core/'
 listing=git('ls-tree','-r','-z',BASE,'--',prefix+'behavior_pack',prefix+'resource_pack')
 before={}
 for record in listing.split(b'\0'):
  if not record:continue
  header,path=record.split(b'\t',1)
  mode,kind,sha=header.split()
  assert kind==b'blob'
  before[path.decode()[len(prefix):]]=sha.decode()
 after={p.relative_to(PROJECT).as_posix():p for pack in (BP,RP) for p in pack.rglob('*') if p.is_file()}
 assert set(after)-set(before)==ADDED,('unexpected added runtime files',set(after)-set(before))
 assert not set(before)-set(after),('runtime file removed',set(before)-set(after))
 changed={path for path,sha in before.items() if blob(after[path].read_bytes())!=sha}
 assert changed==CHANGED,('unexpected runtime drift',changed^CHANGED)
 return len(before)-len(changed)

def java_contract():
 base='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/'+JAVA_COMMIT+'/forge-1.20.1/src/main/java/cn/breezeth/kaleidoscope_grilling/'
 for path,(sha,tokens) in JAVA.items():
  request=urllib.request.Request(base+path,headers={'User-Agent':'Grilling-A2768-contract'})
  with urllib.request.urlopen(request,timeout=90) as response:data=response.read()
  assert blob(data)==sha,('Java reference drift',path)
  for token in tokens:assert token in data.decode(),(path,token)

def source_guards():
 for side in (BP,RP):assert load(side/'manifest.json')['header']['version']==[2,7,69]
 for locale in ('en_US','zh_CN','zh_TW'):
  text=(RP/f'texts/{locale}.lang').read_text(encoding='utf-8-sig')
  keys={line.split('=',1)[0] for line in text.splitlines() if '=' in line}
  for item in ITEMS:
   assert 'tooltip.kaleidoscope_grilling.'+item+'.maxim' in keys,(locale,item)
   assert (BP/f'items/{item}.json').is_file(),item
 food=(BP/'scripts/a2750_food_state_adapter.js').read_text()
 runtime=(BP/'scripts/a2769_food_tooltip_runtime.js').read_text()
 core=(BP/'scripts/a2769_food_tooltip_core.js').read_text()
 assert "import './a2769_food_tooltip_runtime.js'" in food
 assert 'applyFoodMaxim(stack)' in food and 'stack.getLore()' not in food
 assert 'stack.getRawLore()' in core and 'setInterval' not in runtime
 for token in ('playerInventoryItemChange.subscribe','playerSpawn.subscribe','source.clone()','c.getItem(slot)'):
  assert token in runtime,token
 oil=(BP/'scripts/a2736_typed_oil_pot_block_runtime.js').read_text()
 for token in ('interactionIntentStillCurrent(player,intent)','placedOilPotSnapshotMatches(block,snapshot)',
               'restorePlacedOilPotSnapshot(block,snapshot)','intent.selectedSlot','handRestored','potRestored'):
  assert token in oil,token
 assert 'intent.slot' not in oil
 assert oil.index('output=buildCookeryOilPot')<oil.index('if(!clearPlacedOilPotState(block))')<oil.index("block.setType('minecraft:air')")
 builder=(BP/'scripts/a2734_cookery_oil_pot_adapter.js').read_text()
 assert builder.index('out.setLore(lore)')<builder.index('out.setDynamicProperty(HOST_COUNT_KEY')
 assert 'if(!result.valid||result.type!==normalizedType||result.count!==normalizedCount)return undefined' in builder
 adapter=(BP/'scripts/a2739_cookery_oil_pot_block_adapter.js').read_text()
 for token in ('rawType:world.getDynamicProperty','rawCount:world.getDynamicProperty','restorePlacedOilPotSnapshot(block,snapshot);return false'):
  assert token in adapter,token
 # A2.7.67 recipe/material repairs remain protected, not discarded when changing the release verifier.
 from verify_a2767 import method,GATES
 maps=0
 for path in (BP/'blocks').glob('*.json'):
  block=load(path)['minecraft:block'];base=block.get('components',{})
  for components in [base,*[dict(base,**r.get('components',{})) for r in block.get('permutations',[])]]:
   for materials in (components.get('minecraft:material_instances'),components.get('minecraft:item_visual',{}).get('material_instances')):
    if materials is not None:
     assert len({method(materials,k) for k in materials})==1,path;maps+=1
 for name,item in GATES.items():
  doc=load(BP/f'recipes/{name}.json');recipe=doc.get('minecraft:recipe_shaped') or doc['minecraft:recipe_shapeless']
  assert recipe['unlock']==[{'item':item}]
 return maps

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--compiled',action='store_true');args=parser.parse_args()
 from verify_a2766 import check_assets
 subprocess.run([sys.executable,str(DEV/'test_vibrant_gate.py')],check=True)
 assets=check_assets();unchanged=baseline_guard();maps=source_guards();java_contract()
 subprocess.run([sys.executable,str(DEV/'a2764_rebake_skewer_hand_geometry.py'),'--check'],check=True)
 subprocess.run([sys.executable,str(DEV/'verify_a2761_java_interaction_contract.py')],check=True)
 for test in ('test_a275_core.mjs','test_a276_core.mjs','test_a277_core.mjs','test_a2762_core.mjs','test_a2769_core.mjs'):
  subprocess.run(['node',str(DEV/test)],check=True)
 for path in (BP/'scripts').rglob('*.js'):subprocess.run(['node','--check',str(path)],check=True)
 report=load(PROJECT/'reports/a2769-food-tooltip-oil-safety.json')
 assert report['version']=='A2.7.69' and report['maxim_items']==list(ITEMS)
 assert not any(report[k] for k in ('minecraft_tested','bds_tested','client_visuals_tested','placed_oil_color_fixed','placed_seasoning_visual_fixed'))
 print(json.dumps({'version':'A2.7.69','unchanged_runtime_files':unchanged,'material_maps_checked':maps,'maxim_items':len(ITEMS),'pure_lore_cases':10,'assets':assets,'compiled_requested':args.compiled,'minecraft_tested':False,'bds_tested':False,'client_visuals_tested':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
