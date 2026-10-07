"""Original flatulence BlockPos sound origin and per-operation float pitch."""
from verify_a2886 import main as previous
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[2]

def main(expected_version=(2,8,87)):
    previous(expected_version=expected_version)
    subprocess.run(["node","--test","development/gameplay_core/test_flatulence_sound.mjs"],cwd=ROOT,check=True)

if __name__=="__main__":
    main()
