from __future__ import annotations
import hashlib,sys,zipfile
from pathlib import Path
EXPECTED_SHA='c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351'

def read_named(z,suffix):
 names=[n for n in z.namelist() if n.endswith(suffix)]
 assert len(names)==1,(suffix,names)
 return z.read(names[0]).decode('utf-8'),names[0]

def main():
 if len(sys.argv)!=2:raise SystemExit('usage: verify_a2750_cookery_contract.py <Cookery-1.0.6.mcaddon>')
 p=Path(sys.argv[1]);assert p.is_file(),p
 got=hashlib.sha256(p.read_bytes()).hexdigest();assert got==EXPECTED_SHA,(got,EXPECTED_SHA)
 with zipfile.ZipFile(p) as z:
  docs,_=read_named(z,'[BP]/documentation/KC_EXTENSION_API.md')
  registry,_=read_named(z,'[BP]/scripts/api/extensionRegistry.js')
  direct,_=read_named(z,'[BP]/scripts/events/directStation.js')
 for token in (
  '"wok"','kaleidoscope_cookery:register_recipe','kaleidoscope_cookery:api_ready',
 ):assert token in docs,('docs',token)
 for token in (
  'function normalizeWok(raw)','if(kind==="wok")','stirs:1, extension:true','getWokRecipes()',
 ):assert token in registry,('registry',token)
 assert 'kind==="wok_flex"' not in registry
 for token in (
  '"kaleidoscope_cookery:pot"','"kaleidoscope_cookery:oil"','"kaleidoscope_cookery:oil_pot_filled"',
  '"kaleidoscope_cookery:kitchen_shovel_has_oil"','consumeOilFromHeldPot',
 ):assert token in direct,('directStation',token)
 print('A2.7.50 pinned Cookery 1.0.6 Wok host contract: PASS')
 print('public_api=wok; private_station_state=host-owned; flex_wok=false')
if __name__=='__main__':main()
