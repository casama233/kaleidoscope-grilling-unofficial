"""A UV atlas is usable only when each consuming material enables USE_UV_ANIM."""
import json
from verify_a2858 import main as previous
from verify_a2856 import RP
def main():
 previous()
 material=json.loads((RP/'materials/seasoning_atlas.material').read_text())['materials']
 assert material=={'version':'1.0.0','kg_seasoning_atlas:entity_alphatest_one_sided':{'+defines':['USE_UV_ANIM']}}
 placed=json.loads((RP/'entity/a2770_placed_seasoning.entity.json').read_text())['minecraft:client_entity']['description']
 assert placed['materials']['layers']=='kg_seasoning_atlas'
 controllers=json.loads((RP/'render_controllers/a2770_placed.render_controllers.json').read_text())['render_controllers']
 for tint in range(16):assert controllers['controller.render.kg_a2770.pending_'+str(tint)]['materials']==[{'*':'Material.layers'}]
 for name in ['pending_seasoning','empty_seasoning_bottle']:
  d=json.loads((RP/f'attachables/{name}.attachable.json').read_text())['minecraft:attachable']['description']
  assert d['materials']['contents']=='kg_seasoning_atlas'
 print('All 32 seasoning atlas layers resolve to a UV-enabled material; human rendering remains pending')
if __name__=='__main__':main()
