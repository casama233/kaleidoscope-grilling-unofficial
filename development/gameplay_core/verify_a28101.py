"""Direct scalar Cloud fallback transport, preserving the G100 source lineage."""
from verify_a28100 import main as previous

def main(expected_version=(2,8,101)):
    # The inherited G48/G83 paths already run both affected suites and the
    # reproducible Cloud generator; do not duplicate their functional passes.
    previous(expected_version=expected_version)

if __name__=='__main__':
    main()
