from __future__ import annotations
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE_REPO='casama233/kaleidoscope-tavern-unofficial'
SOURCE_COMMIT='c9fb794eb83d7695155fba4479f8b8182dcb4687'
FILES={
 1:'43d4d31cba1097b39a23ac0a1081a7c1f107ca91',
 2:'57920faaa7d2abeac3f63e45955f4d7749dcf260',
 3:'0bf93d473d822f86c6d72237768a814a16892a13',
 4:'9807b1e57ff17cef95eeecff34a38ef223d5e548',
 5:'b450e891305cad6049161515d9ce238f6340ba9c',
 6:'025010d9a6a1738a9c4630014ceec498d4c4fc69',
}
def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 for q,sha in FILES.items():
  path=ROOT/'contracts'/f'a2752_tavern_vinegar_q{q}.json'
  assert path.is_file(),path
  data=path.read_bytes()
  assert blob(data)==sha,(q,blob(data),sha)
  doc=json.loads(data.decode('utf-8'))
  ident=doc['minecraft:item']['description']['identifier']
  assert ident==f'kaleidoscope_tavern:vinegar_q{q}',(q,ident)
  assert doc['minecraft:item']['components']['minecraft:max_stack_size']==16
 print('A2.7.52 pinned Tavern Bedrock vinegar quality contract: PASS (q1..q6)')
 print('source:',SOURCE_REPO+'@'+SOURCE_COMMIT)
if __name__=='__main__':main()
