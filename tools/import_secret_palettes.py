"""Import reviewed, source-attributed palette samples without copying food packs.

Requires explicit local source roots. Ordinary builds use only committed samples.
Vanilla uses Java particle sprites; Cookery samples its reviewed public Bedrock
item sprite (Java particle-model parity remains unverified for that source).
"""
from pathlib import Path
import argparse,hashlib,io,json,shutil
from PIL import Image
from secret_food_palette import sample_grid
from secret_skewer_assets import ROOT,FIX

def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--vanilla',type=Path,required=True);p.add_argument('--cookery-rp',type=Path,required=True);p.add_argument('--grilling',type=Path,required=True);a=p.parse_args()
 catalog=json.loads((ROOT/'development/gameplay_core/fixtures/secret-visual-catalog.json').read_text())['items']
 vanilla=json.loads((a.vanilla/'particle-sprite-manifest.json').read_text());items=vanilla.get('items',vanilla)
 if isinstance(items,list):items={r['id']:r for r in items}
 grilling=json.loads((a.grilling/'particle-sprite-manifest.json').read_text());grill_items={r['id']:r for r in grilling['items']};grill_files={r['path']:r for r in grilling['files']}
 rows=[]
 for index,row in enumerate(catalog,1):
  identifier=row['id'];origin={}
  if identifier.startswith('minecraft:'):
   entry=items[identifier];path=a.vanilla/entry['texture_path'];origin={'kind':'official_java_1.20.1_particle_sprite','sprite':entry['particle_sprite'] if 'particle_sprite'in entry else entry.get('sprite'),'source_path':entry['texture_path']}
  elif identifier.startswith('kaleidoscope_cookery:'):
   path=a.cookery_rp/(row['texture']+'.png');origin={'kind':'reviewed_cookery_1.0.8_bedrock_public_sprite','source_path':row['texture']+'.png','java_particle_parity':False}
  else:
   entry=grill_items[identifier];ref=entry['particle_sprite']
   if not ref:
    rows.append({'id':identifier,'index':index,'palette':[0xB86B45]*16,'source':{'kind':'unresolved_java_particle_provider_fallback','java_particle_parity':False,'reason':'Pinned default model has no resolvable particle; neutral provider fallback is provisional, native missing-sprite output is unverified'}})
    continue
   ns,texture=ref.split(':',1);rel='common/src/main/resources/assets/'+ns+'/textures/'+texture+'.png';path=a.grilling/rel
   origin={'kind':'pinned_java_grilling_particle_sprite','sprite':ref,'source_path':rel,'pin':grilling['source_commit'],'git_blob':grill_files[rel].get('git_blob')}
  raw=path.read_bytes();digest=sha(raw)
  if identifier.startswith('kaleidoscope_cookery:'):assert digest==row['texture_sha256'],identifier
  if identifier.startswith('minecraft:'):assert digest==entry['texture_sha256'],identifier
  if identifier.startswith('kaleidoscope_grilling:'):
   assert digest==grill_files[rel]['sha256'],identifier
   assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==grill_files[rel]['git_blob'],identifier
  origin['sha256']=digest
  palette=sample_grid(Image.open(io.BytesIO(raw)).convert('RGBA'))
  rows.append({'id':identifier,'index':index,'palette':palette,'source':origin})
 white=a.vanilla/'assets/minecraft/textures/block/white_concrete.png';out=FIX/'assets/minecraft/textures/block/white_concrete.png';out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(white,out)
 proof={'schema':1,'algorithm_pin':'9a1acdab27698457bec16c9362678e574895a28c','item_tint_policy':'static default tint -1; stateful item colors and external resource overrides are not sampled dynamically','base_texture':{'source':'official Java1.20.1 particle extraction','path':'assets/minecraft/textures/block/white_concrete.png','sha256':sha(out.read_bytes())},'items':rows}
 proof['vanilla_reference']={k:vanilla[k]for k in ('source_version','official_client_url','client_sha1','client_sha256')}
 (ROOT/'development/gameplay_core/fixtures/secret-food-palettes.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
 print('Imported',len(rows),'palette samples; no source food textures copied')
if __name__=='__main__':main()
