from __future__ import annotations
import hashlib,urllib.request

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
FILES={
 'leaves':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/world/PepperLeavesBlock.java',
  '886ddfc434d38f3df6c440b8ea16c5b7b9569af4',
  (
   'BooleanProperty.create("has_pepper")',
   'random.nextInt(20) == 0',
   'new ItemStack(ModItems.SICHUAN_PEPPER.get(), 1 + level.random.nextInt(2))',
   'STING_INTERVAL_TICKS = 20',
   'entity.makeStuckInBlock(state, new Vec3(0.8, 0.75, 0.8))',
   'entity.getType() == EntityType.FOX',
   'entity.getType() == EntityType.BEE',
  )
 ),
 'sapling':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/world/PepperSaplingBlock.java',
  'a2f89067244663d237e37417d371c4fe3df3bf22',
  (
   'IntegerProperty.create("stage", 0, 1)',
   'level.random.nextFloat() < 0.45F',
   'level.getMaxLocalRawBrightness(pos.above()) >= 9',
   'random.nextInt(7) == 0',
   'ModFeatures.PEPPER_TREE',
  )
 ),
 'tree':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/world/PepperTreeFeature.java',
  'e71c497fcb1ed662f71bbdce45f86a0b41608090',
  (
   'int height = 2 + random.nextInt(2);',
   'for (int y = 0; y <= trunkTop; y++)',
   'for (int dx = -1; dx <= 1; dx++)',
   'int crownY = origin.getY() + trunkTop + 1;',
   'random.nextInt(4) == 0',
  )
 ),
 'log':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/world/PepperLogBlock.java',
  '60681145e5faa97ea2d4ac9100731dfe8cc6aeed',
  ('RotatedPillarBlock','Blocks.OAK_LOG')
 ),
 'strip':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/world/StrippingHandler.java',
  'e887933c46ff8aeb2a54e526e76f669096122b35',
  ('ItemAbilities.AXE_STRIP','Blocks.STRIPPED_OAK_LOG','RotatedPillarBlock.AXIS')
 ),
}

def git_blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 for name,(path,expected,tokens) in FILES.items():
  req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.48-contract/1'})
  with urllib.request.urlopen(req,timeout=90) as r:data=r.read()
  actual=git_blob(data);assert actual==expected,(name,actual,expected)
  s=data.decode('utf-8')
  for token in tokens:assert token in s,(name,token)
 print('A2.7.48 pinned Java Pepper Tree lifecycle contract: PASS')

if __name__=='__main__':main()
