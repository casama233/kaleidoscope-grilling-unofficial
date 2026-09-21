from __future__ import annotations
import hashlib,json,urllib.request

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
FILES={
 'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/world/SweetPotatoCropBlock.java':'1c40e7e39e6940825414564190c96e92a43cc1b2',
 'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/world/CropDropHandler.java':'36a58893c4788626a6b5a610b2a230fd709b4ece',
 'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/registry/ModItems.java':'6f190e03dc1b7c54bbbae1d5d49d35c78c19b63a',
 'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/registry/ModBlocks.java':'69f91d7c18ecfa14c206b910d2d4e1d92ce9f6d0',
 'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/bootstrap/CommonSetup.java':'06e34b81779f72b35a66cedbce19418eb248786a',
 'common/src/main/resources/assets/kaleidoscope_grilling/blockstates/sweet_potato_crop.json':'046feabc10ff69d45d52472a19ecc827e57375eb',
 'common/src/main/resources/data/kaleidoscope_grilling/loot_table/blocks/sweet_potato_crop.json':'d56a547eb8ccd3c12cffe51bed647b6204f2dbd0'
}
def git_blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path):
 req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.19-contract/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 assert git_blob(v)==FILES[path],(path,git_blob(v),FILES[path]);return v
def main():
 crop=fetch(next(p for p in FILES if p.endswith('SweetPotatoCropBlock.java'))).decode()
 for token in ('BlockStateProperties.AGE_7','return 7;','ModItems.SWEET_POTATO.get()','super.randomTick(s, l, p, r);'):assert token in crop,token

 items=fetch(next(p for p in FILES if p.endswith('ModItems.java'))).decode()
 sweet=items.index('public static final DeferredHolder<Item, Item> SWEET_POTATO =')
 chunk=items[sweet:sweet+700]
 for token in ('new ItemNameBlockItem(','ModBlocks.SWEET_POTATO_CROP.get()','.nutrition(3)','.saturationModifier(0.1F)'):assert token in chunk,token

 blocks=fetch(next(p for p in FILES if p.endswith('ModBlocks.java'))).decode()
 sweetb=blocks.index('public static final DeferredHolder<Block, Block> SWEET_POTATO_CROP =')
 bchunk=blocks[sweetb:sweetb+500]
 assert 'BlockBehaviour.Properties.ofLegacyCopy(Blocks.BEETROOTS)' in bchunk
 for token in ('.noCollission()','.randomTicks()','.instabreak()','.noOcclusion()'):assert token in bchunk,token

 setup=fetch(next(p for p in FILES if p.endswith('CommonSetup.java'))).decode()
 assert 'ComposterBlock.COMPOSTABLES.put(ModItems.SWEET_POTATO.get(), 0.65F);' in setup

 drop=fetch(next(p for p in FILES if p.endswith('CropDropHandler.java'))).decode()
 c=drop.index('ModItems.CANOLA_SEEDS.get()')
 s=drop.index('ModItems.SWEET_POTATO.get()')
 o=drop.index('ModItems.ONION.get()')
 assert c<s<o,(c,s,o)
 assert drop.count('nextFloat() < 0.125F')==1
 assert 'ModItems.SWEET_POTATO.get(), 1 + event.getPlayer().getRandom().nextInt(1 + fortune)' in drop

 state=json.loads(fetch(next(p for p in FILES if p.endswith('blockstates/sweet_potato_crop.json'))))
 variants=state['variants'];assert len(variants)==8
 for age in range(8):assert f'age={age}' in variants

 loot=json.loads(fetch(next(p for p in FILES if p.endswith('loot_table/blocks/sweet_potato_crop.json'))))
 assert len(loot['pools'])==2
 assert loot['pools'][0]['entries'][0]['name']=='kaleidoscope_grilling:sweet_potato'
 bonus=loot['pools'][1]
 assert bonus['conditions'][0]['properties']=={'age':'7'}
 entry=bonus['entries'][0];assert entry['name']=='kaleidoscope_grilling:sweet_potato'
 funcs=entry['functions']
 assert funcs[0]=={'function':'minecraft:set_count','count':2}
 assert funcs[1]['function']=='minecraft:apply_bonus'
 assert funcs[1]['enchantment']=='minecraft:fortune'
 assert funcs[1]['formula']=='minecraft:binomial_with_bonus_count'
 assert funcs[1]['parameters']=={'extra':3,'probability':0.5714286}
 print('A2.7.19 pinned Java sweet potato crop/acquisition contract: PASS')
if __name__=='__main__':main()
