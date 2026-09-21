from __future__ import annotations
import hashlib,sys,zipfile
from pathlib import Path

EXPECTED_SHA='c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351'
ONION='kaleidoscope_grilling:onion'

def main():
 if len(sys.argv)!=2:raise SystemExit('usage: verify_a2718_cookery_contract.py <Cookery 1.0.6 mcaddon>')
 p=Path(sys.argv[1]);got=hashlib.sha256(p.read_bytes()).hexdigest();assert got==EXPECTED_SHA,(got,EXPECTED_SHA)
 with zipfile.ZipFile(p) as z:
  texts={}
  for name in z.namelist():
   if '[BP]/scripts/' not in name or not name.endswith('.js'):continue
   try:texts[name]=z.read(name).decode('utf-8')
   except UnicodeDecodeError:continue
 joined='\n'.join(texts.values())
 assert 'kaleidoscope_cookery:api_ready' in joined
 assert 'kaleidoscope_cookery:register_recipe' in joined
 candidates=[(name,s) for name,s in texts.items() if 'millstone' in s.lower() and ('extension' in s.lower() or 'register_recipe' in s)]
 assert candidates,'Cookery millstone extension path no longer discoverable'
 lookup_tokens=('getExtensionMillstoneRecipe','extensionMillstone','MILLSTONE_EXTENSION','millstoneExtensions')
 assert any(any(token in s for token in lookup_tokens) for _,s in candidates) or any('getExtension' in s and 'millstone' in s.lower() for _,s in candidates),[n for n,_ in candidates]
 assert ONION not in joined,'Cookery now owns kaleidoscope_grilling:onion internally; re-audit millstone precedence'
 print('A2.7.18 Cookery 1.0.6 onion millstone extension contract: PASS')
if __name__=='__main__':main()
