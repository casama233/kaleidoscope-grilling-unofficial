"""PBR declaration hotfix; retain every A2.7.67 gameplay/schema/asset gate."""
from pathlib import Path
import subprocess
import sys
from vibrant_gate import check_paths
from verify_a2767 import main as verify_schema_release

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1] / 'projects/grilling/gameplay_core'
if __name__ == '__main__':
    check_paths(PROJECT/'behavior_pack', PROJECT/'resource_pack')
    subprocess.run([sys.executable,str(HERE/'test_vibrant_gate.py')], check=True)
    verify_schema_release(expected_version=(2, 7, 68))
