"""Source-faithful pepper worldgen; native feature placement remains separate evidence."""
from pathlib import Path
import subprocess
from verify_a2859 import main as previous

def main():
    previous()
    subprocess.run(['node','--test','development/gameplay_core/test_pepper_worldgen_seed.mjs'],cwd=Path(__file__).resolve().parents[2],check=True)
    print('A2.8.60 Java-shaped pepper seed placement/rollback regressions PASS; native evidence separate')

if __name__=='__main__':main()
