from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
NEW=('a2759_fireworks_feast_core.js','a2759_fireworks_feast_runtime.js')
LANG_IDS=('fireworks_feast',)

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def function_body(text,name):
 marker=f'function {name}'
 start=text.index(marker)
 paren=text.index('(',start);depth=0;close=None
 for i in range(paren,len(text)):
  if text[i]=='(':depth+=1
  elif text[i]==')':
   depth-=1
   if depth==0:close=i;break
 assert close is not None,name
 brace=text.index('{',close);depth=0
 for i in range(brace,len(text)):
  if text[i]=='{':depth+=1
  elif text[i]=='}':
   depth-=1
   if depth==0:return text[brace:i+1]
 raise AssertionError(name)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,59] and rm['header']['version']==[2,7,59]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.59 Fireworks Feast Parity BP'

 for name in NEW:
  assert (BP/'scripts'/name).read_bytes()==(DEV/name).read_bytes(),name

 core=(BP/'scripts/a2759_fireworks_feast_core.js').read_text(encoding='utf-8')
 assert "id:'fireworks_feast'" in core
 assert "parent:'eat_it_hot'" in core
 assert "frame:'challenge'" in core
 assert 'xp:100' in core
 assert "FIREWORKS_FEAST_PROGRESS_KEY='kaleidoscope_grilling:advancement_foods'" in core
 assert core.count("'kaleidoscope_grilling:")==30  # 29 foods + progress key
 assert "'kaleidoscope_grilling:secret_skewer'" not in core
 assert 'FIREWORKS_FEAST_FOODS.length' in core
 assert 'JSON.parse(value)' in core

 runtime=(BP/'scripts/a2759_fireworks_feast_runtime.js').read_text(encoding='utf-8')
 assert "from './a2753_advancement_runtime.js'" in runtime
 assert "from './a2759_fireworks_feast_core.js'" in runtime
 assert 'player?.getDynamicProperty(FIREWORKS_FEAST_PROGRESS_KEY)' in runtime
 assert 'player.setDynamicProperty(FIREWORKS_FEAST_PROGRESS_KEY,JSON.stringify(eaten))' in runtime
 assert 'awardOneShotAdvancement(player,FIREWORKS_FEAST)' in runtime
 for forbidden in ('subscribe(','runInterval(','runTimeout(','addExperience','world.sendMessage'):
  assert forbidden not in runtime,forbidden

 main=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert main.count("import {recordFireworksFeastFood} from './a2759_fireworks_feast_runtime.js';")==1
 assert main.count('recordFireworksFeastFood(player,id);')==1
 after=function_body(main,'afterCommitted')
 assert after.count('recordFireworksFeastFood(player,id);')==1
 assert after.index('awardMentalPreparationFailed(player,id);')<after.index('recordFireworksFeastFood(player,id);')

 # Preserve prior advancement/hardening/world-acquisition slices.
 for path in (
  BP/'scripts/a2753_advancement_runtime.js',
  BP/'scripts/a2756_advancement_event_runtime.js',
  BP/'scripts/a2758_advancement_challenge_runtime.js',
  BP/'scripts/a2750_food_state_adapter.js',
  BP/'loot_tables/kaleidoscope_grilling/village_pepper_bonus.json',
  BP/'loot_tables/kaleidoscope_grilling/fortress_houttuynia_bonus.json',
  BP/'features/pepper_tree_worldgen.json',
 ):
  assert path.is_file(),path

 adapter=(BP/'scripts/a2750_food_state_adapter.js').read_text(encoding='utf-8')
 apply=adapter.split('export function applyFoodMetadata',1)[1]
 assert apply.index('setHotFood(stack,hotTicks)')<apply.index('setFoodSeasonings(stack,seasoning)')

 for lang in ('en_US.lang','zh_CN.lang','zh_TW.lang'):
  rows=(RP/'texts'/lang).read_text(encoding='utf-8').splitlines()
  for id in LANG_IDS:
   for suffix in ('title','description'):
    key=f'advancement.kaleidoscope_grilling.{id}.{suffix}'
    assert sum(1 for row in rows if row.startswith(key+'='))==1,(lang,key)

 subprocess.run(['node',str(DEV/'test_a2759_core.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2759-fireworks-feast-parity.json')
 assert report['version']=='A2.7.59'
 assert report['advancement']=='fireworks_feast'
 assert report['java_contract']['food_count']==29
 assert report['java_contract']['experience']==100
 assert report['java_contract']['progress_key']=='kaleidoscope_grilling:advancement_foods'
 assert report['reuse']['new_listener_count']==0
 assert report['reuse']['new_interval_count']==0
 assert report['reuse']['duplicate_progression_store'] is False
 assert report['official_reference']['git_blob']=='833e034c9e04dd920680f4287a66efb008a81449'
 assert report['minecraft_tested'] is False and report['bds_tested'] is False

 compiled=[]
 if a.compiled:
  dist=P/'builds/dist'
  for name,source in [('behavior_pack',BP),('resource_pack',RP)]:
   manifest=load(source/'manifest.json')
   matches=[x.parent for x in dist.rglob('manifest.json') if load(x).get('header',{}).get('uuid')==manifest['header']['uuid']]
   assert len(matches)==1,(name,matches);target=matches[0];count=0
   for p in source.rglob('*'):
    if not p.is_file() or p.name.startswith('.'):continue
    q=target/p.relative_to(source);assert q.is_file(),str(q)
    if p.suffix=='.json':assert load(p)==load(q),str(q)
    else:assert p.read_bytes()==q.read_bytes(),str(q)
    count+=1
   compiled.append({'pack':name,'compared_files':count,'matches_source':True})

 result={
  'version':'A2.7.59','fireworks_feast_parity':True,
  'food_count':29,'persistent_player_progress':True,
  'official_player_dynamic_property_sample_pinned':True,
  'shared_a2753_adapter':True,'new_listener_count':0,'new_interval_count':0,
  'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2759-dash-verification.json' if a.compiled else 'a2759-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
