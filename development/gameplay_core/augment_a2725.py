from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
VERSION=[2,7,25]
HOLD_OFFSET=[0,7,2]
ANIM_FILE='animations/a2725_skewer_hold.animation.json'
FIRST='animation.kaleidoscope_grilling.a2725.skewer_hold_first_person'
THIRD='animation.kaleidoscope_grilling.a2725.skewer_hold_third_person'

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.25 Skewer Hand Anchor BP'),(rm,'Kaleidoscope Grilling A2.7.25 Skewer Hand Anchor RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json')
 cfg['name']='Kaleidoscope Grilling A2.7.25 Skewer Hand Anchor'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_25_Skewer_Hand_Anchor'
 write(P/'config.json',cfg)

def animation_doc():
 hold={'loop':True,'bones':{'root':{'position':HOLD_OFFSET}}}
 return {'format_version':'1.8.0','animations':{FIRST:hold,THIRD:hold}}

def patch_attachables():
 paths=sorted((RP/'attachables').glob('*_skewer.attachable.json'))
 if len(paths)!=39:raise RuntimeError(f'A2.7.25 expected 39 skewer attachables, got {len(paths)}')
 for path in paths:
  doc=load(path);desc=doc['minecraft:attachable']['description']
  animations=desc.setdefault('animations',{})
  if 'hold_first_person' in animations or 'hold_third_person' in animations:
   raise RuntimeError('A2.7.25 hold animation already present: '+path.name)
  animations['hold_first_person']=FIRST
  animations['hold_third_person']=THIRD
  scripts=desc.setdefault('scripts',{})
  if 'animate' in scripts:
   raise RuntimeError('A2.7.25 unexpected existing animate script: '+path.name)
  scripts['animate']=[
   {'hold_first_person':'context.is_first_person == 1.0'},
   {'hold_third_person':'context.is_first_person == 0.0'},
  ]
  write(path,doc)
 write(RP/ANIM_FILE,animation_doc())

def report():
 write(P/'reports/a2725-skewer-hand-anchor.json',{
  'version':'A2.7.25',
  'scope':'fixed-skewer attachable hand anchor correction',
  'source_bug':'all 39 fixed/raw/ordinary skewer attachables bound source geometry directly at its model origin, omitting the hand-space offset already used by the A1.16 player-binding prototype',
  'bedrock_fix':{
   'attachable_count':39,
   'shared_animation_file':ANIM_FILE,
   'root_bone':'root',
   'first_person_offset':HOLD_OFFSET,
   'third_person_offset':HOLD_OFFSET,
   'first_person_condition':'context.is_first_person == 1.0',
   'third_person_condition':'context.is_first_person == 0.0',
   'geometry_rebaked':False,
   'bite_stage_pre_animation_preserved':True,
  },
  'offset_provenance':{
   'prototype':'projects/grilling/integration/immersion_lab/resource_pack/models/entity/hand_props.geo.json',
   'prototype_builder':'development/player_binding/build.py',
   'raw_beef_stage0_to_prototype_delta':HOLD_OFFSET,
  },
  'java_note':'Java item models carry separate first/third-person display transforms. Bedrock item-slot binding already supplies the holder/view basis, so this batch restores the missing local hand anchor only instead of blindly applying Java rotations a second time.',
  'minecraft_tested':False,'bds_tested':False,
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,24]:
  raise RuntimeError('A2.7.25 must augment verified A2.7.24')
 patch_versions();patch_attachables();report()
 print('A2.7.25 skewer hand anchor complete')
if __name__=='__main__':main()
