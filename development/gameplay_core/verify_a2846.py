"""Inventory series attribution; inherited 2.8.45 regressions remain required."""
import subprocess
import sys
from pathlib import Path
from verify_a2845 import main as previous


def main():
    previous()
    subprocess.run([sys.executable, str(Path(__file__).with_name('test_item_labels.py'))], check=True)
    print('A2.8.46 localized inventory labels PASS; human rendering remains separate')


if __name__ == '__main__':
    main()
