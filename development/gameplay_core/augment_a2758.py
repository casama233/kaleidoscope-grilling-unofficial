from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,58]
NEW_SCRIPTS=('a2758_advancement_challenge_core.js','a2758_advancement_challenge_runtime.js')
LANG={
 'en_US.lang':[
  'advancement.kaleidoscope_grilling.mental_preparation_failed.title=Mental Preparation Failed',
  'advancement.kaleidoscope_grilling.mental_preparation_failed.description=Eat a raw caterpillar skewer.',
  'advancement.kaleidoscope_grilling.metallic_taste.title=Metallic Taste',
  'advancement.kaleidoscope_grilling.metallic_taste.description=Mix special seasoning containing totem powder.',
  'advancement.kaleidoscope_grilling.taste_of_dragon.title=Taste of Dragon',
  'advancement.kaleidoscope_grilling.taste_of_dragon.description=Mix special seasoning containing dragon egg powder.',
  'advancement.kaleidoscope_grilling.metal_tolerance_failed.title=Metal Tolerance Failed',
  'advancement.kaleidoscope_grilling.metal_tolerance_failed.description=Try to gain Heavy Metal again while poisoned.',
  'advancement.kaleidoscope_grilling.strongest_shield.title=The Strongest Shield',
  'advancement.kaleidoscope_grilling.strongest_shield.description=Successfully resist the curse of an "Ordinary" Skewer',
  'advancement.kaleidoscope_grilling.strongest_spear.title=The Strongest Spear',
  'advancement.kaleidoscope_grilling.strongest_spear.description=Fail to resist the curse of an "Ordinary" Skewer',
  'advancement.kaleidoscope_grilling.wedding_candy.title=Wedding Candy for You!',
  'advancement.kaleidoscope_grilling.wedding_candy.description=On September 12, 2026, Breezeth, the creator of Kaleidoscope Grilling, will marry the love of his life. Take this candy and share in their happiness!',
  'message.kaleidoscope_grilling.advancement.task_announce= made the advancement: ',
  'message.kaleidoscope_grilling.advancement.task_self=§aAdvancement made: §r',
  'message.kaleidoscope_grilling.advancement.challenge_announce= completed the challenge: ',
  'message.kaleidoscope_grilling.advancement.challenge_self=§5Challenge complete: §r',
 ],
 'zh_CN.lang':[
  'advancement.kaleidoscope_grilling.mental_preparation_failed.title=心理建设失败',
  'advancement.kaleidoscope_grilling.mental_preparation_failed.description=吃下一根生猪儿虫串。',
  'advancement.kaleidoscope_grilling.metallic_taste.title=金属味儿',
  'advancement.kaleidoscope_grilling.metallic_taste.description=摇匀一瓶含有不死图腾粉的特制调料。',
  'advancement.kaleidoscope_grilling.taste_of_dragon.title=龙的味道',
  'advancement.kaleidoscope_grilling.taste_of_dragon.description=摇匀一瓶含有龙蛋粉的特制调料。',
  'advancement.kaleidoscope_grilling.metal_tolerance_failed.title=金属耐受失败',
  'advancement.kaleidoscope_grilling.metal_tolerance_failed.description=重金属中毒期间再次尝试获得重金属。',
  'advancement.kaleidoscope_grilling.strongest_shield.title=最强的盾',
  'advancement.kaleidoscope_grilling.strongest_shield.description=成功抵挡“普通”烤串的诅咒',
  'advancement.kaleidoscope_grilling.strongest_spear.title=最强的矛',
  'advancement.kaleidoscope_grilling.strongest_spear.description=未能成功抵挡“普通”烤串的诅咒',
  'advancement.kaleidoscope_grilling.wedding_candy.title=请你吃喜糖！',
  'advancement.kaleidoscope_grilling.wedding_candy.description=2026年9月12日，森罗物语：烟火的作者微风 Breezeth 将与此生挚爱步入婚姻。收下这颗喜糖，一同分享他们的幸福吧！',
  'message.kaleidoscope_grilling.advancement.task_announce= 获得进度：',
  'message.kaleidoscope_grilling.advancement.task_self=§a进度达成：§r',
  'message.kaleidoscope_grilling.advancement.challenge_announce= 完成挑战：',
  'message.kaleidoscope_grilling.advancement.challenge_self=§5挑战完成：§r',
 ],
 'zh_TW.lang':[
  'advancement.kaleidoscope_grilling.mental_preparation_failed.title=心理建設失敗',
  'advancement.kaleidoscope_grilling.mental_preparation_failed.description=吃下一根生豬兒蟲串。',
  'advancement.kaleidoscope_grilling.metallic_taste.title=金屬味兒',
  'advancement.kaleidoscope_grilling.metallic_taste.description=搖勻一瓶含有不死圖騰粉的特製調料。',
  'advancement.kaleidoscope_grilling.taste_of_dragon.title=龍的味道',
  'advancement.kaleidoscope_grilling.taste_of_dragon.description=搖勻一瓶含有龍蛋粉的特製調料。',
  'advancement.kaleidoscope_grilling.metal_tolerance_failed.title=金屬耐受失敗',
  'advancement.kaleidoscope_grilling.metal_tolerance_failed.description=重金屬中毒期間再次嘗試獲得重金屬。',
  'advancement.kaleidoscope_grilling.strongest_shield.title=最強的盾',
  'advancement.kaleidoscope_grilling.strongest_shield.description=成功抵擋「普通」烤串的詛咒',
  'advancement.kaleidoscope_grilling.strongest_spear.title=最強的矛',
  'advancement.kaleidoscope_grilling.strongest_spear.description=未能成功抵擋「普通」烤串的詛咒',
  'advancement.kaleidoscope_grilling.wedding_candy.title=請你吃喜糖！',
  'advancement.kaleidoscope_grilling.wedding_candy.description=2026年9月12日，《森羅物語：煙火》的作者微風 Breezeth 將與此生摯愛步入婚姻。收下這顆喜糖，一同分享他們的幸福吧！',
  'message.kaleidoscope_grilling.advancement.task_announce= 獲得進度：',
  'message.kaleidoscope_grilling.advancement.task_self=§a進度達成：§r',
  'message.kaleidoscope_grilling.advancement.challenge_announce= 完成挑戰：',
  'message.kaleidoscope_grilling.advancement.challenge_self=§5挑戰完成：§r',
 ],
}

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.58 Challenge Advancement Parity BP'),(rm,'Kaleidoscope Grilling A2.7.58 Challenge Advancement Parity RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.58 Challenge Advancement Parity'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_58_Challenge_Advancement_Parity'
 write(P/'config.json',cfg)

