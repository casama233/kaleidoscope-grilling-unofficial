from __future__ import annotations
import hashlib,sys,zipfile
from pathlib import Path

EXPECTED_SHA='c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351'

def main():
 if len(sys.argv)!=2:
  raise SystemExit('usage: verify_a2734_cookery_contract.py <Cookery 1.0.6 mcaddon>')
 p=Path(sys.argv[1]);got=hashlib.sha256(p.read_bytes()).hexdigest()
 assert got==EXPECTED_SHA,(got,EXPECTED_SHA)

 with zipfile.ZipFile(p) as z:
  oil_name=next(n for n in z.namelist() if n.endswith('[BP]/scripts/custom_components/blocks/oilPot.js'))
  place_name=next(n for n in z.namelist() if n.endswith('[BP]/scripts/events/replaceablePlacement.js'))
  oil=z.read(oil_name).decode('utf-8')
  place=z.read(place_name).decode('utf-8')

 assert 'const CAPACITY = 256;' in oil
 assert 'const ITEM_KEY = "kc_oil_count";' in oil
 assert 'function itemOil(stack){try{return Math.max(0,Math.min(CAPACITY,Number(stack?.getDynamicProperty(ITEM_KEY)??0)));}catch{return 0;}}' in oil
 assert 'if(stack?.typeId===FILLED_POT&&raw===undefined)return CAPACITY' in oil

 assert 'const OIL_CAPACITY=256;' in place
 assert 'const OIL_ITEM_KEY="kc_oil_count";' in place
 assert 'if(item.typeId===FILLED_OIL_POT&&raw===undefined)return OIL_CAPACITY' in place

 print('A2.7.34 Cookery 1.0.6 oil-pot read-mode contract: PASS')
 print('normal item read: missing kc_oil_count -> 0')
 print('legacy placement read: missing kc_oil_count on filled pot -> 256')

if __name__=='__main__':
 main()
