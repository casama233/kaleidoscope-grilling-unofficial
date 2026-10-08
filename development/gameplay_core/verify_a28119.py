"""Held plates, explicit plant adapters and acknowledged Heavy Metal transfer."""
from pathlib import Path
import os
import subprocess
import sys
from verify_a28118 import main as previous
from verification_session import SESSION_ENV, current_source_validation_session

ROOT = Path(__file__).resolve().parents[2]


def main(expected_version=(2, 8, 119)):
    # The inherited chain already owns player, bottle, secret, hand-pose and
    # source-conservation checks. Add only the new plate generator boundary.
    previous(expected_version=expected_version)
    subprocess.run([
        sys.executable, '-B', 'tools/build_plate_held.py', '--check',
    ], cwd=ROOT, check=True)
    print('G119 held plates, plant adapters and Heavy Metal source repairs PASS; native/client acceptance remain separate')


if __name__ == '__main__':
    if os.environ.pop(SESSION_ENV, None) == Path(__file__).name:
        with current_source_validation_session():
            main()
    else:
        main()
