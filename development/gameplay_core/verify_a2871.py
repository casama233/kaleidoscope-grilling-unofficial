"""Rebuilt bottle source fixes; native acceptance remains a separate gate."""
from pathlib import Path
import subprocess,sys
from verify_a2868 import main as previous
ROOT=Path(__file__).resolve().parents[2]
def main():
 previous(expected_version=(2,8,71))
 for name in ('test_finished_bottle_icons.py','test_bottle_fill_proxy_assets.py'):
  subprocess.run([sys.executable,str(ROOT/'development/gameplay_core'/name)],cwd=ROOT,check=True)
 for name in ('build_finished_bottle_icons.py','build_bottle_fill_proxies.py'):
  subprocess.run([sys.executable,str(ROOT/'development/gameplay_core'/name),'--check'],cwd=ROOT,check=True)
 subprocess.run(['node','--test',str(ROOT/'development/gameplay_core/test_bottle_fill_proxies.mjs')],cwd=ROOT,check=True)
 print('G71 rebuilt bottle source checks PASS; native/client acceptance pending')
if __name__=='__main__':main()
