"""Seasoning data/source/dispatch guards; no simulated player or client proof."""
from pathlib import Path
import hashlib,json,math,re,subprocess,sys
from verify_a2855 import main as previous
from verify_a287 import expression
ROOT=Path(__file__).resolve().parents[2];BP=ROOT/'projects/grilling/gameplay_core/behavior_pack';RP=ROOT/'projects/grilling/gameplay_core/resource_pack'
def main():
 previous()
 subprocess.run([sys.executable,str(ROOT/'tools/build_seasoning_held.py'),'--check'],check=True)
 fixture=json.loads((ROOT/'development/gameplay_core/fixtures/java-seasoning-motion-1.1.1.json').read_text())
 for row in fixture['source_files'].values():assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256']
 java=(ROOT/fixture['source_files']['SeasoningAnimation.java']['path']).read_text();assert 'DURATION_TICKS = 10' in java
 data=(BP/'scripts/a2770_placed_visual_data.js').read_text();colors=json.loads(re.search(r'INGREDIENT_COLORS=Object.freeze\((.*)\);',data).group(1))
 accepted=re.findall(r"'([^']+)':'(?:speed|strength|duration|totem|vitality|numbness|base)'",(BP/'scripts/a2743_seasoning_contract_core.js').read_text())
 assert len(accepted)==8 and all(x in colors and len(colors[x])==2 for x in accepted)
 assert len({tuple(colors[x]) for x in accepted})==8
 for name in ['pending_seasoning','special_seasoning','empty_seasoning_bottle']:
  d=json.loads((RP/f'attachables/{name}.attachable.json').read_text())['minecraft:attachable']['description']
  for first in [0,1]:
   for slot,hand,code in [('main_hand','right',1),('off_hand','left',2)]:
    for phase in range(11):
     for active in [0,1,2]:
      for pending in [0,1,2]:
       rows=[k for row in d['scripts']['animate'] for k,e in row.items() if expression(e,first,slot,hand+'item',True,season_phase=phase,season_hand=active,pending_hand=pending)]
       expected='tp_'+hand if not first else 'season_'+hand if phase and active==code else 'shake_'+hand if name=='pending_seasoning' and pending==code else 'fp_'+hand
       assert rows==[expected],(name,first,slot,phase,active,pending,rows)
 anim=json.loads((RP/'animations/seasoning_held.animation.json').read_text())['animations']
 for key,a in anim.items():
  if '.sprinkle.' in key:assert a['animation_length']==.5 and not a['loop']
  for curve in ['position','rotation']:
   assert all(math.isfinite(v) for vector in a['bones']['grip'][curve].values() for v in vector)
 print('All eight seasoning colors, ordered held layers, exclusive hand dispatch and Java 10-tick motion PASS; client pending')
if __name__=='__main__':main()
