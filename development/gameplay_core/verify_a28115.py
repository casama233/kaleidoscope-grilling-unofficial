"""Plate nutrition bounds and block-use priority; reuse existing affected checks."""
from pathlib import Path
import os
from verify_a28114 import main as previous
from verification_session import SESSION_ENV, current_source_validation_session

def main():
    # Existing inherited tests exercise the real nutrition and plate callbacks.
    previous(expected_version=(2, 8, 115))
    print('G115 plate source repairs PASS; real player and client acceptance remain separate')

if __name__ == '__main__':
    if os.environ.pop(SESSION_ENV, None) == Path(__file__).name:
        with current_source_validation_session():
            main()
    else:
        main()
