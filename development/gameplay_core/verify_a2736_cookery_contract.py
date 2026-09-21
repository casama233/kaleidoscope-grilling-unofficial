from __future__ import annotations
import hashlib,sys,zipfile
from pathlib import Path
EXPECTED='c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351'
def main():
 if len(sys.argv)!=2:raise SystemExit('usage: verify_a2736_cookery_contract.py <Cookery 1.0.6 mcaddon>')
 p=Path(sys.argv[1]);assert hashlib.sha256(p.read_bytes()).hexdigest()==EXPECTED
 with zipfile.ZipFile(p) as z:
  oil=z.read(next(n for n in z.namelist() if n.endswith('[BP]/scripts/custom_components/blocks/oilPot.js'))).decode('utf-8')
  place=z.read(next(n for n in z.namelist() if n.endswith('[BP]/scripts/events/replaceablePlacement.js'))).decode('utf-8')
 for token in ('const POT = "kaleidoscope_cookery:oil_pot";','const CAPACITY = 256;','const ITEM_KEY = "kc_oil_count";','kc_oilpot:','"kaleidoscope_cookery:has_oil"'):
  assert token in oil,token
 assert 'world.afterEvents.playerBreakBlock.subscribe' in oil
 assert 'world.afterEvents.blockExplode.subscribe' in oil
 assert 'const amount=read(pseudo);' in oil and 'const drop=makePotItem(amount);' in oil
 assert 'const amount=read(b);' in oil and 'const drop=makePotItem(amount);' in oil
 for token in ('const OIL_POT="kaleidoscope_cookery:oil_pot";','const FILLED_OIL_POT="kaleidoscope_cookery:oil_pot_filled";','const OIL_ITEM_KEY="kc_oil_count";','const OIL_CAPACITY=256;'):
  assert token in place,token
 print('A2.7.36 Cookery 1.0.6 placed oil-pot host contract: PASS')
 print('host break/explosion drops are after-events, so before-event interception can replace typed drops without duplication')
if __name__=='__main__':main()
