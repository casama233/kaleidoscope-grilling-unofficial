from __future__ import annotations
import hashlib,urllib.request

URL='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/oil/OilFillingHandler.java'
EXPECTED_BLOB='8f9738b94ed119093f3f8552dc7e76c58fa08bc4'

def git_blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 req=urllib.request.Request(URL,headers={'User-Agent':'Grilling-A2.7.37-contract/1'})
 with urllib.request.urlopen(req,timeout=90) as r:data=r.read()
 assert git_blob(data)==EXPECTED_BLOB,(git_blob(data),EXPECTED_BLOB)
 s=data.decode('utf-8')
 for token in (
  'public static void onRightClickItem(PlayerInteractEvent.RightClickItem event)',
  'if (event.getHand() != InteractionHand.MAIN_HAND) return;',
  'ItemStack bucket = event.getEntity().getMainHandItem();',
  'ItemStack pot = event.getEntity().getOffhandItem();',
  'if (type == null || !OilPotCompat.isOilPot(pot)) return;',
  'event.setCanceled(true);',
  'count > OilPotCompat.FLUID_CAPACITY - 8',
  '(current.isEmpty() ? count > 0 : !current.equals(type))',
  'OilPotCompat.fill(pot, type, 8);',
  'new ItemStack(Items.BUCKET)',
  'if (!event.getEntity().getAbilities().instabuild)',
 ):
  assert token in s,token
 print('A2.7.37 pinned Java OilFillingHandler RightClickItem contract: PASS')
if __name__=='__main__':main()
