"""Plate outline target repair; affected cases remain in the existing chain."""
from pathlib import Path
import os
from verify_a28115 import main as previous
from verification_session import SESSION_ENV, current_source_validation_session

def main():
    previous(expected_version=(2, 8, 116))
    print('G116 plate outline source repairs PASS; native/client acceptance remain separate')

if __name__ == '__main__':
    if os.environ.pop(SESSION_ENV, None) == Path(__file__).name:
        with current_source_validation_session():
            main()
    else:
        main()
