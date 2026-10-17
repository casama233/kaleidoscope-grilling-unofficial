"""Sampled-candidate whole-body liquid admission and Hinder LivingEntity gates."""
from verify_a2885 import main as previous
from pathlib import Path
import subprocess, sys
ROOT=Path(__file__).resolve().parents[2]

def main(expected_version=(2,8,86)):
    previous(expected_version=expected_version)
    subprocess.run(['node','--test','development/gameplay_core/test_projectile_dodge_liquid.mjs'],cwd=ROOT,check=True)
    subprocess.run([sys.executable,'tools/build_projectile_dodge_liquid_catalog.py','--check'],cwd=ROOT,check=True)

if __name__=='__main__':
    main()
