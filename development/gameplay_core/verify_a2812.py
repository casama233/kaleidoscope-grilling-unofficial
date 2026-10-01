"""Integrated PR #78–85 gate; retain stable baseline checks and add each feature's regressions."""
from pathlib import Path
import subprocess,sys
from verify_a2811 import main as baseline
from verify_a287 import secret_compat_gate,parity_batch2_gate,parity_batch3_gate
ROOT=Path(__file__).resolve().parents[2]
def main():
 baseline();secret_compat_gate();parity_batch2_gate();parity_batch3_gate()
 for args in [
  ['node','--experimental-vm-modules','development/gameplay_core/test_a288_parity.mjs'],
  ['node','projects/grilling/gameplay_core/review/pure_checks.mjs'],
  ['node','tools/check_family_knives.mjs'],
 ['node','development/gameplay_core/test_java_survival_parity.mjs'],
 ['node','development/gameplay_core/test_dragon_powder_transaction.mjs'],
  [sys.executable,'tools/test_guide_icon_regression.py'],
  [sys.executable,'development/gameplay_core/test_skewer_hand_anchor.py'],
  [sys.executable,'tools/check_grilling_guide.py'],
  [sys.executable,'tools/check_station_storage.py'],
 ]:subprocess.run(args,cwd=ROOT,check=True)
 print('A2.8.12 all-PR source integration regressions PASS; native/client/restart results remain separate')
if __name__=='__main__':main()
