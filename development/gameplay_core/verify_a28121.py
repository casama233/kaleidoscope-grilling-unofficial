"""Saved Java pot phases, native cuisine quality and plant cost ownership."""
from pathlib import Path
import os
import subprocess
from verify_a28120 import main as previous
from verification_session import SESSION_ENV, current_source_validation_session

ROOT = Path(__file__).resolve().parents[2]


def main(expected_version=(2, 8, 121)):
    # Keep all inherited gates. These new checks are pure data/storage only;
    # native players, saved worlds and rendered clients need separate evidence.
    previous(expected_version=expected_version)
    for name in ('test_plant_fertilizer_storage.mjs', 'test_java_pot_core.mjs', 'test_cuisine_quality_java.mjs'):
        subprocess.run(['node', str(ROOT / 'development/gameplay_core' / name)], cwd=ROOT, check=True)
    print('G121 pot, quality and plant source repairs PASS; native/client acceptance remain separate')


if __name__ == '__main__':
    if os.environ.pop(SESSION_ENV, None) == Path(__file__).name:
        with current_source_validation_session():
            main()
    else:
        main()
