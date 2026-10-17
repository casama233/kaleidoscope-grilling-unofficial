from __future__ import annotations
import hashlib,urllib.request

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
FILES={
 'machine_hud':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/client/MachineHud.java',
  '2156ed061b5843618d6929ba5e5aa92aff0688a5',
  (
   'else if (blockEntity instanceof BigVatBlockEntity vat) drawVat',
   'private static void drawVat',
   'Component.translatable("hud.kaleidoscope_grilling.vat.title")',
   'vat.fluid().isEmpty()',
   'vat.fluid().getHoverName()',
   '"hud.kaleidoscope_grilling.vat.capacity"',
   'BigVatBlockEntity.BUCKET_VOLUME',
   'BigVatBlockEntity.CAPACITY_BUCKETS',
   'Component.translatable("hud.kaleidoscope_grilling.vat.accepts")',
  )
 ),
 'big_vat_entity':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/oil/BigVatBlockEntity.java',
  '66f372ba808a9373d06f6cf4e7246f4911139689',
  (
   'public static final int CAPACITY_BUCKETS = 8;',
   'public static final int CAPACITY = CAPACITY_BUCKETS * BUCKET_VOLUME;',
   'private final FluidTank tank =',
   'public IFluidHandler fluidHandler()',
   'public FluidStack fluid()',
   'public int buckets()',
   'public boolean canInsert(Fluid fluid, int amount)',
  )
 ),
}

def git_blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 for name,(path,expected,tokens) in FILES.items():
  req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.42-contract/1'})
  with urllib.request.urlopen(req,timeout=90) as r:data=r.read()
  actual=git_blob(data);assert actual==expected,(name,actual,expected)
  s=data.decode('utf-8')
  for token in tokens:assert token in s,(name,token)
 print('A2.7.42 pinned Java Big Vat HUD contract: PASS')

if __name__=='__main__':main()
