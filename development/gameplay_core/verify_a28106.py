"""G106 publishes the pending interaction fix with its synchronized guide."""
from verify_a28102 import main as previous


def main():
    previous(expected_version=(2, 8, 106))


if __name__ == '__main__':
    main()
