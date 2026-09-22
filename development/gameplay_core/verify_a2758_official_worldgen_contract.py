from __future__ import annotations
import hashlib,urllib.request

SOURCES={
 'features':(
  'https://raw.githubusercontent.com/Mojang/bedrock-samples/46ba6ea985fb5a92d79a9419198f10dda14c199d/documentation/Features.html',
  'leaf_blocks',
  ('["minecraft:azalea_leaves", 3]','["minecraft:azalea_leaves_flowered", 1]')
 ),
 'tick':(
  'https://raw.githubusercontent.com/Mojang/bedrock-schemas/569b6c57fe55f7433d89d40f1b10dbec7e73bcfd/schemas/bp/blocks/block_minecraft_tick.schema.json',
  'interval_range',
  ('"looping"','If false, the block will only be ticked once')
 ),
}

def main():
 for name,(url,anchor,tokens) in SOURCES.items():
  req=urllib.request.Request(url,headers={'User-Agent':'Grilling-A2.7.58-contract/1'})
  with urllib.request.urlopen(req,timeout=90) as r:data=r.read()
  text=data.decode('utf-8')
  assert anchor in text,(name,anchor)
  for token in tokens:assert token in text,(name,token)
  print(name,hashlib.sha256(data).hexdigest())
 print('A2.7.58 pinned official Bedrock worldgen/tick contracts: PASS')

if __name__=='__main__':main()
