"""Java use eligibility and configured nested saturation regression."""
from pathlib import Path
import subprocess
from verify_a2852 import main as previous

def main():
    previous()
    subprocess.run(['node','--test','development/gameplay_core/test_java_use_gates.mjs'],cwd=Path(__file__).resolve().parents[2],check=True)
    print('A2.8.53 Java skewer use gates and nested nutrition PASS; native/client evidence separate')

if __name__=='__main__':main()
