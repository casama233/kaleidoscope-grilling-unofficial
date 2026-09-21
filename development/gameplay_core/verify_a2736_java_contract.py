from __future__ import annotations
import hashlib,urllib.request

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/'
FILES={
 'mixin/OilPotBlockEntityMixin.java':('bace9e1dbf4beeb6bc7202c317ed8d302d2286cc',(
  'private String grilling$oilType = "";','OilPotCompat.capacity(grilling$oilType)','tag.putString("GrillingOilType", grilling$oilType);')),
 'mixin/OilPotBlockMixin.java':('7d76cdb8e47203b42ae66c0aef99f3c7fc1d1800',(
  'access.grilling$setOilType(OilPotCompat.getType(stack));','OilPotCompat.setType(stack, access.grilling$getOilType())','held.isEmpty() || OilPotCompat.isCookeryFat(held)')),
 'oil/OilFillingHandler.java':('8f9738b94ed119093f3f8552dc7e76c58fa08bc4',(
  'pot.grilling$setOilCount(pot.grilling$getOilCount() + 8);','OilPotCompat.FLUID_CAPACITY - 8','!current.equals(type)')),
}
def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def main():
 for path,(sha,tokens) in FILES.items():
  req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.36-contract/1'})
  with urllib.request.urlopen(req,timeout=90) as r:data=r.read()
  assert blob(data)==sha,(path,blob(data),sha);s=data.decode('utf-8')
  for token in tokens:assert token in s,(path,token)
 print('A2.7.36 pinned Java typed Oil Pot block contract: PASS')
if __name__=='__main__':main()
