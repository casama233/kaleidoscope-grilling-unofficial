"""Finite projectile-dodge reservations, movement and original audio adapters."""
from verify_a2884 import main as previous
from pathlib import Path
import subprocess, sys
ROOT=Path(__file__).resolve().parents[2]

def main(expected_version=(2,8,85)):
    previous(expected_version=expected_version)
    subprocess.run(['node','--test','development/gameplay_core/test_projectile_dodge_reservations.mjs','development/gameplay_core/test_projectile_dodge_movement.mjs','development/gameplay_core/test_projectile_dodge_audio.mjs'],cwd=ROOT,check=True)
    subprocess.run([sys.executable,'tools/build_projectile_dodge_audio.py','--check'],cwd=ROOT,check=True)

if __name__=='__main__':
    main()
