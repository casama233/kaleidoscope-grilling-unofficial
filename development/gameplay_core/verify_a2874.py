"""Current portable fidelity repairs; reuse the unchanged source chain once."""
from pathlib import Path
import subprocess,sys
from verify_a2873 import main as previous
ROOT=Path(__file__).resolve().parents[2]
def main():
 previous(expected_version=(2,8,74))
 for name in ('test_finished_bottle_icons.py','test_bottle_fill_proxy_assets.py'):
  subprocess.run([sys.executable,str(ROOT/'development/gameplay_core'/name)],cwd=ROOT,check=True)
 for name in ('build_finished_bottle_icons.py','build_bottle_fill_proxies.py'):
  subprocess.run([sys.executable,str(ROOT/'development/gameplay_core'/name),'--check'],cwd=ROOT,check=True)
 subprocess.run(['node','--experimental-vm-modules','--test','development/gameplay_core/test_java_heat_deadlines.mjs'],cwd=ROOT,check=True)
 subprocess.run(['node','--test','development/gameplay_core/test_bottle_fill_proxies.mjs'],cwd=ROOT,check=True)
if __name__=='__main__':main()
