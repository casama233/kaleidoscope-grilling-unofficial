"""A2.8.8 local-review registration; retain preceding gates, then add static/pure checks.
The candidate author has not run the full repository CI or Dash build.
"""
from pathlib import Path
import subprocess,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROJECT=ROOT/'projects/grilling/gameplay_core'
if __name__=='__main__':
    # Do not replace or weaken the previously required baseline gates.
    subprocess.run([sys.executable,str(HERE/'verify_a287.py'),*sys.argv[1:]],check=True)
    subprocess.run([sys.executable,str(PROJECT/'review/validate_candidate.py')],check=True)
