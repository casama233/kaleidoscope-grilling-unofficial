from __future__ import annotations
import hashlib,sys,zipfile
from pathlib import Path

EXPECTED_SHA='c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351'
CANOLA='kaleidoscope_grilling:canola_seeds'

def main():
 if len(sys.argv)!=2:raise SystemExit('usage: verify_a2716_cookery_contract.py <Cookery 1.0.6 mcaddon>')
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
 assert 'millstone' in joined.lower()
 candidates=[
  (name,s) for name,s in texts.items()
  if 'millstone' in s.lower() and ('extension' in s.lower() or 'register_recipe' in s)
 ]
 assert candidates,'Cookery millstone extension path no longer discoverable'
 lookup_tokens=('getExtensionMillstoneRecipe','extensionMillstone','MILLSTONE_EXTENSION','millstoneExtensions')
 assert any(any(token in s for token in lookup_tokens) for _,s in candidates) or any('getExtension' in s and 'millstone' in s.lower() for _,s in candidates), [n for n,_ in candidates]
 assert CANOLA not in joined,'Cookery now owns a canola_seeds recipe/input; re-audit extension precedence'
 print('A2.7.16 Cookery 1.0.6 millstone extension contract: PASS')
 print('millstone extension candidates:',','.join(n for n,_ in candidates[:8]))
if __name__=='__main__':main()
