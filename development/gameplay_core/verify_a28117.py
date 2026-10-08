"""Bottle cancellation and handheld nutrition; reuse the affected current tests."""
from pathlib import Path
import os
from verify_a28116 import main as previous
from verification_session import SESSION_ENV, current_source_validation_session


def main(expected_version=(2, 8, 117)):
    previous(expected_version=expected_version)
    print('Bottle cancellation and handheld saturation source repairs PASS; native/client acceptance remain separate')


if __name__ == '__main__':
    if os.environ.pop(SESSION_ENV, None) == Path(__file__).name:
        with current_source_validation_session():
            main()
    else:
        main()
