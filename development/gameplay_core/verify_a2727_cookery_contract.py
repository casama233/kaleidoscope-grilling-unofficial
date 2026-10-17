from __future__ import annotations
import hashlib,sys,zipfile
from pathlib import Path

EXPECTED_SHA='c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351'

def main():
 if len(sys.argv)!=2:
  raise SystemExit('usage: verify_a2727_cookery_contract.py <Cookery 1.0.6 mcaddon>')
 p=Path(sys.argv[1])
 got=hashlib.sha256(p.read_bytes()).hexdigest()
 assert got==EXPECTED_SHA,(got,EXPECTED_SHA)

 with zipfile.ZipFile(p) as z:
  names=z.namelist()
  doc=next(n for n in names if n.endswith('[BP]/documentation/KC_EXTENSION_API.md'))
  registry=next(n for n in names if n.endswith('[BP]/scripts/api/extensionRegistry.js'))
  direct=next(n for n in names if n.endswith('[BP]/scripts/custom_components/blocks/directStation.js'))
  d=z.read(doc).decode('utf-8')
  r=z.read(registry).decode('utf-8')
  s=z.read(direct).decode('utf-8')

 joined=d+'\n'+r
 for token in (
  'kaleidoscope_cookery:api_ready',
  'kaleidoscope_cookery:api_ping',
  'kaleidoscope_cookery:register_recipe',
 ):
  assert token in joined,token
 assert 'chopping_board' in joined.lower()
 assert 'millstone' in joined.lower()

 # Public extension recipes are the normal path, but built-in board recipes
 # have priority. This is why the minecraft:beef adapter remains justified.
 assert 'const r=BOARD_RECIPES[id]||getExtensionBoardRecipe(id);' in s

 print('A2.7.27 Cookery 1.0.6 public extension host contract: PASS')
 print('host docs:',doc)
 print('host registry:',registry)
 print('beef exception: built-in chopping recipe precedes extension')

if __name__=='__main__':
 main()
