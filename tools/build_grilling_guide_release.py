"""Deprecated guide-only command: build the complete Grilling product instead."""
import sys
from build_grilling_release import main
if __name__=='__main__':
    print('Guide-only packaging is retired. Building Grilling with its built-in chapter.',file=sys.stderr)
    main()
