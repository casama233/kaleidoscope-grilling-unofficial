"""Bake source face tint onto the actual white-concrete texture.

Inputs are reviewed 16-color samples, not copied external food artwork. The
original per-face UV rectangles remain inside each 16×16 tinted sprite tile.
"""
from pathlib import Path
import argparse,hashlib,io,json
from PIL import Image
from secret_food_palette import color_at
from secret_skewer_assets import FIX,ROOT,ASSET,pinned,palette_texture
RP=ROOT/'projects/grilling/gameplay_core/resource_pack'
SAMPLES=ROOT/'development/gameplay_core/fixtures/secret-food-palettes.json'

def build():
 proof=json.loads(SAMPLES.read_text());catalog=json.loads((ROOT/'development/gameplay_core/fixtures/secret-visual-catalog.json').read_text())['items']
 assert [r['id'] for r in proof['items']]==[r['id'] for r in catalog]
 white_path=FIX/'assets/minecraft/textures/block/white_concrete.png';raw=white_path.read_bytes()
 assert hashlib.sha256(raw).hexdigest()==proof['base_texture']['sha256']
 white=Image.open(io.BytesIO(raw)).convert('RGBA');assert white.size==(16,16)
 output={RP/'textures/secret_skewer_stick.png':pinned(ASSET+'textures/item/secret_skewer_stick.png')}
 for index,row in enumerate(proof['items'],1):
  assert len(row['palette'])==16
  for style in range(7):
   atlas=Image.new('RGBA',(256,96))
   tiles={}
   for face in range(6):
    for cell in range(16):
     color=color_at(row['palette'],face,cell,4 if style==6 else style,style==6)
     if color not in tiles:
      factors=[color>>16&255,color>>8&255,color&255]
      channels=[white.getchannel(i).point([(v*f+127)//255 for v in range(256)]) for i,f in enumerate(factors)]
      tiles[color]=Image.merge('RGBA',(*channels,white.getchannel('A')))
     atlas.paste(tiles[color],(cell*16,face*16))
   stream=io.BytesIO();atlas.save(stream,format='PNG',compress_level=9)
   output[RP/(palette_texture(index,style)+'.png')]=stream.getvalue()
 return output

def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();output=build()
 for path,data in output.items():
  if a.check:assert path.read_bytes()==data,path
  else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
 print(f'{len(output)-1} ingredient palette/stage atlases + exact secret shaft; source lighting/native acceptance separate')
if __name__=='__main__':main()
