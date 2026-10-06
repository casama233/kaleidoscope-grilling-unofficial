"""Rack visual selection and owner-requested fixed cells; client QA is separate."""
from pathlib import Path
import subprocess
from verify_a2854 import main as previous

def main():
    previous()
    subprocess.run(['node','--test','development/gameplay_core/test_rack_visual_selection.mjs','development/gameplay_core/test_rack_geometry.mjs'],cwd=Path(__file__).resolve().parents[2],check=True)
    print('Rack fixed-cell selection/resources PASS; owner adaptation, native/client acceptance separate')

if __name__=='__main__':main()