def patch_scripts():
 scripts=BP/'scripts'
 for name in NEW_SCRIPTS:shutil.copy2(DEV/name,scripts/name)
 shutil.copy2(DEV/'a2758_refactored_a2753_advancement_runtime.js',scripts/'a2753_advancement_runtime.js')
 shutil.copy2(DEV/'a2758_refactored_a2747_wedding_candy_runtime.js',scripts/'a2747_wedding_candy_runtime.js')

 main=scripts/'main.js';s=main.read_text(encoding='utf-8')
 anchor="import {awardLookingThePart,awardGleamingWithOil,awardSeasoningMilestones,awardEatItHot} from './a2756_advancement_event_runtime.js';\n"
 add=anchor+"import {awardSeasoningFinishedChallenges,awardMentalPreparationFailed,awardMetalToleranceFailed,awardOrdinaryChallenge,ordinaryChallengeOutcome} from './a2758_advancement_challenge_runtime.js';\n"
 if s.count(anchor)!=1:raise RuntimeError('A2.7.58 advancement import anchor drift')
 if 'a2758_advancement_challenge_runtime.js' in s:raise RuntimeError('A2.7.58 main already patched')
 s=s.replace(anchor,add,1)

 old=" if((c.totem??0)>0&&!fxGet(player,'heavy_metal_poisoning'))fxSet(player,'heavy_metal',duration,c.totem>=4?1:0);"
 new=""" if((c.totem??0)>0){
  const poisoned=!!fxGet(player,'heavy_metal_poisoning');
  if(poisoned)awardMetalToleranceFailed(player,c.totem,true);
  else fxSet(player,'heavy_metal',duration,c.totem>=4?1:0);
 }"""
 if s.count(old)!=1:raise RuntimeError('A2.7.58 heavy metal anchor drift')
 s=s.replace(old,new,1)

 old="""function applyOrdinary(player){
 const challenged=!!fxGet(player,'invincible');if(challenged)fxClear(player,'invincible');
 if(challenged&&Math.random()<.5){try{player.dimension.playSound('random.shield_block',player.location);player.dimension.spawnParticle('minecraft:electric_spark_particle',{x:player.location.x,y:player.location.y+1,z:player.location.z})}catch{}message(player,'§6普通串被無敵擋下');return}
 system.run(()=>{try{player.kill()}catch{try{player.applyDamage(100000,{cause:'override'})}catch{}}});
}"""
 new="""function applyOrdinary(player){
 const challenged=!!fxGet(player,'invincible');if(challenged)fxClear(player,'invincible');
 const outcome=ordinaryChallengeOutcome(challenged,Math.random());
 if(outcome==='shield'){awardOrdinaryChallenge(player,outcome);try{player.dimension.playSound('random.shield_block',player.location);player.dimension.spawnParticle('minecraft:electric_spark_particle',{x:player.location.x,y:player.location.y+1,z:player.location.z})}catch{}message(player,'§6普通串被無敵擋下');return}
 if(outcome==='spear')awardOrdinaryChallenge(player,outcome);
 system.run(()=>{try{player.kill()}catch{try{player.applyDamage(100000,{cause:'override'})}catch{}}});
}"""
 if s.count(old)!=1:raise RuntimeError('A2.7.58 Ordinary Skewer anchor drift')
 s=s.replace(old,new,1)

 old=" applyFixedEffect(player,id);\n awardEatItHot(player,id,meta.hot);"
 new=" applyFixedEffect(player,id);\n awardEatItHot(player,id,meta.hot);\n awardMentalPreparationFailed(player,id);"
 if s.count(old)!=1:raise RuntimeError('A2.7.58 food challenge anchor drift')
 s=s.replace(old,new,1)

 old="try{out.setDynamicProperty(SEASON_VARIANT_KEY,Math.floor(Math.random()*(SEASONING_VARIANT_MAX+1)));out.setLore(['§7Uses: '+SEASONING_MAX_USES+'/'+SEASONING_MAX_USES,'§7Ingredients: '+list.length+'/'+SEASONING_CAPACITY])}catch{};setHand(player,hand,out);message(player,'§a調料搖勻完成');"
 new="try{out.setDynamicProperty(SEASON_VARIANT_KEY,Math.floor(Math.random()*(SEASONING_VARIANT_MAX+1)));out.setLore(['§7Uses: '+SEASONING_MAX_USES+'/'+SEASONING_MAX_USES,'§7Ingredients: '+list.length+'/'+SEASONING_CAPACITY])}catch{};setHand(player,hand,out);awardSeasoningFinishedChallenges(player,list);message(player,'§a調料搖勻完成');"
 if s.count(old)!=1:raise RuntimeError('A2.7.58 seasoning-finished anchor drift')
 s=s.replace(old,new,1)
 main.write_text(s,encoding='utf-8')

