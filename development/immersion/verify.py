"""Read actual source/compiled pack outputs; no Minecraft semantic validation claim."""
from pathlib import Path
import argparse, hashlib, json, math, re
ROOT=Path(__file__).resolve().parents[2]
LAB=ROOT/'projects/grilling/integration/immersion_lab'

def load(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def finite(value):
 if isinstance(value,float) and not math.isfinite(value):raise ValueError('Non-finite JSON number')
 if isinstance(value,dict):
  for child in value.values():finite(child)
 if isinstance(value,list):
  for child in value:finite(child)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');args=ap.parse_args()
 rp=LAB/'resource_pack';bp=LAB/'behavior_pack'
 for path in LAB.rglob('*.json'):finite(load(path))
 definition=load(bp/'entities/rehearsal.json')['minecraft:entity']['description']
 client=load(rp/'entity/rehearsal.entity.json')['minecraft:client_entity']['description']
 geometry=load(rp/'models/entity/rehearsal.geo.json')['minecraft:geometry'][0]
 assert definition['identifier']==client['identifier']=='kg_imm:rehearsal'
 assert geometry['description']['identifier']==client['geometry']['default']
 assert len(definition['properties'])<=32 and all(p['client_sync'] for p in definition['properties'].values())
 body=load(rp/'animations/rehearsal.animation.json')['animations'][client['animations']['scene']]
 bones={b['name']:b for b in geometry['bones']}
 assert len(bones)==len(geometry['bones'])
 for name,bone in bones.items():
  seen={name}
  while 'parent' in bone:
   name=bone['parent'];assert name in bones and name not in seen
   seen.add(name);bone=bones[name]
 assert all(n in bones for n in body['bones'])
 pre=' '.join(client['scripts']['pre_animation'])
 for prop in re.findall(r"q.property\('([^']+)'\)",pre):assert prop in definition['properties']
 sound_defs=load(rp/'sounds/sound_definitions.json')['sound_definitions']
 for sound in sound_defs.values():
  for entry in sound['sounds']:
   name=entry if isinstance(entry,str) else entry['name']
   assert (rp/(name+'.ogg')).is_file(),name
 for path in [rp/'entity/player.entity.json',rp/'entity/player.json']:
  assert not path.exists(),'Never replace vanilla player'
 checks=[]
 for pack in ['resource_pack','behavior_pack']:
  source=LAB/pack;manifest=load(source/'manifest.json')
  assert all(v['version']==[0,1,15] for v in manifest['modules'])
  if args.compiled:
   matches=[x.parent for x in (LAB/'builds/dist').rglob('manifest.json') if load(x).get('header',{}).get('uuid')==manifest['header']['uuid']]
   assert len(matches)==1,(pack,matches)
   files=[p for p in source.rglob('*') if p.is_file() and not p.name.startswith('.')]
   for path in files:
    dst=matches[0]/path.relative_to(source);assert dst.is_file(),str(dst)
    if path.suffix=='.json':assert load(path)==load(dst),str(dst)
    else:assert path.read_bytes()==dst.read_bytes(),str(dst)
   checks.append({'pack':pack,'uuid':manifest['header']['uuid'],'compared_files':len(files),'matches_source':True})
 report={'reference_validation':True,'bone_count':len(bones),'animation_bone_count':len(body['bones']),'sound_definitions':len(sound_defs),'compiled':args.compiled,'compiled_packs':checks,'minecraft_tested':False,'bridge_ui_tested':False}
 out=ROOT/'projects/grilling/reports/immersion_a115'/('dash-verification.json' if args.compiled else 'pack-references.json')
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(out.read_text())
if __name__=='__main__':main()
