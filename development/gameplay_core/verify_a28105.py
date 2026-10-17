"""G105 keeps the current checks and source-bound pending placement cases."""
from verify_a28102 import main as previous


def main():
    previous(expected_version=(2, 8, 105))


if __name__ == '__main__':
    main()
