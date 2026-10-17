from __future__ import annotations
import hashlib,json,urllib.request

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
FILES={
 'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/world/CanolaCropBlock.java':'9b728ebc1961a8527d2b36b97b90dc2c6903b5fb',
 'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/world/CropDropHandler.java':'36a58893c4788626a6b5a610b2a230fd709b4ece',
 'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/registry/ModItems.java':'6f190e03dc1b7c54bbbae1d5d49d35c78c19b63a',
 'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/bootstrap/CommonSetup.java':'06e34b81779f72b35a66cedbce19418eb248786a',
 'common/src/main/resources/assets/kaleidoscope_grilling/blockstates/canola_crop.json':'25a57e64eeb2b7635e9075578ae121d1c4719a17',
 'common/src/main/resources/data/kaleidoscope_grilling/loot_table/blocks/canola_crop.json':'6e4643a2b44e73add93b4cb674adc2489eacfa70'
}
def git_blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path):
 req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.15-contract/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 assert git_blob(v)==FILES[path],(path,git_blob(v),FILES[path]);return v
def main():
 crop=fetch(next(p for p in FILES if p.endswith('CanolaCropBlock.java'))).decode()
 for token in ('BlockStateProperties.AGE_7','return 7;','ModItems.CANOLA_SEEDS.get()','super.randomTick(s, l, p, r);'):assert token in crop,token

 drop=fetch(next(p for p in FILES if p.endswith('CropDropHandler.java'))).decode()
 for token in (
  'Blocks.SHORT_GRASS',
  '"kaleidoscope_cookery:straw_hat"',
  '"kaleidoscope_cookery:straw_hat_flower"',
  'ModItems.CANOLA_SEEDS.get(), 1 + event.getPlayer().getRandom().nextInt(1 + fortune)',
  'nextFloat() < 0.125F'
 ):assert token in drop,token

 items=fetch(next(p for p in FILES if p.endswith('ModItems.java'))).decode()
 assert 'CANOLA_SEEDS =' in items
 assert '"canola_seeds"' in items
 assert 'new ItemNameBlockItem(ModBlocks.CANOLA_CROP.get(), new Item.Properties())' in items

 setup=fetch(next(p for p in FILES if p.endswith('CommonSetup.java'))).decode()
 assert 'ComposterBlock.COMPOSTABLES.put(ModItems.CANOLA_SEEDS.get(), 0.30F);' in setup

 state=json.loads(fetch(next(p for p in FILES if p.endswith('blockstates/canola_crop.json'))))
 variants=state['variants'];assert len(variants)==8
 for age in range(8):assert f'age={age}' in variants

 loot=json.loads(fetch(next(p for p in FILES if p.endswith('loot_table/blocks/canola_crop.json'))))
 assert len(loot['pools'])==2
 assert loot['pools'][0]['entries'][0]['name']=='kaleidoscope_grilling:canola_seeds'
 bonus=loot['pools'][1]
 assert bonus['conditions'][0]['properties']=={'age':'7'}
 fn=bonus['entries'][0]['functions'][0]
 assert fn['function']=='minecraft:apply_bonus' and fn['enchantment']=='minecraft:fortune'
 assert fn['formula']=='minecraft:binomial_with_bonus_count'
 assert fn['parameters']=={'extra':2,'probability':0.5714286}
 print('A2.7.15 pinned Java canola crop/acquisition contract: PASS')
if __name__=='__main__':main()
