"""Source-backed rack visual selection; native FIXED projection remains separate."""
from pathlib import Path
import subprocess
from verify_a2854 import main as previous

def main():
    previous()
    subprocess.run(['node','--test','development/gameplay_core/test_rack_visual_selection.mjs'],cwd=Path(__file__).resolve().parents[2],check=True)
    print('A2.8.55 rack hook selection PASS; native FIXED projection remains unaccepted')

if __name__=='__main__':main()
