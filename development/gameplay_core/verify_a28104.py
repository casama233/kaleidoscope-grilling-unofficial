"""G104 uses the existing icon regressions with its actual release identity."""
from verify_a28102 import main as previous


def main():
    previous(expected_version=(2, 8, 104))


if __name__ == '__main__':
    main()
