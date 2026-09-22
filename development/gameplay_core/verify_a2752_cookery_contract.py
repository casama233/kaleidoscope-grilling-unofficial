from __future__ import annotations
import hashlib,sys,zipfile
from pathlib import Path
EXPECTED_SHA='c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351'

def read_named(z,suffix):
 names=[n for n in z.namelist() if n.endswith(suffix)]
 assert len(names)==1,(suffix,names)
 return z.read(names[0]).decode('utf-8'),names[0]

def main():
 if len(sys.argv)!=2:raise SystemExit('usage: verify_a2752_cookery_contract.py <Cookery-1.0.6.mcaddon>')
 p=Path(sys.argv[1]);assert p.is_file(),p
 got=hashlib.sha256(p.read_bytes()).hexdigest();assert got==EXPECTED_SHA,(got,EXPECTED_SHA)
 with zipfile.ZipFile(p) as z:
  docs,_=read_named(z,'[BP]/documentation/KC_EXTENSION_API.md')
  registry,_=read_named(z,'[BP]/scripts/api/extensionRegistry.js')
 for token in (
  '"stockpot_exact"','"stockpot_flex"','kaleidoscope_cookery:register_recipe','kaleidoscope_cookery:api_ready'
 ):assert token in docs,('docs',token)
 for token in (
  'function normalizeStockpot(raw,flex=false)',
  'else if(kind==="stockpot_exact")','else if(kind==="stockpot_flex")',
  'getStockpotExactRecipes()','getStockpotFlexRecipes()'
 ):assert token in registry,('registry',token)
 print('A2.7.52 pinned Cookery 1.0.6 Stockpot host contract: PASS')
 print('public_api=stockpot_exact,stockpot_flex; direct station bridge inherited from verified A2.7.50')
if __name__=='__main__':main()
