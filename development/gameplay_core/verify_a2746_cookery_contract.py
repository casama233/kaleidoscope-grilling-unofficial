from __future__ import annotations
import hashlib,sys,zipfile
from pathlib import Path

EXPECTED_SHA='c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351'
NEEDED=(
 'kaleidoscope_cookery:kitchen_knife',
 'kaleidoscope_cookery:kitchen_shovel',
 'kaleidoscope_cookery:oil_pot',
)

def main():
 if len(sys.argv)!=2:raise SystemExit('usage: verify_a2746_cookery_contract.py <Cookery 1.0.6 mcaddon>')
 p=Path(sys.argv[1]);got=hashlib.sha256(p.read_bytes()).hexdigest();assert got==EXPECTED_SHA,(got,EXPECTED_SHA)
 hits={k:[] for k in NEEDED}
 with zipfile.ZipFile(p) as z:
  for name in z.namelist():
   if '/items/' not in name or not name.endswith('.json'):continue
   try:s=z.read(name).decode('utf-8-sig')
   except Exception:continue
   for key in NEEDED:
    if key in s:hits[key].append(name)
 for key,files in hits.items():assert files,(key,'missing from Cookery item JSON')
 print('A2.7.46 Cookery rack tag/id contract: PASS')
 for key,files in hits.items():print(key,'=>',files[:8])

if __name__=='__main__':main()
