"""Deterministic eating animation serialization across platform math libraries."""
from pathlib import Path
import subprocess,sys
from verify_a2858 import main as previous

def main():
    previous()
    subprocess.run([sys.executable,'development/gameplay_core/test_eating_serialization.py'],cwd=Path(__file__).resolve().parents[2],check=True)
    print('A2.8.59 deterministic zero/initial-Euler serialization PASS; client parity remains separate')

if __name__=='__main__':main()
