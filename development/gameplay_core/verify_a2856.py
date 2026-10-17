"""Fourth-flip ingredient snapshot and snapshot-only station display."""
from pathlib import Path
import subprocess
from verify_a2855 import main as previous

def main():
    previous()
    subprocess.run(['node','--test','development/gameplay_core/test_fourth_flip_snapshot.mjs'],cwd=Path(__file__).resolve().parents[2],check=True)
    print('A2.8.56 fourth-flip snapshot/rollback PASS; native persistence and visuals remain separate')

if __name__=='__main__':main()
