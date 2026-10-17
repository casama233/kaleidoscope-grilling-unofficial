"""Skewer first-person player-bone projection gate; client acceptance is separate."""
import subprocess
import sys
from pathlib import Path
from verify_a2842 import main as baseline

def main():
    baseline()
    subprocess.run([sys.executable,str(Path(__file__).with_name('test_native_skewer_fp.py'))],check=True)
    print('A2.8.43 player-bone skewer projection PASS; Minecraft rendering unaccepted')

if __name__ == '__main__': main()
