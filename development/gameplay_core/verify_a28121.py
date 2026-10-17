"""Retain G120 checks for the registered shared Tavern guide entrance."""
from pathlib import Path
import os
from verify_a28120 import main as previous
from verification_session import SESSION_ENV, current_source_validation_session


def main(expected_version=(2, 8, 121)):
    previous(expected_version=expected_version)
    print('G121 retains G120 source checks and the registered Tavern guide bridge; native/client acceptance remain separate')


if __name__ == '__main__':
    if os.environ.pop(SESSION_ENV, None) == Path(__file__).name:
        with current_source_validation_session():
            main()
    else:
        main()
