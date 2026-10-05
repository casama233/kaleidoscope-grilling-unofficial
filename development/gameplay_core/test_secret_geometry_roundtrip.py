"""Every authored food face/rotation/UV is tested without a Minecraft claim."""
from pathlib import Path
import hashlib,json,math,sys,unittest
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];RP=ROOT/'projects/grilling/gameplay_core/resource_pack';sys.path.insert(0,str(ROOT/'tools'))
from secret_skewer_assets import model,COMPLETE_STATES,PARTIAL_STATES,state_slot_cubes,palette_texture
from secret_food_palette import color_at
class SecretGeometryRoundTrip(unittest.TestCase):
 def test_all_source_cells_round_trip_positions_rotations_and_face_uvs(self):
  for state in COMPLETE_STATES+PARTIAL_STATES:
   for slot in range(1 if state in (16,32,48)else 2 if state in PARTIAL_STATES else 3):
    source=[e for e in model(state)['elements']if any('tintindex'in f for f in e['faces'].values())and next(iter(e['faces'].values()))['tintindex']//128==slot]
    cubes=state_slot_cubes(state,slot,True)
    for e,c in zip(source,cubes,strict=True):
     o,size=c['origin'],c['size'];a=[8-o[0]-size[0],o[1]-24,o[2]+8];b=[a[i]+size[i]for i in range(3)]
     for actual,expected in zip(a+b,e['from']+e['to']):self.assertAlmostEqual(actual,expected,places=12)
     self.assertEqual(set(c['uv']),set(e['faces']))
     for face,original in e['faces'].items():
      local=original['tintindex']%128;cell=local%16;side=local//16
      u0,v0=c['uv'][face]['uv'];du,dv=c['uv'][face]['uv_size'];u1,v1=u0+du,v0+dv
      if face in ('up','down'):u0,v0,u1,v1=u1,v1,u0,v0
      actual=[u0-cell*16,v0-side*16,u1-cell*16,v1-side*16]
      for x,y in zip(actual,original['uv']):self.assertAlmostEqual(x,y,places=12)
     rotation=e.get('rotation',{})
     if rotation.get('angle'):
      axis='xyz'.index(rotation['axis']);self.assertEqual(c['rotation'][axis],rotation['angle']*(-1 if axis<2 else 1))
      self.assertEqual(c['pivot'],[8-rotation['origin'][0],rotation['origin'][1]+24,rotation['origin'][2]-8])
     else:self.assertNotIn('rotation',c)
 def test_grill_food_cells_match_held_geometry_without_socket_offset(self):
  world={g['description']['identifier']:g for g in json.loads((RP/'models/entity/grill_display.geo.json').read_text())['minecraft:geometry']}
  for state in COMPLETE_STATES:
   for slot in range(3):
    cubes=state_slot_cubes(state,slot,True)
    for c in cubes:
     c['origin'][1]-=24
     if'pivot'in c:c['pivot'][1]-=24
    actual=world[f'geometry.kg_station.grill.state_{state}_{slot}']['bones'][1]['cubes']
    for a,b in zip(actual,cubes,strict=True):
     for x,y in zip(a['origin'],b['origin']):self.assertAlmostEqual(x,y,places=12)
     self.assertEqual(a['uv'],b['uv']);self.assertEqual(a['size'],b['size']);self.assertEqual(a.get('rotation'),b.get('rotation'))
 def test_representative_atlases_keep_white_concrete_texel_variation_and_exact_tint(self):
  proof=json.loads((ROOT/'development/gameplay_core/fixtures/secret-food-palettes.json').read_text());source={r['id']:r for r in proof['items']}
  white=Image.open(ROOT/'development/gameplay_core/fixtures/java-secret-skewer-9a1acdab/assets/minecraft/textures/block/white_concrete.png').convert('RGBA')
  for identifier in ('minecraft:apple','minecraft:carrot','minecraft:beef','minecraft:cooked_beef'):
   row=source[identifier];self.assertEqual(row['source']['kind'],'official_java_1.20.1_particle_sprite')
   for style in range(7):
    atlas=Image.open(RP/(palette_texture(row['index'],style)+'.png')).convert('RGBA');self.assertEqual(atlas.size,(256,96))
    for face in range(6):
     for cell in range(16):
      color=color_at(row['palette'],face,cell,4 if style==6 else style,style==6);factors=[color>>16&255,color>>8&255,color&255]
      for xy in ((0,0),(4,8),(15,15)):
       w=white.getpixel(xy);expected=tuple((w[i]*factors[i]+127)//255 for i in range(3))+(w[3],)
       self.assertEqual(atlas.getpixel((cell*16+xy[0],face*16+xy[1])),expected)
if __name__=='__main__':unittest.main()
