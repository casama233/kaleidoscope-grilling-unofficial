from __future__ import annotations
import copy, hashlib, json, shutil, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'projects/grilling'
P=SRC/'gameplay_core'
BP=P/'behavior_pack'
RP=P/'resource_pack'
VERSION=[2,1,0]
UPSTREAM='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
PNG_BLOBS={
 'green_chili_powder':'ba3ea295fffa8c81f46e62fbc1ac745ff1182f18',
 'sichuan_pepper':'58cb2b17ad72f83d6edb65780244cd4c75e99f68',
 'onion_powder':'e91b1fd3def9ad8c8484906d3ce885e75c544e22',
 'houttuynia_powder':'2f4580e953b773adb19a23473c0d0cc31e293d51',
 'totem_powder':'e11d5aa1aef590512028816d6821da4735511120',
 'dragon_egg_powder':'841d3fba245196c536a72b39c8f29bff7c5baaf6',
}
FORMAL_BASES=[
 'beef','pork_belly','chicken_skin','mid_wing','squid_tentacle','fish','sweet_potato_sheet','potato_slice',
 'caterpillar','mushroom','bun_slice','ender_pearl','meatball','slime','meat_and_bone','fried_egg','gluten','lamb','golden'
]

def git_blob(v:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(v)).encode()+b'\0'+v).hexdigest()

def fetch_binary(path,expected):
    req=urllib.request.Request(UPSTREAM+path,headers={'User-Agent':'Grilling-A2.1/1'})
    with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
    if git_blob(v)!=expected:raise RuntimeError('pinned binary mismatch: '+path)
    return v

def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    if isinstance(data,(dict,list)):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    else:path.write_text(data,encoding='utf-8')

def load(path):return json.loads(path.read_text(encoding='utf-8-sig'))

def bump_manifest(path,label):
    m=load(path);m['header']['version']=VERSION;m['header']['name']='Kaleidoscope Grilling A2.1 '+label
    m['header']['description']='Cookery油壺、完整調料資料、煙火氣與效果等價層；需要 Cookery 1.0.6'
    for mod in m.get('modules',[]):mod['version']=VERSION
    for dep in m.get('dependencies',[]):
        if dep.get('uuid') in {load(RP/'manifest.json')['header']['uuid'],load(BP/'manifest.json')['header']['uuid']}:
            dep['version']=VERSION
    write(path,m)

def seasoning_item(identifier,icon):
    return {'format_version':'1.26.30','minecraft:item':{'description':{'identifier':'kaleidoscope_grilling:'+identifier,'menu_category':{'category':'items'}},'components':{
      'minecraft:display_name':{'value':'item.kaleidoscope_grilling:'+identifier+'.name'},
      'minecraft:icon':{'textures':{'default':icon}},'minecraft:max_stack_size':64
    }}}

def candidate_for(item_id):
    if item_id=='ordinary_skewer':return 'ordinary_full'
    cooked=item_id.startswith('grilled_')
    base=item_id.replace('raw_','').replace('grilled_','').removesuffix('_skewer')
    if base=='slime':return 'slime_frame_4' if cooked else 'slime_frame_0'
    return base+('_cooked' if cooked else '_raw')

def add_attachable(item_id,candidate,specs):
    by={x['name']:x for x in specs['candidates']}
    if candidate not in by:raise RuntimeError('missing candidate '+candidate)
    spec=by[candidate];geo_src=SRC/f'resource_pack/models/entity/kg_a1/{candidate}.geo.json'
    atlas=spec['atlas_name'];tex_src=SRC/f'resource_pack/textures/kg_a1/{atlas}.png'
    if not geo_src.is_file() or not tex_src.is_file():raise RuntimeError('missing exported source '+candidate)
    geo=load(geo_src);ident='geometry.kg_a21.'+item_id
    for g in geo['minecraft:geometry']:
        g['description']['identifier']=ident
        for b in g.get('bones',[]):
            if not b.get('parent'):b['binding']='q.item_slot_to_bone_name(context.item_slot)'
    write(RP/f'models/entity/a21/{item_id}.geo.json',geo)
    dest=RP/f'textures/a21/{item_id}.png';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(tex_src,dest)
    attach={'format_version':'1.10.0','minecraft:attachable':{'description':{
      'identifier':'kaleidoscope_grilling:'+item_id,'materials':{'default':'entity_alphablend'},
      'textures':{'default':'textures/a21/'+item_id},'geometry':{'default':ident},
      'render_controllers':['controller.render.kg_a21.item']
    }}}
    write(RP/f'attachables/{item_id}.attachable.json',attach)

