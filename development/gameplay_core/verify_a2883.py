"""Plate-only full-skewer projection; no native/global acceptance claim."""
from pathlib import Path
import subprocess,sys
from verify_a2879 import main as previous
ROOT=Path(__file__).resolve().parents[2]
def main(expected_version=(2,8,83)):
 previous(expected_version=expected_version)
 subprocess.run(['node','--test','development/gameplay_core/test_oil_snapshot_intent.mjs','development/gameplay_core/test_cookery_damage_feedback.mjs'],cwd=ROOT,check=True)
 subprocess.run([sys.executable,'tools/build_cookery_effect_feedback.py','--check'],cwd=ROOT,check=True)
 subprocess.run([sys.executable,'tools/build_plate_food_display.py','--check'],cwd=ROOT,check=True)
 subprocess.run(['node','--test','development/gameplay_core/test_plate_qa_core.mjs'],cwd=ROOT,check=True)
 subprocess.run([sys.executable,'-m','unittest','discover','-s','tools','-p','test_plate_qa_source_witness.py'],cwd=ROOT,check=True)
 subprocess.run(['node','--test','development/gameplay_core/test_plate_visual.mjs','development/gameplay_core/test_plate_transactions.mjs','development/gameplay_core/test_rack_tool_runtime.mjs'],cwd=ROOT,check=True)
if __name__=='__main__':main()
