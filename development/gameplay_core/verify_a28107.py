"""Original ground descent plus exact Native legacy-field relations."""
from pathlib import Path
import subprocess
import sys
from verify_a28102 import main as previous

ROOT = Path(__file__).resolve().parents[2]


def main(expected_version=(2, 8, 107)):
    previous(expected_version=expected_version)
    subprocess.run([sys.executable, 'tools/build_projectile_dodge_ground_catalog.py', '--check'], cwd=ROOT, check=True)
    subprocess.run(['node', '--test', 'development/gameplay_core/test_projectile_dodge_ground_catalog.mjs',
                    'development/gameplay_core/test_projectile_dodge_native_alias.mjs',
                    'development/gameplay_core/test_projectile_dodge_ground_composition.mjs'], cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
