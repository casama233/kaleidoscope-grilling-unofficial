from __future__ import annotations
import hashlib,urllib.request

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
FILES={
 'placed':(
  'common/src/main/resources/data/kaleidoscope_grilling/worldgen/placed_feature/pepper_tree.json',
  'fb1517f27394ef410250f7369b9aab3f9ca19955',
  (
   '"type": "minecraft:rarity_filter", "chance": 16',
   '"type": "minecraft:in_square"',
   '"type": "minecraft:surface_water_depth_filter", "max_water_depth": 0',
   '"type": "minecraft:heightmap", "heightmap": "OCEAN_FLOOR"',
   '"type": "minecraft:biome"',
  )
 ),
 'biome_modifier':(
  'common/src/main/resources/data/kaleidoscope_grilling/neoforge/biome_modifier/add_pepper_tree.json',
  '3a03e6c31e96bd049e198759ee55ef87d0ec9dbb',
  (
   '"biomes": "#minecraft:is_forest"',
   '"features": "kaleidoscope_grilling:pepper_tree"',
   '"step": "vegetal_decoration"',
  )
 ),
}

def git_blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 for name,(path,expected,tokens) in FILES.items():
  req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.51-contract/1'})
  with urllib.request.urlopen(req,timeout=90) as r:data=r.read()
  actual=git_blob(data);assert actual==expected,(name,actual,expected)
  s=data.decode('utf-8')
  for token in tokens:assert token in s,(name,token)
 print('A2.7.51 pinned Java Pepper forest worldgen contract: PASS')

if __name__=='__main__':main()
