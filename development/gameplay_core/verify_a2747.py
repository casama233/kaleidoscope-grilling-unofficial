from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
ITEM_ID='kaleidoscope_grilling:wedding_candy';TEXTURE_BLOB='d7ca9f5dfa61d6658372d8e181283fb5bf756d78'
LANG_KEYS=(
 'item.kaleidoscope_grilling:wedding_candy.name','tooltip.kaleidoscope_grilling.wedding_candy.1',
 'tooltip.kaleidoscope_grilling.wedding_candy.2','message.kaleidoscope_grilling.wedding_candy.received')

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def blob(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,47] and rm['header']['version']==[2,7,47]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.47 Wedding Candy BP'

 item=load(BP/'items/wedding_candy.json')['minecraft:item'];assert item['description']['identifier']==ITEM_ID
 c=item['components'];food=c['minecraft:food']
 assert c['minecraft:max_stack_size']==64 and c['minecraft:icon']['textures']['default']=='wedding_candy'
 assert food['nutrition']==20 and food['saturation_modifier']==0.5 and food['can_always_eat'] is True
 assert c['minecraft:use_modifiers']['use_duration']==1.6

 tex=RP/'textures/items/wedding_candy.png';assert tex.is_file() and blob(tex.read_bytes())==TEXTURE_BLOB
 atlas=load(RP/'textures/item_texture.json')['texture_data'];assert atlas['wedding_candy']['textures']=='textures/items/wedding_candy'
 catalog=load(BP/'item_catalog/crafting_item_catalog.json');items=catalog['minecraft:crafting_items_catalog']['categories'][0]['groups'][0]['items']
 assert items.count(ITEM_ID)==1

 for name in ('a2747_wedding_candy_core.js','a2747_wedding_candy_runtime.js'):
  assert (BP/'scripts'/name).read_bytes()==(DEV/name).read_bytes(),name
 effect=(BP/'scripts/a2732_standalone_food_effect_core.js').read_text(encoding='utf-8')
 for token in ('WEDDING_CANDY_ID','WEDDING_CANDY_EFFECT','WEDDING_CANDY_EFFECT_TICKS','itemId:WEDDING_CANDY_ID'):
  assert token in effect,token
 standalone=(BP/'scripts/a2732_standalone_food_effect_runtime.js').read_text(encoding='utf-8')
 assert standalone.count('itemCompleteUse.subscribe')==1
 wedding=(BP/'scripts/a2747_wedding_candy_runtime.js').read_text(encoding='utf-8')
 assert wedding.count('system.runInterval(')==1 and 'itemCompleteUse.subscribe' not in wedding
 assert 'shanghaiCalendar' in wedding and 'nextWeddingCandyProgress' in wedding and 'addExperience' in wedding
 main_text=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert main_text.count("import './a2747_wedding_candy_runtime.js';")==1
 assert "fxGet(target,'invincible')" in main_text and 'beforeEvents.entityHurt.subscribe' in main_text

 for lang in ('en_US.lang','zh_CN.lang','zh_TW.lang'):
  rows=(RP/'texts'/lang).read_text(encoding='utf-8').splitlines()
  for key in LANG_KEYS:assert sum(1 for row in rows if row.startswith(key+'='))==1,(lang,key)

 subprocess.run(['node',str(DEV/'test_a2747_core.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)
 report=load(P/'reports/a2747-wedding-candy.json')
 assert report['version']=='A2.7.47' and report['java_contract']['nutrition']==20
 assert report['java_contract']['effect_ticks']==300 and report['java_contract']['advancement_xp_reward']==50
 assert report['reuse']['existing_item_complete_use_listener'] is True
 assert report['reuse']['new_item_complete_use_listener'] is False
 assert report['bedrock_adaptation']['xp_reward_preserved'] is True
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
  'version':'A2.7.47','wedding_candy':True,'shared_standalone_food_effect_runtime':True,
  'new_item_complete_use_listener':False,'event_runtime':True,'invincible_ticks':300,
  'event_window':'2026-09-01..2026-09-12 Asia/Shanghai','xp_reward':50,
  'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2747-dash-verification.json' if a.compiled else 'a2747-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
