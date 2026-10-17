"""Rack item model selection, preserving existing skewer/gameplay regressions."""
from pathlib import Path
import json
from PIL import Image
from verify_a2831 import main as baseline
ROOT=Path(__file__).resolve().parents[2];RP=ROOT/'projects/grilling/gameplay_core/resource_pack';BP=ROOT/'projects/grilling/gameplay_core/behavior_pack'
def main():
 baseline()
 assert not (RP/'attachables/advanced_rack.attachable.json').exists(),'Java generated rack must not use world-model hand override'
 item=json.loads((BP/'items/advanced_rack.json').read_text())['minecraft:item'];c=item['components']
 assert c['minecraft:icon']=={'textures':{'default':'advanced_rack'}}
 assert c['minecraft:block_placer']=={'block':'kaleidoscope_grilling:advanced_rack_block'}
 assert c['minecraft:max_stack_size']==1
 assert Image.open(RP/'textures/items/advanced_rack.png').convert('RGBA').tobytes()==Image.open(Path(__file__).parent/'fixtures/a283/advanced_rack.png').convert('RGBA').tobytes()
 print('A2.8.32 rack generated-item route PASS; native client acceptance pending')
if __name__=='__main__':main()
