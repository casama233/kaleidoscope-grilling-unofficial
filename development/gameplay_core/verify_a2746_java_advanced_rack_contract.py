from __future__ import annotations
import hashlib,urllib.request

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
FILES={
 'rack_entity':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/rack/AdvancedRackBlockEntity.java',
  'ac52b331e020d2020964da754c8fdeec47cd1c52',
  (
   'public static final int COMPARTMENT_COUNT = 9;',
   'private NonNullList<ItemStack> items = NonNullList.withSize(COMPARTMENT_COUNT, ItemStack.EMPTY);',
   'private NonNullList<ItemStack> filters = NonNullList.withSize(COMPARTMENT_COUNT, ItemStack.EMPTY);',
   'if (!AdvancedRackCompatApi.canPlace(slot, stack)) return false;',
   'if (!stack.isEmpty() && filters.get(slot).isEmpty()) filters.set(slot, stack.copyWithCount(1));',
   'if (slot < 0 || slot >= COMPARTMENT_COUNT || !getItem(slot).isEmpty()) return;',
   'for (int slot = 0; slot < 5; slot++) if (!items.get(slot).isEmpty()) occupied++;',
   'if (OilPotCompat.isOilPot(first) && OilPotCompat.isOilPot(second))',
   'if (isSeasoningBottle(first) && isSeasoningBottle(second)) return true;',
  )
 ),
 'rack_compat':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/AdvancedRackCompatApi.java',
  'a27032bf1c8e852f0afdf584fc00d9b1daadf828',
  (
   '"advanced_rack_seasonings"',
   '"advanced_rack_tools"',
   'slot < 5 ? isSeasoningItem(stack) : isToolItem(stack)',
  )
 ),
 'rack_block':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/rack/AdvancedRackBlock.java',
  'bcbd48401f08534cba33bdda96c6d37c29efead1',
  (
   'IntegerProperty.create("spice_level", 0, 4)',
   'private static final VoxelShape NORTH = Block.box(1, 5, 11, 15, 14, 16);',
   'private static final VoxelShape SOUTH = Block.box(1, 5, 0, 15, 14, 5);',
  )
 ),
}

def git_blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 for name,(path,expected,tokens) in FILES.items():
  req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.46-contract/1'})
  with urllib.request.urlopen(req,timeout=90) as r:data=r.read()
  actual=git_blob(data);assert actual==expected,(name,actual,expected)
  s=data.decode('utf-8')
  for token in tokens:assert token in s,(name,token)
 print('A2.7.46 pinned Java Advanced Rack foundation contract: PASS')

if __name__=='__main__':main()
