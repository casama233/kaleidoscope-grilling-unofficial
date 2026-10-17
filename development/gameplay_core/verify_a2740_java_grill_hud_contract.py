from __future__ import annotations
import hashlib,urllib.request

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
FILES={
 'machine_hud':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/client/MachineHud.java',
  '2156ed061b5843618d6929ba5e5aa92aff0688a5',
  (
   'Component.translatable("hud.kaleidoscope_grilling.grill.title")',
   'int max = grill.getPhase() <= 2 ? 800 : 400;',
   '"hud.kaleidoscope_grilling.grill.timer", Math.min(grill.getPhaseTicks(), max), max',
   '"hud.kaleidoscope_grilling.grill.flips", grill.getFlips(), 4',
   '"hud.kaleidoscope_grilling.grill.seasoning." + (grill.isSeasoned() ? "added" : "none")',
   'Component.translatable("message.kaleidoscope_grilling.grill_ready_to_take")',
  )
 ),
 'jade_grill':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/compat/jade/GrillProvider.java',
  '01eff3e5fbba33d3303536df2633771c2dc15baa',
  (
   '"jade.kaleidoscope_grilling.grill.need_heat"',
   '"jade.kaleidoscope_grilling.grill.empty"',
   '"jade.kaleidoscope_grilling.grill.need_oil"',
   '"jade.kaleidoscope_grilling.grill.flipping"',
   '"jade.kaleidoscope_grilling.grill.need_flip"',
   '"jade.kaleidoscope_grilling.grill.need_seasoning"',
   '"jade.kaleidoscope_grilling.grill.ready"',
   '"jade.kaleidoscope_grilling.grill.burning"',
  )
 ),
 'grill_entity':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/grill/GrillBlockEntity.java',
  '6f12af87af8837dc2fec034efd6076bea49637bc',
  (
   'private static final int FINISHED_TICKS = 800;',
   'private static final int BURNT_TICKS = 400;',
   'if (flips >= 4) {',
   'flipCooldown = 20;',
   'public int occupiedSlots()',
  )
 ),
}

def git_blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 for name,(path,expected,tokens) in FILES.items():
  req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.40-contract/1'})
  with urllib.request.urlopen(req,timeout=90) as r:data=r.read()
  actual=git_blob(data);assert actual==expected,(name,actual,expected)
  s=data.decode('utf-8')
  for token in tokens:assert token in s,(name,token)
 print('A2.7.40 pinned Java grill HUD contract: PASS')

if __name__=='__main__':main()
