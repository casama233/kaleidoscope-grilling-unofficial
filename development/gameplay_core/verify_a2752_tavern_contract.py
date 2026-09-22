from __future__ import annotations
import hashlib,json,urllib.request

BASE='https://raw.githubusercontent.com/casama233/kaleidoscope-tavern-unofficial/c9fb794eb83d7695155fba4479f8b8182dcb4687/'
FILES={
 1:('runtime/BP/items/vinegar_q1.json','43d4d31cba1097b39a23ac0a1081a7c1f107ca91'),
 2:('runtime/BP/items/vinegar_q2.json','57920faaa7d2abeac3f63e45955f4d7749dcf260'),
 3:('runtime/BP/items/vinegar_q3.json','0bf93d473d822f86c6d72237768a814a16892a13'),
 4:('runtime/BP/items/vinegar_q4.json','9807b1e57ff17cef95eeecff34a38ef223d5e548'),
 5:('runtime/BP/items/vinegar_q5.json','b450e891305cad6049161515d9ce238f6340ba9c'),
 6:('runtime/BP/items/vinegar_q6.json','025010d9a6a1738a9c4630014ceec498d4c4fc69'),
}
def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 for q,(path,sha) in FILES.items():
  req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.52-tavern-contract/1'})
  with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
  assert blob(v)==sha,(q,blob(v),sha)
  doc=json.loads(v.decode('utf-8'))
  ident=doc['minecraft:item']['description']['identifier']
  assert ident==f'kaleidoscope_tavern:vinegar_q{q}',(q,ident)
 print('A2.7.52 pinned Tavern Bedrock vinegar quality contract: PASS (q1..q6)')
if __name__=='__main__':main()
