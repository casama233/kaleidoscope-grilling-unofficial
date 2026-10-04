"""Public oil/food APIs, native contents and source-backed eating/health regressions."""
from pathlib import Path
import json,subprocess,sys
from verify_a2836 import main as baseline
ROOT=Path(__file__).resolve().parents[2]
def main():
 baseline()
 subprocess.run(['node','--test','development/gameplay_core/test_oil_api.mjs','development/gameplay_core/test_family_oil_food_api.mjs','development/gameplay_core/test_world_oil_transfers.mjs','development/gameplay_core/test_dragon_health.mjs'],cwd=ROOT,check=True)
 subprocess.run([sys.executable,'tools/build_eating_motion.py','--check'],cwd=ROOT,check=True)
 spec=json.loads((ROOT/'projects/grilling/gameplay_core/behavior_pack/host-extensions/board-api.json').read_text())
 assert spec['version']==([0,2,4] if tuple(json.loads((ROOT/'baseline.json').read_text())['version'])>=(2,8,67) else [0,2,3] if tuple(json.loads((ROOT/'baseline.json').read_text())['version'])>=(2,8,41) else [0,2,2] if tuple(json.loads((ROOT/'baseline.json').read_text())['version'])>=(2,8,40) else [0,2,1] if tuple(json.loads((ROOT/'baseline.json').read_text())['version'])>=(2,8,38) else [0,2,0]) and len(spec['original_files'])==8 and len(spec['copies'])==8
 assert set(spec['original_files'])==set(spec['patched_files'])
 assert all('/manifest.json' not in path for path in spec['original_files'])
 assert len(spec['json_updates'])==2
 for op in spec['json_updates']:
  assert op['pointer']==['minecraft:item','components','minecraft:allow_off_hand'] and op['value'] is True
 assert any('handleSharedStationOil' in op['text'] for op in spec['insertions'])
 assert any('beginCuisineCarrier' in op['text'] for op in spec['insertions'])
 print('A2.8.37 public oil/food/guide APIs and fault recovery PASS; native/client evidence remains separate')
if __name__=='__main__':main()
