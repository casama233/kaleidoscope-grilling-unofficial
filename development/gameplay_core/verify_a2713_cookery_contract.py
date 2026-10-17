from __future__ import annotations
import hashlib,re,sys,zipfile
from pathlib import Path

EXPECTED_SHA='c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351'

def main():
 if len(sys.argv)!=2:raise SystemExit('usage: verify_a2713_cookery_contract.py <Cookery 1.0.6 mcaddon>')
 p=Path(sys.argv[1]);got=hashlib.sha256(p.read_bytes()).hexdigest();assert got==EXPECTED_SHA,(got,EXPECTED_SHA)
 with zipfile.ZipFile(p) as z:
  direct=next(n for n in z.namelist() if n.endswith('[BP]/scripts/custom_components/blocks/directStation.js'))
  data=next(n for n in z.namelist() if n.endswith('[BP]/scripts/data/stationRecipes.js'))
  s=z.read(direct).decode('utf-8');d=z.read(data).decode('utf-8')
 assert 'const r=BOARD_RECIPES[id]||getExtensionBoardRecipe(id);' in s
 assert not re.search(r'"kaleidoscope_grilling:houttuynia"\s*:',d), 'Cookery now has a built-in houttuynia board recipe; extension parity must be re-audited'
 print('A2.7.13 Cookery 1.0.6 houttuynia extension contract: PASS')

if __name__=='__main__':main()
