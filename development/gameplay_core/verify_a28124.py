"""Keep all G123 gates; their existing API/food checks own seasoning reloads."""
from pathlib import Path
import os
from verify_a28123 import main as previous
from verification_session import SESSION_ENV, current_source_validation_session


def main(expected_version=(2, 8, 124)):
    previous(expected_version=expected_version)
    print('G124 retains G123 host and G122 conservation gates; registered seasoning reloads require separate native/client evidence')


if __name__ == '__main__':
    if os.environ.pop(SESSION_ENV, None) == Path(__file__).name:
        with current_source_validation_session():
            main()
    else:
        main()
