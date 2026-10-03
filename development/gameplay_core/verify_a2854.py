"""Stop/completion ordering; native timing remains a separate acceptance gate."""
from pathlib import Path
import subprocess
from verify_a2853 import main as previous

def main():
    previous()
    subprocess.run(['node','--test','development/gameplay_core/test_java_release_grace.mjs'],cwd=Path(__file__).resolve().parents[2],check=True)
    print('Stop/completion boundary/order regressions PASS; native timing acceptance separate')

if __name__=='__main__':main()