def patch_lang():
 for name,lines in LANG.items():
  p=RP/'texts'/name;s=p.read_text(encoding='utf-8');rows=s.splitlines()
  for line in lines:
   key=line.split('=',1)[0]
   if any(row.startswith(key+'=') for row in rows):raise RuntimeError(f'{name}: duplicate key {key}')
  if s and not s.endswith('\n'):s+='\n'
  p.write_text(s+'\n'.join(lines)+'\n',encoding='utf-8')

def report():
 write(P/'reports/a2758-challenge-advancement-parity.json',{
  'version':'A2.7.58',
  'challenge_advancements':[
   'mental_preparation_failed','metallic_taste','taste_of_dragon','metal_tolerance_failed',
   'strongest_shield','strongest_spear','wedding_candy'
  ],
  'reuse':{
   'one_shot_adapter':'a2753_advancement_runtime.js',
   'frame_aware_shared_adapter':True,
   'new_listener_count':0,'new_interval_count':0,'duplicate_progression_store':False,
   'existing_wedding_interval_reused':True
  },
  'wedding_candy':{
   'direct_daily_xp_removed':True,
   'one_shot_advancement_xp':50,
   'daily_candy_claim_preserved':True
  },
  'ordinary_skewer':{
   'single_rng_result_shared_with_advancement':True,
   'shield_on_block':True,'spear_on_failed_challenge':True
  },
  'native_java_advancement_tree':False,'native_java_toast':False,
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,57]:raise RuntimeError('A2.7.58 must augment published A2.7.57')
 patch_scripts();patch_lang();patch_versions();report()
 print('A2.7.58 challenge advancement parity complete')

if __name__=='__main__':main()
