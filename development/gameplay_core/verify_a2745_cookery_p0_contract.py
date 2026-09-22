from __future__ import annotations
import sys,zipfile
from pathlib import Path

def read_named(z,suffix):
 names=[n for n in z.namelist() if n.endswith(suffix)]
 assert len(names)==1,(suffix,names)
 return z.read(names[0]).decode('utf-8'),names[0]

def main():
 if len(sys.argv)!=2:raise SystemExit('usage: verify_a2745_cookery_p0_contract.py <Cookery-1.0.6.mcaddon>')
 p=Path(sys.argv[1]);assert p.is_file(),p
 with zipfile.ZipFile(p) as z:
  docs,_=read_named(z,'[BP]/documentation/KC_EXTENSION_API.md')
  registry,_=read_named(z,'[BP]/scripts/api/extensionRegistry.js')
  direct,_=read_named(z,'[BP]/scripts/events/directStation.js')

 for token in (
  '"wok"','"stockpot_exact"','"stockpot_flex"',
  'kaleidoscope_cookery:register_recipe','kaleidoscope_cookery:api_ready',
 ):
  assert token in docs,('docs',token)

 for token in (
  'function normalizeWok(raw)','function normalizeStockpot(raw,flex=false)',
  'if(kind==="wok")','else if(kind==="stockpot_exact")','else if(kind==="stockpot_flex")',
  'stirs:1, extension:true',
  'getWokRecipes()','getStockpotExactRecipes()','getStockpotFlexRecipes()',
 ):
  assert token in registry,('registry',token)
 assert 'kind==="wok_flex"' not in registry

 for token in (
  '"kaleidoscope_cookery:pot"','"kaleidoscope_cookery:stockpot"',
  '"kaleidoscope_cookery:oil"','"kaleidoscope_cookery:oil_pot_filled"',
  '"kaleidoscope_cookery:kitchen_shovel_has_oil"',
  'consumeOilFromHeldPot',
 ):
  assert token in direct,('directStation',token)

 print('A2.7.45 pinned Cookery 1.0.6 P0 host contract: PASS')
 print('public_api=wok,stockpot_exact,stockpot_flex; wok_flex=false; private_station_state=host-owned')

if __name__=='__main__':main()
