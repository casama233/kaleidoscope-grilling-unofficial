from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
COOKERY_BP='10f37ae2-9ccf-435f-b34b-0eec8191cd94';COOKERY_RP='c89dc8df-c3fc-4bc8-8bd0-527abba76681';CV=[1,0,6]
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def git_blob(p):
 v=p.read_bytes();return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,1] and rm['header']['version']==[2,7,1]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.1 Gameplay BP'
 assert rm['header']['name']=='Kaleidoscope Grilling A2.7.1 Gameplay RP'
 assert {'uuid':COOKERY_BP,'version':CV} in bm['dependencies'] and {'uuid':COOKERY_RP,'version':CV} in rm['dependencies']
 assert {'module_name':'@minecraft/server','version':'2.9.0'} in bm['dependencies']

 powder=load(BP/'items/sweet_potato_powder.json')['minecraft:item']
 assert powder['description']['identifier']=='kaleidoscope_grilling:sweet_potato_powder'
 pc=powder['components']
 assert pc['minecraft:max_stack_size']==64 and pc['minecraft:allow_off_hand'] is True
 assert pc['minecraft:use_modifiers']['use_duration']==1.5 and pc['minecraft:use_modifiers']['start_using']=='always'
 assert pc['minecraft:use_modifiers']['movement_modifier']==0.2
 assert pc['minecraft:use_animation']['value']=='bow'
 assert pc['minecraft:food']['nutrition']==0 and pc['minecraft:food']['can_always_eat'] is True
 sheet=load(BP/'items/raw_sweet_potato_sheet.json')['minecraft:item']
 assert sheet['description']['identifier']=='kaleidoscope_grilling:raw_sweet_potato_sheet'
 assert sheet['components']['minecraft:max_stack_size']==64
 assert git_blob(RP/'textures/items/sweet_potato_powder.png')=='2e15c9ea095ff0ef7c7959b05bd9f60d79631dab'
 assert git_blob(RP/'textures/items/raw_sweet_potato_sheet.png')=='a537de022aa9cc50b99dfec6f0fedd0046cb2d2f'

 core=(BP/'scripts/a271_sweet_potato_core.js').read_text(encoding='utf-8')
 for token in ("KNEAD_TICKS=30","KNEAD_SECONDS=1.5","CHOPPING_BOARD_CUTS=4","kneadResult"):assert token in core,token
 rt=(BP/'scripts/a271_sweet_potato_runtime.js').read_text(encoding='utf-8')
 for token in ('ACTIVE_KNEADS','itemStartUse','itemStopUse','itemCompleteUse','installResult','armor.equip_leather'):assert token in rt,token
 main=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert "import './a271_sweet_potato_runtime.js';" in main
 assert "stack?.typeId==='kaleidoscope_grilling:sweet_potato_powder'" in main

 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a24_core.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a25_core.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a26_core.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a271_core.mjs')],check=True)

 parity=load(P/'reports/a271-parity.json')
 assert parity['version']=='A2.7.1'
 assert parity['direct_knead']['duration_ticks']==30
 assert parity['direct_knead']['transforms_entire_starting_stack'] is True
 assert parity['java_alternate_processing']['cookery_chopping_board']['cut_count']==4
 assert parity['java_alternate_processing']['cookery_chopping_board']['ported_in_this_slice'] is False

 compiled=[]
 if a.compiled:
  dist=P/'builds/dist'
  for name,source in [('behavior_pack',BP),('resource_pack',RP)]:
   manifest=load(source/'manifest.json')
   matches=[p.parent for p in dist.rglob('manifest.json') if load(p).get('header',{}).get('uuid')==manifest['header']['uuid']]
   assert len(matches)==1,(name,matches);target=matches[0];count=0
   for p in source.rglob('*'):
    if not p.is_file() or p.name.startswith('.'):continue
    q=target/p.relative_to(source);assert q.is_file(),str(q)
    if p.suffix=='.json':assert load(p)==load(q),str(q)
    else:assert p.read_bytes()==q.read_bytes(),str(q)
    count+=1
   compiled.append({'pack':name,'compared_files':count,'matches_source':True})

 result={
  'version':'A2.7.1','knead_ticks':30,'full_stack_transform':True,
  'chopping_board_cut_count_reference':4,'chopping_board_runtime_ported':False,
  'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a271-dash-verification.json' if a.compiled else 'a271-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))
if __name__=='__main__':main()
