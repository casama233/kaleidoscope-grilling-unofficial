from __future__ import annotations
import hashlib,sys,zipfile,re
from pathlib import Path
EXPECTED='c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351'
def main():
 p=Path(sys.argv[1]);assert hashlib.sha256(p.read_bytes()).hexdigest()==EXPECTED
 with zipfile.ZipFile(p) as z:
  oil=z.read(next(n for n in z.namelist() if n.endswith('[BP]/scripts/custom_components/blocks/oilPot.js'))).decode('utf-8')
  place=z.read(next(n for n in z.namelist() if n.endswith('[BP]/scripts/events/replaceablePlacement.js'))).decode('utf-8')
 for token in ('kc_oilpot:','kc_oil_count','kaleidoscope_cookery:oil_pot_filled','kaleidoscope_cookery:has_oil','256'):
  assert token in oil,token
 for token in ('kc_oil_count','kaleidoscope_cookery:oil_pot_filled','kaleidoscope_cookery:oil_pot','256'):
  assert token in place,token
 assert re.search(r'playerBreakBlock|blockExplode',oil), 'host break/explosion lifecycle not found'
 print('A2.7.35 Cookery 1.0.6 placed oil-pot host contract: PASS')
if __name__=='__main__':main()
