"""A UV atlas is usable only when each consuming material enables USE_UV_ANIM."""
import json
from verify_a2858 import main as previous
from verify_a2856 import RP,ROOT
def main():
 previous()
 version=tuple(json.loads((RP.parent/'behavior_pack/manifest.json').read_text())['header']['version'])
 native=version>=(2,8,61)
 if native:
  assert not (RP/'materials/entity.material').exists() and not (RP/'materials/seasoning_atlas.material').exists()
 else:
  path='entity.material' if version>=(2,8,60) else 'seasoning_atlas.material'
  material=json.loads((RP/'materials'/path).read_text())['materials']
  assert material=={'version':'1.0.0','kg_seasoning_atlas:entity_alphatest_one_sided':{'+defines':['USE_UV_ANIM']}}
 placed=json.loads((RP/'entity/a2770_placed_seasoning.entity.json').read_text())['minecraft:client_entity']['description']
 expected='entity_alphatest_one_sided' if native else 'kg_seasoning_atlas'
 assert placed['materials']['layers']==expected
 controllers=json.loads((RP/'render_controllers/a2770_placed.render_controllers.json').read_text())['render_controllers']
 for tint in range(16):assert controllers['controller.render.kg_a2770.pending_'+str(tint)]['materials']==[{'*':'Material.layers'}]
 for name in ['pending_seasoning','empty_seasoning_bottle']:
  d=json.loads((RP/f'attachables/{name}.attachable.json').read_text())['minecraft:attachable']['description']
  assert d['materials']['contents']==expected
 if native:
  from PIL import Image
  count=json.loads((ROOT/'development/gameplay_core/fixtures/a2770/sources.json').read_text())['pending_palette_tiles']
  for filename,prefix,rcfile,rcprefix in [('a2770_placed/seasoning.geo.json','geometry.kg_a2770.pending_','a2770_placed.render_controllers.json','controller.render.kg_a2770.pending_'),('seasoning_held.geo.json','geometry.kg_seasoning.held_','seasoning_held.render_controllers.json','controller.render.kg_seasoning.held_')]:
   geometries={g['description']['identifier']:g for g in json.loads((RP/'models/entity'/filename).read_text())['minecraft:geometry']}
   render=json.loads((RP/'render_controllers'/rcfile).read_text())['render_controllers']
   for tint in range(16):
    rc=render[rcprefix+str(tint)];assert 'uv_anim' not in rc
    assert len(next(iter(rc['arrays']['geometries'].values())))==count
    base=geometries[prefix+str(tint)]['description'];width,height=base['texture_width'],base['texture_height']
    with Image.open(RP/f'textures/a2770_placed/pending_{tint}.png') as image:
     for tile in range(count):
      g=geometries[prefix+str(tint)+'_c'+str(tile)];assert (g['description']['texture_width'],g['description']['texture_height'])==image.size
      x,y=(tile%8)*width,(tile//8)*height
      for bone in g['bones']:
       for cube in bone.get('cubes',[]):
        for face in cube['uv'].values():
         u,v=face['uv'];du,dv=face['uv_size']
         assert x<=min(u,u+du)<=max(u,u+du)<=x+width and y<=min(v,v+dv)<=max(v,v+dv)<=y+height,(tint,tile,face)
  print('All held/placed palette UVs stay inside their selected tile with native materials; client pending')
 else:print('All 32 seasoning atlas layers resolve to a UV-enabled material; human rendering remains pending')
if __name__=='__main__':main()
