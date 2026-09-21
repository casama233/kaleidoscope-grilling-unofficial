from __future__ import annotations
import hashlib,sys,zipfile
from pathlib import Path

EXPECTED_SHA='c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351'

def main():
 if len(sys.argv)!=2:raise SystemExit('usage: verify_a2710_cookery_contract.py <Cookery 1.0.6 mcaddon>')
 p=Path(sys.argv[1]);got=hashlib.sha256(p.read_bytes()).hexdigest();assert got==EXPECTED_SHA,(got,EXPECTED_SHA)
 with zipfile.ZipFile(p) as z:
  direct=next(n for n in z.namelist() if n.endswith('[BP]/scripts/custom_components/blocks/directStation.js'))
  data=next(n for n in z.namelist() if n.endswith('[BP]/scripts/data/stationRecipes.js'))
  s=z.read(direct).decode('utf-8');d=z.read(data).decode('utf-8')
 required_direct=[
  'const KNIVES=new Set(["kaleidoscope_cookery:iron_kitchen_knife","kaleidoscope_cookery:gold_kitchen_knife","kaleidoscope_cookery:diamond_kitchen_knife","kaleidoscope_cookery:netherite_kitchen_knife"])',
  '"minecraft:chicken":2',
  'kc_station:',
  'const r=BOARD_RECIPES[id]||getExtensionBoardRecipe(id);',
  'if((d.cuts||0)>=d.max){pop(b,d.result.id,d.result.count);save(b,{})'
 ]
 for token in required_direct:assert token in s,token
 assert '"minecraft:chicken":{"result":"kaleidoscope_cookery:raw_cut_small_meats","count":2,"cuts":4}' in d
 print('A2.7.10 Cookery 1.0.6 chicken-board/knife contract: PASS')
if __name__=='__main__':main()
