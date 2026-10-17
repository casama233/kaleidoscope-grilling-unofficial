"""Native-editor-discovered held-frame repairs, retaining the complete baseline."""
from pathlib import Path
import subprocess,sys
from verify_a2812 import main as baseline
ROOT=Path(__file__).resolve().parents[2]
def main():
    baseline()
    for command in [
        [sys.executable,'development/gameplay_core/test_held_pose_frames.py'],
        [sys.executable,'tools/audit_grilling_render.py','--fail-on-error'],
    ]: subprocess.run(command,cwd=ROOT,check=True)
    print('A2.8.18 held frame/inventory regressions PASS; native screenshots are evidence, not client acceptance')
if __name__=='__main__':main()
