from __future__ import annotations
import hashlib,json,urllib.request

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
FILES={
 'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/world/OnionCropBlock.java':'881b9e426e5108b28ad366d248cf6208be797504',
 'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/world/CropDropHandler.java':'36a58893c4788626a6b5a610b2a230fd709b4ece',
 'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/registry/ModItems.java':'6f190e03dc1b7c54bbbae1d5d49d35c78c19b63a',
 'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/bootstrap/CommonSetup.java':'06e34b81779f72b35a66cedbce19418eb248786a',
 'common/src/main/resources/assets/kaleidoscope_grilling/blockstates/onion_crop.json':'3769d7a50dfc62a7a2e8bfca918c314ff3ff5a59',
 'common/src/main/resources/data/kaleidoscope_grilling/loot_table/blocks/onion_crop.json':'b96926076396c2a70003aaca65766fcfee9e27d6'
}
def git_blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path):
 req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.17-contract/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 assert git_blob(v)==FILES[path],(path,git_blob(v),FILES[path]);return v
def main():
 crop=fetch(next(p for p in FILES if p.endswith('OnionCropBlock.java'))).decode()
 for token in ('BlockStateProperties.AGE_7','return 7;','ModItems.ONION.get()','super.randomTick(s, l, p, r);'):assert token in crop,token

 drop=fetch(next(p for p in FILES if p.endswith('CropDropHandler.java'))).decode()
 for token in (
  'Blocks.SHORT_GRASS',
  '"kaleidoscope_cookery:straw_hat"',
  '"kaleidoscope_cookery:straw_hat_flower"',
  'ModItems.ONION.get(), 1 + event.getPlayer().getRandom().nextInt(1 + fortune)',
  'nextFloat() < 0.125F'
 ):assert token in drop,token

 items=fetch(next(p for p in FILES if p.endswith('ModItems.java'))).decode()
 assert 'public static final DeferredHolder<Item, Item> ONION =' in items
 assert 'new ItemNameBlockItem(ModBlocks.ONION_CROP.get(), new Item.Properties())' in items

 setup=fetch(next(p for p in FILES if p.endswith('CommonSetup.java'))).decode()
 assert 'ComposterBlock.COMPOSTABLES.put(ModItems.ONION.get(), 0.65F);' in setup

 state=json.loads(fetch(next(p for p in FILES if p.endswith('blockstates/onion_crop.json'))))
 variants=state['variants'];assert len(variants)==8
 for age in range(8):assert f'age={age}' in variants

 loot=json.loads(fetch(next(p for p in FILES if p.endswith('loot_table/blocks/onion_crop.json'))))
 assert len(loot['pools'])==2
 assert loot['pools'][0]['entries'][0]['name']=='kaleidoscope_grilling:onion'
 bonus=loot['pools'][1]
 assert bonus['conditions'][0]['properties']=={'age':'7'}
 fn=bonus['entries'][0]['functions'][0]
 assert fn['function']=='minecraft:apply_bonus'
 assert fn['enchantment']=='minecraft:fortune'
 assert fn['formula']=='minecraft:binomial_with_bonus_count'
 assert fn['parameters']=={'extra':2,'probability':0.5714286}
 print('A2.7.17 pinned Java onion crop/acquisition contract: PASS')
if __name__=='__main__':main()
