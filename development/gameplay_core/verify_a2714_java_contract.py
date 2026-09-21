from __future__ import annotations
import hashlib,json,urllib.request

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
FILES={
 'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/world/HouttuyniaCropBlock.java':'c906c305a2ede0587bdf3d543f5782a05a16d71e',
 'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/world/FortressWartReplacementHandler.java':'e0e5116dbf5f084efad161b1c32190351345ca4c',
 'common/src/main/resources/assets/kaleidoscope_grilling/blockstates/houttuynia_crop.json':'dbf5384b283635f91dfd9a68cf38f08437f99e16',
 'common/src/main/resources/data/kaleidoscope_grilling/loot_table/blocks/houttuynia_crop.json':'1affd5611dd36d3c8622aa04fd4a1c33b74f5300'
}

def git_blob(v):
 return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def fetch(path):
 req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.14-contract/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 assert git_blob(v)==FILES[path],(path,git_blob(v),FILES[path])
 return v

def main():
 crop=fetch(next(p for p in FILES if p.endswith('HouttuyniaCropBlock.java'))).decode()
 for token in (
  'BlockStateProperties.AGE_7',
  'BooleanProperty.create("red_variant")',
  'return 7;',
  'ModItems.HOUTTUYNIA.get()',
  'is(Blocks.SOUL_SAND)',
  'random.nextFloat() < 0.3F',
  'getRawBrightness(pos, 0) >= 8',
  'ground.getBlock() instanceof FarmBlock || state.is(Blocks.SOUL_SAND)'
 ):assert token in crop,token

 repl=fetch(next(p for p in FILES if p.endswith('FortressWartReplacementHandler.java'))).decode()
 for token in (
  'REPLACEMENT_PERCENT = 25',
  'event.isNewChunk()',
  'BuiltinStructures.FORTRESS',
  'state.is(Blocks.NETHER_WART)',
  'case 0 -> 0;',
  'case 1 -> 3;',
  'default -> 7;',
  '.setValue(HouttuyniaCropBlock.RED_VARIANT, true)'
 ):assert token in repl,token

 blockstate=json.loads(fetch(next(p for p in FILES if p.endswith('blockstates/houttuynia_crop.json'))))
 variants=blockstate['variants']
 assert len(variants)==16
 for age in range(5):
  assert variants[f'age={age},red_variant=false']==variants[f'age={age},red_variant=true']
 for age in (5,6,7):
  assert variants[f'age={age},red_variant=false']!=variants[f'age={age},red_variant=true']

 loot=json.loads(fetch(next(p for p in FILES if p.endswith('loot_table/blocks/houttuynia_crop.json'))))
 assert len(loot['pools'])==2
 assert loot['pools'][0]['entries'][0]['name']=='kaleidoscope_grilling:houttuynia'
 bonus=loot['pools'][1]
 assert bonus['conditions'][0]['properties']=={'age':'7'}
 fn=bonus['entries'][0]['functions'][0]
 assert fn['function']=='minecraft:apply_bonus'
 assert fn['enchantment']=='minecraft:fortune'
 assert fn['formula']=='minecraft:binomial_with_bonus_count'
 assert fn['parameters']=={'extra':1,'probability':0.5714286}

 print('A2.7.14 pinned Java Houttuynia crop contract: PASS')

if __name__=='__main__':main()
