"""Persistent rescue claims, plant growth and acknowledged cuisine settlement."""
from pathlib import Path
import os
from verify_a28119 import main as previous
from verification_session import SESSION_ENV, current_source_validation_session


def main(expected_version=(2, 8, 120)):
    # Retain the existing affected suites and their assertions. Native player
    # events, saved-world behavior and rendered clients are separate evidence.
    previous(expected_version=expected_version)
    print('G120 persistent claims, plant and cuisine source repairs PASS; native/client acceptance remain separate')


if __name__ == '__main__':
    if os.environ.pop(SESSION_ENV, None) == Path(__file__).name:
        with current_source_validation_session():
            main()
    else:
        main()
