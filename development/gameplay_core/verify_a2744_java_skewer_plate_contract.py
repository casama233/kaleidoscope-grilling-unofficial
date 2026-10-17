from __future__ import annotations
import hashlib,urllib.request

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
FILES={
 'plate_provider':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/compat/jade/SkewerPlateProvider.java',
  'e230917adb32d8ae5d8b0837350ddb5bef7f4c98',
  (
   'SkewerPlateBlockEntity plate',
   'plate.copySkewers()',
   '"jade.kaleidoscope_grilling.skewer_plate.count"',
   '"jade.kaleidoscope_grilling.skewer_plate.empty"',
   '"jade.kaleidoscope_grilling.skewer_plate.take"',
   '"jade.kaleidoscope_grilling.skewer_plate.pack"',
  )
 ),
 'plate_entity':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/skewer/SkewerPlateBlockEntity.java',
  'b50903f3dcd6069d5b5b13133abc0d52eaf66dfd',
  (
   'public static final int CAPACITY = 5;',
   'public boolean add(ItemStack source, boolean creative)',
   'public ItemStack removeLast()',
   'public List<ItemStack> copySkewers()',
  )
 ),
}

def git_blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 for name,(path,expected,tokens) in FILES.items():
  req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.44-contract/1'})
  with urllib.request.urlopen(req,timeout=90) as r:data=r.read()
  actual=git_blob(data);assert actual==expected,(name,actual,expected)
  s=data.decode('utf-8')
  for token in tokens:assert token in s,(name,token)
 print('A2.7.44 pinned Java Skewer Plate HUD contract: PASS')

if __name__=='__main__':main()
