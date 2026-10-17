from pathlib import Path
import subprocess
import sys
from verify_a2846 import main as previous


def main():
    previous()
    subprocess.run([sys.executable, str(Path(__file__).with_name('test_eating_arms.py'))], check=True)
    print('A2.8.47 third-person eating arm fallback PASS; human rendering unaccepted')


if __name__ == '__main__':
    main()
