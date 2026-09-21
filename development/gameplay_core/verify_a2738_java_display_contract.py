from __future__ import annotations
import hashlib,urllib.request

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
FILES={
 'oil_compat':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/oil/OilPotCompat.java',
  '4264ab947a4222784151fbd50ae84a1a8037d491',
  (
   'public static final int FAT_CAPACITY = 256;',
   'public static final int FLUID_CAPACITY = 64;',
   'Component.translatable("item.kaleidoscope_grilling.oil_pot." + type)',
  )
 ),
 'block_mixin':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/mixin/OilPotBlockMixin.java',
  '7d76cdb8e47203b42ae66c0aef99f3c7fc1d1800',
  (
   'builder.add(OilPotVisualState.OIL_TYPE);',
   'access.grilling$setOilType(OilPotCompat.getType(stack));',
   'OilPotCompat.setType(stack, access.grilling$getOilType())',
   'OilPotCompat.setType(cir.getReturnValue(), access.grilling$getOilType());',
  )
 ),
 'client_setup':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/client/ClientSetup.java',
  '227d21a500f284cec1f2061ffa935457051e4596',
  (
   'private static final ResourceLocation OIL_TYPE =',
   'case "canola" -> 0.25F;',
   'case "secret_chili" -> 0.5F;',
   'case "premium_chili" -> 0.75F;',
  )
 ),
 'oil_hud':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/oil/OilPotHud.java',
  '40c6f7e19c50d3081a16c8c93b3cfc06f0db532d',
  (
   'minecraft.hitResult instanceof BlockHitResult hit',
   'hud.kaleidoscope_grilling.oil_pot.title',
   'hud.kaleidoscope_grilling.oil_pot.capacity',
   'OilPotCompat.capacity(type)',
  )
 ),
}

def git_blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 for name,(path,expected,tokens) in FILES.items():
  req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.38-contract/1'})
  with urllib.request.urlopen(req,timeout=90) as r:data=r.read()
  actual=git_blob(data);assert actual==expected,(name,actual,expected)
  s=data.decode('utf-8')
  for token in tokens:assert token in s,(name,token)
 print('A2.7.38 pinned Java typed-oil display/contract audit: PASS')

if __name__=='__main__':main()
