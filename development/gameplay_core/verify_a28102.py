"""G102 native GUI fallback icons; preserve the latest functional chain."""
from pathlib import Path
import subprocess
import sys
from verify_a28101 import main as previous

ROOT = Path(__file__).resolve().parents[2]


def main(expected_version=(2, 8, 102)):
    previous(expected_version=expected_version)
    subprocess.run([sys.executable, 'tools/build_skewer_inventory_icons.py', '--check'], cwd=ROOT, check=True)
    subprocess.run([sys.executable, 'tools/test_skewer_inventory_icons.py'], cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
