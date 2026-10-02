"""Review the canonical additive chopping-board API extension."""
from pathlib import Path
import json,subprocess
from verify_a2830 import main as baseline
ROOT=Path(__file__).resolve().parents[2]
def main():
 baseline()
 subprocess.run(['node','--test','development/gameplay_core/test_board_api.mjs'],cwd=ROOT,check=True)
 spec=json.loads((ROOT/'projects/grilling/gameplay_core/behavior_pack/host-extensions/board-api.json').read_text())
 current=json.loads((ROOT/'baseline.json').read_text())['version']
 if tuple(current)>=(2,8,37):
  assert spec['version']==[0,2,0] and len(spec['original_files'])==8 and len(spec['copies'])==8
 else:
  assert spec['version']==[0,1,0] and len(spec['original_files'])==2 and len(spec['copies'])==2
 assert all('/manifest.json' not in p for p in spec['patched_files'])
 print('A2.8.31 pinned host API, additive outputs and transaction regressions PASS')
if __name__=='__main__':main()