def main():
    if not P.is_dir():raise RuntimeError('run A2.0 build.py first')
    report=load(P/'reports/build.json')
    if report.get('version')!='A2.0.0':raise RuntimeError('expected freshly generated A2.0 base')
    # Replace runtime/core with A2.1 authored layers.
    shutil.copyfile(Path(__file__).parent/'a21_core_logic.js',BP/'scripts/core_logic.js')
    shutil.copyfile(Path(__file__).parent/'a21_runtime.js',BP/'scripts/main.js')
    # Versions/dependencies.
    bp=load(BP/'manifest.json');rp=load(RP/'manifest.json')
    bp_uuid=bp['header']['uuid'];rp_uuid=rp['header']['uuid']
    bp['header']['version']=VERSION;bp['header']['name']='Kaleidoscope Grilling A2.1 Gameplay BP';bp['header']['description']='Cookery油壺、調味、煙火氣與效果等價層；需要 Cookery 1.0.6'
    rp['header']['version']=VERSION;rp['header']['name']='Kaleidoscope Grilling A2.1 Gameplay RP';rp['header']['description']='正式串3D手持與調料瓶素材；需要 Cookery 1.0.6'
    for mod in bp['modules']:mod['version']=VERSION
    for mod in rp['modules']:mod['version']=VERSION
    for dep in bp['dependencies']:
        if dep.get('uuid')==rp_uuid:dep['version']=VERSION
    write(BP/'manifest.json',bp);write(RP/'manifest.json',rp)
    cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.1 Gameplay';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_1';write(P/'config.json',cfg)
    # Six formal seasoning ingredients from pinned Java assets.
    terrain=load(RP/'textures/item_texture.json');texdata=terrain['texture_data']
    for item,blob in PNG_BLOBS.items():
        raw=fetch_binary('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/'+item+'.png',blob)
        dest=RP/f'textures/items/{item}.png';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
        texdata[item]={'textures':'textures/items/'+item}
        write(BP/f'items/{item}.json',seasoning_item(item,item))
    # Better bottle icons from the verified converted spice-jar atlas.
    spice=SRC/'resource_pack/textures/kg_a1/spice_jar.png'
    for item in ('empty_seasoning_bottle','pending_seasoning','special_seasoning'):
        shutil.copyfile(spice,RP/f'textures/items/{item}.png');texdata[item]={'textures':'textures/items/'+item}
    empty=load(BP/'items/empty_seasoning_bottle.json')
    empty['minecraft:item']['components']['minecraft:block_placer']={'block':'kaleidoscope_grilling:seasoning_bottle','replace_block_item':True}
    write(BP/'items/empty_seasoning_bottle.json',empty)
    pending={'format_version':'1.26.30','minecraft:item':{'description':{'identifier':'kaleidoscope_grilling:pending_seasoning','menu_category':{'category':'items'}},'components':{
      'minecraft:display_name':{'value':'item.kaleidoscope_grilling:pending_seasoning.name'},
      'minecraft:icon':{'textures':{'default':'pending_seasoning'}},'minecraft:max_stack_size':1,'minecraft:hand_equipped':True,
      'minecraft:use_modifiers':{'start_using':'always','use_duration':4.0,'movement_modifier':0.35},
      'minecraft:use_animation':{'value':'none'}
    }}}
    write(BP/'items/pending_seasoning.json',pending)
    write(RP/'textures/item_texture.json',terrain)
    # Actual seasoning bottle block, one-bottle A2.1 core; payload preserved on pickup/place.
    bottle_geo=load(SRC/'resource_pack/models/entity/kg_a1/seasoning_bottles_1.geo.json')
    bottle_geo['minecraft:geometry'][0]['description']['identifier']='geometry.kg_a21.seasoning_bottle'
    write(RP/'models/blocks/seasoning_bottle.geo.json',bottle_geo)
    shutil.copyfile(spice,RP/'textures/blocks/seasoning_bottle.png')
    terrain_block=load(RP/'textures/terrain_texture.json');terrain_block['texture_data']['kg_a21_seasoning_bottle']={'textures':'textures/blocks/seasoning_bottle'};write(RP/'textures/terrain_texture.json',terrain_block)
    block={'format_version':'1.26.50','minecraft:block':{'description':{'identifier':'kaleidoscope_grilling:seasoning_bottle'},'components':{
      'minecraft:display_name':'tile.kaleidoscope_grilling:seasoning_bottle.name','minecraft:geometry':'geometry.kg_a21.seasoning_bottle',
      'minecraft:material_instances':{'*':{'texture':'kg_a21_seasoning_bottle','render_method':'blend'}},
      'minecraft:collision_box':{'origin':[-3,0,-3],'size':[6,12,6]},'minecraft:selection_box':{'origin':[-4,0,-4],'size':[8,13,8]},
      'minecraft:destructible_by_mining':{'seconds_to_destroy':.3}
    }}}
    write(BP/'blocks/seasoning_bottle.json',block)
    # Formal base 3D held attachables. Bite-stage switching is deliberately separate.
    specs=load(SRC/'config/asset_specs.json')
    formal=[]
    for base in FORMAL_BASES:
        for prefix in ('raw_','grilled_'):
            item=prefix+base+'_skewer';add_attachable(item,candidate_for(item),specs);formal.append(item)
    add_attachable('ordinary_skewer','ordinary_full',specs);formal.append('ordinary_skewer')
    write(RP/'render_controllers/a21_items.render_controllers.json',{'format_version':'1.8.0','render_controllers':{
      'controller.render.kg_a21.item':{'geometry':'Geometry.default','materials':[{'*':'Material.default'}],'textures':['Texture.default']}
    }})
    # Four-second bottle shake, main/off hand, no infinite looping.
    def shake_bone(side):
        frames={}
        for i in range(21):
            t=i*.2;wave=1 if i%2 else -1
            frames[str(round(t,2))]=[-58+wave*20,side*(18+wave*34),side*(26-wave*30)]
        return frames
    write(RP/'animations/a21_shake.animation.json',{'format_version':'1.8.0','animations':{
      'animation.kg_a21.player.shake.main':{'animation_length':4.0,'override_previous_animation':True,'bones':{'rightarm':{'rotation':shake_bone(1)}}},
      'animation.kg_a21.player.shake.off':{'animation_length':4.0,'override_previous_animation':True,'bones':{'leftarm':{'rotation':shake_bone(-1)}}}
    }})
    # Localisation additions.
    zh=RP/'texts/zh_TW.lang';cn=RP/'texts/zh_CN.lang';en=RP/'texts/en_US.lang'
    zh_add={
      'green_chili_powder':'青辣椒粉','sichuan_pepper':'花椒','onion_powder':'洋蔥粉','houttuynia_powder':'魚腥草粉',
      'totem_powder':'圖騰粉','dragon_egg_powder':'龍蛋粉','pending_seasoning':'待搖調料瓶'
    }
    en_add={k:k.replace('_',' ').title() for k in zh_add};en_add['sichuan_pepper']='Sichuan Pepper';en_add['pending_seasoning']='Pending Seasoning'
    def append(path,values,block_name):
        text=path.read_text();text+='\n'+'\n'.join('item.kaleidoscope_grilling:'+k+'.name='+v for k,v in values.items())+'\n'
        text+='tile.kaleidoscope_grilling:seasoning_bottle.name='+block_name+'\n';path.write_text(text)
    append(zh,zh_add,'調料瓶');append(cn,{**zh_add,'onion_powder':'洋葱粉','houttuynia_powder':'折耳根粉','dragon_egg_powder':'龙蛋粉'},'调料瓶');append(en,en_add,'Seasoning Bottle')
    # Update report.
    report.update({
      'version':'A2.1.0','formal_seasoning_ingredients':6,'seasoning_bottle_block':True,'pending_shake_ticks':80,
      'cookery_oil_pot_direct':True,'cookery_oil_property':'kc_oil_count','cookery_oil_legacy_full':256,
      'seasoning_max_uses':16,'seasoning_capacity':8,'hot_time_source':'world.getAbsoluteTime()','hot_bucket_ticks':100,
      'hot_saturation_percent':125,'held_3d_attachables':len(formal),
      'custom_effect_equivalence':['vigor','mustard','tundra_strider','preservation','flatulence','projectile_dodge','hinder','sulfur','warmth'],
      'advanced_seasoning_equivalence':['heavy_metal','heavy_metal_poisoning','dragon_blood','numb'],
      'a21_known_gaps':[
        'Bedrock Cookery 1.0.6 exposes generic oil only; chili-oil type remains an optional Grilling item property until true fluids arrive',
        'seasoning bottle block currently models one editable bottle, not Java four-bottle physical stacking',
        'Tundra Strider powder-snow walking and Mustard/Sulfur AI goals use script approximations',
        'Dragon Blood uses nearest stable Health Boost approximation (+4/+8 max health instead of Java +6/+10)',
        'Numb tracks duration but Java-only crosshair orbit/limb sway is not yet reproduced in native HUD',
        'formal held 3D attachables use converted base geometry; bite-stage geometry switching remains pending engine-safe integration',
        'Minecraft/BDS runtime not yet tested'
      ]
    })
    write(P/'reports/build.json',report)
    write(P/'reports/a21-build.json',{k:report[k] for k in ['version','cookery_oil_pot_direct','seasoning_bottle_block','pending_shake_ticks','hot_saturation_percent','held_3d_attachables','custom_effect_equivalence','advanced_seasoning_equivalence','a21_known_gaps']})
    readme=P/'README.zh-TW.md'
    readme.write_text('# A2.1 Gameplay Core\n\nA2.1 在 A2.0 真三槽烤爐上補上 Cookery 1.0.6 油壺直連、可編配調料瓶、煙火氣到期與125%飽和度、Java Cookery 效果等價層、普通／黃金串特殊邏輯，以及39種固定串基礎3D手持 attachable。詳見 reports/a21-build.json 與 docs/STATUS-A2.1.md。\n',encoding='utf-8')
    print(json.dumps(load(P/'reports/a21-build.json'),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
