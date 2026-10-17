from __future__ import annotations
import hashlib,sys,zipfile
from pathlib import Path

EXPECTED_SHA='c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351'

def main():
 if len(sys.argv)!=2:
  raise SystemExit('usage: verify_a2731_cookery_contract.py <Cookery 1.0.6 mcaddon>')
 p=Path(sys.argv[1])
 got=hashlib.sha256(p.read_bytes()).hexdigest()
 assert got==EXPECTED_SHA,(got,EXPECTED_SHA)

 with zipfile.ZipFile(p) as z:
  names=z.namelist()
  doc=next(n for n in names if n.endswith('[BP]/documentation/KC_EXTENSION_API.md'))
  registry=next(n for n in names if n.endswith('[BP]/scripts/api/extensionRegistry.js'))
  d=z.read(doc).decode('utf-8')
  r=z.read(registry).decode('utf-8')

 joined=(d+'\n'+r).lower()
 assert 'kaleidoscope_cookery:api_ready' in joined
 assert 'kaleidoscope_cookery:register_recipe' in joined

 # v1.0.6 exposes recipe/station extensions, but no public crop lifecycle
 # registration surface. Check explicit API-style spellings rather than the
 # generic word "crop", which could appear in unrelated documentation prose.
 forbidden=(
  'register_crop','registercrop','crop_extension','cropextension',
  'crop_ready','cropready','kind":"crop"',"kind:'crop'",
  'capability":"crop"',"capability:'crop'"
 )
 hits=[token for token in forbidden if token in joined]
 assert not hits,('Cookery now appears to expose crop extension API; re-audit A2.7.31',hits)

 print('A2.7.31 Cookery 1.0.6 crop-extension audit: PASS')
 print('No public crop registration surface detected in KC_EXTENSION_API.md / extensionRegistry.js')

if __name__=='__main__':
 main()
