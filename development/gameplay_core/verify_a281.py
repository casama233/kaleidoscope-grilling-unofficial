"""A2.8.1 focused fixes plus the complete A2.8.0 regression suite."""
import sys
from pathlib import Path
import a281_visual_contract as c
import verify_a280 as prior

def main():
 c.vat_contract();c.icon_contract();c.baseline_contract()
 prior.run(sys.executable,str(Path(__file__).with_name('a281_bottle_icons.py')),'--check')
 prior.run(sys.executable,str(Path(__file__).with_name('test_a281_visual.py')))
 prior.main(version=(2,8,1),proof_name='a281-invariants.json')
if __name__=='__main__':main()
