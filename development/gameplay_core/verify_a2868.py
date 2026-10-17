"""Integrated helper/terminal source gate; native acceptance remains bounded."""
from pathlib import Path
import subprocess,sys
from verify_a2867 import main as previous
ROOT=Path(__file__).resolve().parents[2]
VERSION=(2,8,68)
def main(expected_version=VERSION):
 previous(expected_version=expected_version)
 for name in ('test_g68_binding_admission.py','test_generated_food_sprite.py','test_generated_food_sprite_alignment.py','test_partial_skewer_held.py','test_secret_active_calibration.py','test_secret_completion_scope.py','test_secret_geometry_roundtrip.py','test_secret_helper_projection.py','test_secret_idle_calibration.py','test_secret_slot_order.py','test_secret_terminal_visibility.py'):
  subprocess.run([sys.executable,str(ROOT/'development/gameplay_core'/name)],cwd=ROOT,check=True)
 for name in ('test_audit_grilling_render.py','test_secret_food_palette.py'):
  subprocess.run([sys.executable,str(ROOT/'tools'/name)],cwd=ROOT,check=True)
 subprocess.run(['node','--test',*[str(ROOT/'development/gameplay_core'/name)for name in ('test_core_skewer_cycle.mjs','test_full_skewer_flow.mjs','test_secret_helper_runtime.mjs','test_secret_visual_state.mjs')]],cwd=ROOT,check=True)
 print('A'+'.'.join(map(str,expected_version))+' helper/terminal source regressions PASS; no new native/global acceptance claimed')
if __name__=='__main__':main()
