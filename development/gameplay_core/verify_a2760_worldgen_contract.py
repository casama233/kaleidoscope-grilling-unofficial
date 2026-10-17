from __future__ import annotations
import hashlib,urllib.request
from pathlib import Path

MOJANG_COMMIT='46ba6ea985fb5a92d79a9419198f10dda14c199d'
MOJANG_BASE=f'https://raw.githubusercontent.com/Mojang/bedrock-samples/{MOJANG_COMMIT}/'
FEATURES_PATH='documentation/Features.html'
FEATURES_BLOB='dfb66d2371e818bea6bfffb1c1785d956a76b6d6'

ROOT=Path(__file__).resolve().parents[2]

def git_blob(v:bytes)->str:
 return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def fetch(path):
 req=urllib.request.Request(MOJANG_BASE+path,headers={'User-Agent':'Grilling-A2.7.60-worldgen-contract/1'})
 with urllib.request.urlopen(req,timeout=90) as r:return r.read()

def main():
 data=fetch(FEATURES_PATH)
 actual=git_blob(data);assert actual==FEATURES_BLOB,(actual,FEATURES_BLOB)
 text=data.decode('utf-8')
 start=text.index('"acacia_trunk"')
 example=text[start:start+4500]
 for token in (
  '"trunk_lean"',
  '"allow_diagonal_growth": true',
  '"lean_height"',
  '"lean_steps"',
  '"random_spread_canopy"',
  '["minecraft:azalea_leaves", 3]',
  '["minecraft:azalea_leaves_flowered", 1]',
 ):
  assert token in example,token

 # Keep the published pack fix aligned with the already BDS-validated server-edition shim.
 shim=(ROOT/'tools/build_server_edition.py').read_text(encoding='utf-8')
 assert "for k in ('lean_height', 'lean_steps')" in shim
 assert "trunk.setdefault('lean_height', {'base': 1, 'intervals': [1], 'min_height_for_canopy': 2})" in shim
 assert "trunk.setdefault('lean_steps', {'base': 1, 'intervals': [1]})" in shim

 server_doc=(ROOT/'docs/STATUS-A2.7.14-SERVER.md').read_text(encoding='utf-8')
 assert 'No definition found for feature' in server_doc
 assert 'lean_height' in server_doc and 'lean_steps' in server_doc
 assert '兩包內容日誌 0 錯誤' in server_doc

 print('A2.7.60 Mojang tree-feature + BDS evidence contract: PASS')
 print('mojang commit:',MOJANG_COMMIT)
 print('features blob:',FEATURES_BLOB)

if __name__=='__main__':main()
