"""Native item icons, preserving all previous gameplay and held-route checks."""
import subprocess,sys
from pathlib import Path
from verify_a2832 import main as baseline

def main():
 baseline()
 subprocess.run([sys.executable,str(Path(__file__).with_name('test_native_item_icons.py'))],check=True)
 print('A2.8.33 exact source sprites and native sapling item PASS; native client acceptance pending')
if __name__=='__main__':main()
