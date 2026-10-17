from __future__ import annotations
import hashlib,urllib.request

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
FILES={
 'machine_hud':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/client/MachineHud.java',
  '2156ed061b5843618d6929ba5e5aa92aff0688a5',
  (
   'private static void drawPress',
   '"hud.kaleidoscope_grilling.press.cakes", press.cakes(), OilPressBlockEntity.MAX_CAKES',
   '"hud.kaleidoscope_grilling.press.progress"',
   '"hud.kaleidoscope_grilling.press.vat.none"',
   '"hud.kaleidoscope_grilling.press.vat.wrong"',
   '"hud.kaleidoscope_grilling.press.vat.full"',
   '"hud.kaleidoscope_grilling.press.vat.found"',
  )
 ),
 'jade_press':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/compat/jade/OilPressProvider.java',
  '356e10a5ca536d91e3770c4e6389589214da0813',
  (
   'press.progress() > 0 || press.waitingForContainer() ? "progress" : "cakes"',
   'OilPressContainerApi.probeNearby',
   '"jade.kaleidoscope_grilling.press.vat.none"',
   '"jade.kaleidoscope_grilling.press.vat.incompatible"',
  )
 ),
 'press_entity':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/oil/OilPressBlockEntity.java',
  'c7447be63135f52e15646587226339b3d8036738',
  (
   'public static final int MAX_CAKES = 4;',
   'public static final int REQUIRED_PROGRESS = 16;',
   'public static final int ANVIL_PROGRESS = 4;',
   'public static final int PRESS_COOLDOWN_TICKS = 10;',
   'public boolean waitingForContainer()',
  )
 ),
}

def git_blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 for name,(path,expected,tokens) in FILES.items():
  req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.41-contract/1'})
  with urllib.request.urlopen(req,timeout=90) as r:data=r.read()
  actual=git_blob(data);assert actual==expected,(name,actual,expected)
  s=data.decode('utf-8')
  for token in tokens:assert token in s,(name,token)
 print('A2.7.41 pinned Java oil-press HUD contract: PASS')

if __name__=='__main__':main()
