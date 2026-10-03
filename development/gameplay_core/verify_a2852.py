"""Native-use profile release; source checks remain distinct from client proof."""
from pathlib import Path
import json,subprocess,sys
from verify_a2851 import main as previous
ROOT=Path(__file__).resolve().parents[2];BP=ROOT/'projects/grilling/gameplay_core/behavior_pack';RP=ROOT/'projects/grilling/gameplay_core/resource_pack'
def main():
 previous()
 subprocess.run([sys.executable,str(ROOT/'tools/build_native_eating_variants.py'),'--check'],check=True)
 subprocess.run([sys.executable,str(ROOT/'tools/build_eating_motion.py'),'--check'],check=True)
 variants=list((BP/'items').glob('*_java_three_alt.json'))
 assert len(variants)==22,len(variants)
 for p in variants:
  alt=json.loads(p.read_text())['minecraft:item'];base=json.loads(p.with_name(p.name.replace('_java_three_alt','')).read_text())['minecraft:item']
  a=dict(alt['components']);b=dict(base['components']);a['minecraft:use_modifiers']=dict(a['minecraft:use_modifiers']);b['minecraft:use_modifiers']=dict(b['minecraft:use_modifiers'])
  assert a['minecraft:use_modifiers'].pop('use_duration')==4.5,p
  assert b['minecraft:use_modifiers'].pop('use_duration')==5,p
  assert a==b,p
  assert 'menu_category' not in alt['description'],p
  assert alt['components']['minecraft:display_name']==base['components']['minecraft:display_name'],p
 print('2.8.52 canonical native 90/100 tick profile variants and authored item-matrix conversion; client pending')
if __name__=='__main__':main()
