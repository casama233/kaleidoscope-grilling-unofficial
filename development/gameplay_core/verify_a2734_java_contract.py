from __future__ import annotations
import hashlib,urllib.request

URL='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/oil/OilPotCompat.java'
EXPECTED_BLOB='4264ab947a4222784151fbd50ae84a1a8037d491'

def git_blob(v):
 return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 req=urllib.request.Request(URL,headers={'User-Agent':'Grilling-A2.7.34-contract/1'})
 with urllib.request.urlopen(req,timeout=90) as r:data=r.read()
 assert git_blob(data)==EXPECTED_BLOB,(git_blob(data),EXPECTED_BLOB)
 s=data.decode('utf-8')
 for token in (
  'public static final int FAT_CAPACITY = 256;',
  'public static final int FLUID_CAPACITY = 64;',
  'return count == null ? 0 : Math.min(capacity(getType(stack)), count);',
  'return type == null || type.isEmpty() ? FAT_CAPACITY : FLUID_CAPACITY;',
  'if (remaining == 0) setType(stack, "");',
  'stack.set(countType(), Math.min(FLUID_CAPACITY, getCount(stack) + points));',
 ):
  assert token in s,token
 print('A2.7.34 pinned Java OilPotCompat contract: PASS')

if __name__=='__main__':
 main()
