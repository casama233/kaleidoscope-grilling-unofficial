"""Bottle native attachment regression; client acceptance remains separate."""
import subprocess,sys
from pathlib import Path
from verify_a2845 import main as baseline
def main():
    baseline()
    subprocess.run([sys.executable,str(Path(__file__).with_name('test_native_bottle_fp.py'))],check=True)
    print('A2.8.46 bottle native projection PASS; client rendering unaccepted')
if __name__=='__main__':main()
