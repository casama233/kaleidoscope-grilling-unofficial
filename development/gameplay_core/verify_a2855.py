"""Rack visual selection and owner-requested fixed cells; client QA is separate."""
from pathlib import Path
import subprocess
import sys
from verify_a2854 import main as previous

def main():
    previous()
    subprocess.run(['node','--test','development/gameplay_core/test_rack_visual_selection.mjs','development/gameplay_core/test_rack_geometry.mjs','development/gameplay_core/test_rack_tool_runtime.mjs'],cwd=Path(__file__).resolve().parents[2],check=True)
    subprocess.run([sys.executable,'development/gameplay_core/test_rack_tool_display.py'],cwd=Path(__file__).resolve().parents[2],check=True)
    print('Rack fixed-cell selection/resources PASS; owner adaptation, native/client acceptance separate')

if __name__=='__main__':main()
