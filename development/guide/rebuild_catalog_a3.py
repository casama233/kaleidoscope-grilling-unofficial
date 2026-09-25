"""One-time, source-backed migration from A2 tutorials to a Cookery-style A3 catalog.

Read a locally supplied Cookery 1.0.6 pack. Never copy host scripts into this repo.
Normal builds use catalog.a3.json, not this historical migration.
"""
from __future__ import annotations
import argparse, hashlib, itertools, json, re, subprocess
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
G=ROOT/'projects/grilling';GAME=G/'gameplay_core';BP,RP=GAME/'behavior_pack',GAME/'resource_pack';GUIDE=G/'guide'
LOCALES=('zh_CN','zh_TW','en_US');NS='kaleidoscope_grilling:'
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(p,obj):
    Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def tri(cn,tw,en):return dict(zip(LOCALES,(cn,tw,en)))
def lang(p):return dict(x.split('=',1) for x in Path(p).read_text(encoding='utf-8-sig').splitlines() if '=' in x and not x.startswith('#'))
def pure_data():
    modules={'a24_skewering_core.js':'recipeTable','a2727_cookery_host_recipes_core.js':'recipeTable','a2732_standalone_food_effect_core.js':'standaloneFoodEffectTable'};out={}
    for file,fn in modules.items():
        code=f"import {{pathToFileURL}} from 'node:url';const m=await import(pathToFileURL(process.argv[1]));console.log(JSON.stringify(m.{fn}()));"
        out[file]=json.loads(subprocess.check_output(['node','--input-type=module','-e',code,str(BP/'scripts'/file)],text=True,encoding='utf-8'))
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--host-bp',required=True,type=Path);args=ap.parse_args();host=args.host_bp
    digest=hashlib.sha256((host/'scripts/events/guidebook.js').read_bytes()).hexdigest()
    if digest!='acff33eec87add1c149aff3789b1b9ec62dd1ef642a5bc7d2b2f1b70dd6332ff':raise ValueError('Unknown Cookery guide revision')
    old=load(GUIDE/'content.a2.json');old_entries={e['id']:e for e in old['entries']};host_lang={}
    for loc in LOCALES:
        paths=[p for p in (host/'scripts').rglob(f'{loc}.js') if 'guidebook' in str(p).lower()]
        if len(paths)!=1:raise ValueError('Ambiguous host locale '+loc)
        code="import {pathToFileURL} from 'node:url';const m=await import(pathToFileURL(process.argv[1]));console.log(JSON.stringify(m.default ?? m));"
        host_lang[loc]=json.loads(subprocess.check_output(['node','--input-type=module','-e',code,str(paths[0])],text=True,encoding='utf-8'))
    names={l:{} for l in LOCALES}
    for l in LOCALES:
        for k,v in lang(RP/'texts'/f'{l}.lang').items():
            if k.startswith(('item.','tile.')) and k.endswith('.name'):names[l].setdefault(k.split('.',1)[1][:-5],v)
        names[l].update({k:v for k,v in host_lang[l]['itemNames'].items() if k.startswith('kaleidoscope_cookery:')})
    vanilla={
      'stick':tri('木棍','木棍','Stick'),'redstone':tri('红石粉','紅石粉','Redstone Dust'),
      'gunpowder':tri('火药','火藥','Gunpowder'),'cod':tri('鳕鱼','鱈魚','Cod'),
      'salmon':tri('鲑鱼','鮭魚','Salmon'),'tropical_fish':tri('热带鱼','熱帶魚','Tropical Fish'),
      'pufferfish':tri('河豚','河豚','Pufferfish'),'brown_mushroom':tri('棕色蘑菇','棕色蘑菇','Brown Mushroom'),
      'red_mushroom':tri('红色蘑菇','紅色蘑菇','Red Mushroom'),'carrot':tri('胡萝卜','胡蘿蔔','Carrot'),
      'potato':tri('马铃薯','馬鈴薯','Potato'),'beetroot':tri('甜菜根','甜菜根','Beetroot'),
      'ender_pearl':tri('末影珍珠','末影珍珠','Ender Pearl'),'slime_ball':tri('黏液球','黏液球','Slimeball'),
      'bone':tri('骨头','骨頭','Bone'),'golden_apple':tri('金苹果','金蘋果','Golden Apple'),
      'totem_of_undying':tri('不死图腾','不死圖騰','Totem of Undying'),'golden_carrot':tri('金胡萝卜','金胡蘿蔔','Golden Carrot'),
      'poisonous_potato':tri('毒马铃薯','毒馬鈴薯','Poisonous Potato'),'spider_eye':tri('蜘蛛眼','蜘蛛眼','Spider Eye'),
      'sugar':tri('糖','糖','Sugar'),'honey_bottle':tri('蜂蜜瓶','蜂蜜瓶','Honey Bottle'),
      'wheat':tri('小麦','小麥','Wheat'),'bucket':tri('桶','桶','Bucket'),'brick_block':tri('红砖块','紅磚塊','Bricks'),
      'iron_ingot':tri('铁锭','鐵錠','Iron Ingot'),'oak_fence':tri('橡木栅栏','橡木柵欄','Oak Fence'),
      'hopper':tri('漏斗','漏斗','Hopper'),'beef':tri('生牛肉','生牛肉','Raw Beef'),
      'porkchop':tri('生猪排','生豬排','Raw Porkchop'),'chicken':tri('生鸡肉','生雞肉','Raw Chicken'),
      'bowl':tri('碗','碗','Bowl'),'water':tri('水','水','Water'),'oak_planks':tri('橡木木板','橡木木板','Oak Planks')}
    for short,ts in vanilla.items():
        for l in LOCALES:names[l]['minecraft:'+short]=ts[l]
    for q in range(1,7):
        for l in LOCALES:names[l][f'kaleidoscope_tavern:vinegar_q{q}']=tri(f'醋（品质 {q}）',f'醋（品質 {q}）',f'Vinegar (quality {q})')[l]
    items={load(p)['minecraft:item']['description']['identifier']:(p,load(p)['minecraft:item']) for p in (BP/'items').glob('*.json')}
    blocks={load(p)['minecraft:block']['description']['identifier']:(p,load(p)['minecraft:block']) for p in (BP/'blocks').glob('*.json')}
    atlas=load(RP/'textures/item_texture.json')['texture_data'];data=pure_data();fixed=data['a24_skewering_core.js'];host_rows=data['a2727_cookery_host_recipes_core.js']
    categories=[]
    def cat(cid,title,icon,parent=None):
        r={'id':cid,'title':title,'icon':icon}
        if parent:r['parent']=parent
        categories.append(r)
    root_icons={'workstations':'guide_grill','food_encyclopedia':'beef_cooked','tools_gear':'guide_seasoning','storage_utilities':'big_vat','farming_harvesting':'canola_stage_7','progression_guide':'guide_recipe_book'}
    for cid,icon in root_icons.items():cat(cid,{l:host_lang[l]['strings'][cid] for l in LOCALES},'textures/ui/kg_grilling/'+icon)
    foodcats=[('food_grill',tri('烧烤架','燒烤架','Grill'),'grilled_beef_skewer'),('food_threading',tri('手工穿串','手工穿串','Hand Threading'),'raw_beef_skewer'),('food_wok',tri('炒锅','炒鍋','Wok'),'houttuynia_stir_fried_pork'),('food_stockpot',tri('汤锅','湯鍋','Stockpot'),'potato_beef_stew'),('food_crafting',tri('合成与加热','合成與加熱','Crafting & Heating'),'roasted_sweet_potato'),('food_board',tri('砧板加工','砧板加工','Chopping Board'),'beef_chunks'),('food_mill',tri('磨石加工','磨石加工','Millstone'),'canola_powder'),('food_other',{l:host_lang[l]['strings']['ingredients_other'] for l in LOCALES},'sichuan_pepper')]
    for cid,title,short in foodcats:cat(cid,title,'textures/ui/kg_grilling/catalog/'+short,'food_encyclopedia')
    entries={};icon_sources={};issues=[]
    excluded=[NS+x for x in ('canola_oil_brush','secret_chili_oil_brush','premium_chili_oil_brush')]
    def entry(iid,cats,icon=None,title=None):
        if iid in entries:raise ValueError('Duplicate page '+iid)
        short=iid.split(':')[1]
        r={'id':iid,'categories':list(cats),'title':title or {l:names[l].get(iid,iid) for l in LOCALES},'body':{l:[] for l in LOCALES},'kinds':['item'],'recipes':[],'source_refs':[],'acquisition':'unverified'}
        if iid in items:
            path,obj=items[iid];c=obj['components'];raw=c.get('minecraft:icon',{});key=raw.get('textures',{}).get('default') if isinstance(raw,dict) else raw
            tex=atlas[key]['textures'];tex=tex[0] if isinstance(tex,list) else tex;src=RP/(tex if tex.endswith('.png') else tex+'.png')
            if not src.is_file():raise ValueError('Missing item icon '+str(src))
            dest='textures/ui/kg_grilling/catalog/'+short
            icon_sources[dest]={'source':src.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'item':iid,'atlas_key':key}
            r['icon']=dest;r['stack']=c.get('minecraft:max_stack_size',64);r['source_refs'].append(path.relative_to(ROOT).as_posix())
            if c.get('minecraft:block_placer'):r['kinds'].append('block')
            f=c.get('minecraft:food')
            if f and f.get('nutrition',0)>0:
                r['food']={'nutrition':f['nutrition'],'saturation':round(2*f['nutrition']*f['saturation_modifier'],4)}
                r['food_source']={'nutrition':f['nutrition'],'saturation_modifier':f['saturation_modifier']}
        else:
            r['icon']=icon
            if iid in blocks:r['kinds']=['item','block'];r['source_refs'].append(blocks[iid][0].relative_to(ROOT).as_posix())
        if not r.get('icon'):raise ValueError('No icon '+iid)
        entries[iid]=r;return r
    def text(r,ts):
        for l in LOCALES:r['body'][l].append(ts[l])
    def borrow(r,key,indices=None):
        e=old_entries[key]
        for l in LOCALES:
            body=e['body'][l];r['body'][l].extend(body if indices is None else [body[i] for i in indices])
        r['source_refs'].append('projects/grilling/guide/content.a2.json#'+key)
    def known(r,source):r['acquisition']='verified';r['source_refs'].append('projects/grilling/gameplay_core/behavior_pack/'+source)
    def rec(r,method,ingredients,count=1,time=0,result=None,source=None):
        r['recipes'].append({'method':method,'ingredients':ingredients,'count':count,'time':time,'result':result or r['id']});known(r,source or 'scripts/a24_skewering_core.js')
    board={'beef_chunks','carrot_dice','potato_slice','raw_mantou_slice','minced_houttuynia','raw_sweet_potato_sheet','chicken_skin'}
    mill={'canola_powder','onion_powder','sweet_potato_powder','red_chili_powder'}
    wok={'houttuynia_stir_fried_pork','green_pepper_squid_tentacles','braised_chicken_wings'}
    soup={'potato_beef_stew','red_sweet_potato_porridge','sour_spicy_noodles'}
    crafted={'roasted_chicken_wing','roasted_sweet_potato','sugared_tomato','pepper_honey','cold_houttuynia','wedding_candy'}
    storage={'advanced_rack','skewer_plate','canola_oil_bucket','secret_chili_oil_bucket','premium_chili_oil_bucket'}
    farm={'canola_seeds','houttuynia','onion','sweet_potato','sichuan_pepper','oil_residue'}
    tools={'empty_seasoning_bottle','pending_seasoning','special_seasoning'}
    for iid in sorted(items):
        if iid in excluded:continue
        sh=iid.split(':')[1]
        if sh.startswith('grilled_') or sh in {'dark_grilling','mysterious_skewer'}:cs=['food_grill']
        elif sh.endswith('_skewer'):cs=['food_threading']
        elif sh in board:cs=['food_board']
        elif sh in mill:cs=['food_mill']
        elif sh in wok:cs=['food_wok']
        elif sh in soup:cs=['food_stockpot']
        elif sh in crafted:cs=['food_crafting']
        elif sh in storage:cs=['storage_utilities']
        elif sh in tools:cs=['tools_gear']
        elif sh=='skewer_recipe_book':cs=['progression_guide']
        else:cs=['food_other']
        if sh in farm:cs.append('farming_harvesting')
        if sh=='wedding_candy':cs.append('progression_guide')
        entry(iid,cs)
    for sh,icon,cs in [('grill','grill_legged_lit',['workstations']),('oil_press','oil_press',['workstations']),('big_vat','big_vat',['storage_utilities'])]:entry(NS+sh,cs,'textures/ui/kg_grilling/'+icon)
    p=entry(NS+'pepper_sapling',['farming_harvesting'],'textures/ui/kg_grilling/catalog/sichuan_pepper')
    p['related_ids']=[NS+'pepper_log',NS+'pepper_leaves'];p['title']=tri('花椒树','花椒樹','Sichuan Pepper Tree')
    plant_key=blocks[NS+'pepper_sapling'][1]['components']['minecraft:material_instances']['*']['texture'];plant_tex=load(RP/'textures/terrain_texture.json')['texture_data'][plant_key]['textures']
    plant_src=RP/(plant_tex+'.png');p['icon']='textures/ui/kg_grilling/catalog/pepper_sapling'
    icon_sources[p['icon']]={'source':plant_src.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(plant_src.read_bytes()).hexdigest(),'item':NS+'pepper_sapling','atlas_key':plant_key,'plant_sprite':True}
    borrow(p,'guide_pepper_tree');known(p,'scripts/a2748_pepper_tree_runtime.js')
    text(p,tri('取得：破坏花椒树叶可能掉落树苗；剪刀或精准采集可取得叶块。花椒原木可合成 4 块橡木木板。','取得：破壞花椒樹葉可能掉落樹苗；剪刀或精準採集可取得葉塊。花椒原木可合成 4 塊橡木木板。','Acquisition: pepper leaves can drop saplings; shears or Silk Touch recover the leaf block. A pepper log crafts into 4 oak planks.'))
    text(entries[NS+'skewer_plate'],tri('取得：主手持烤串，潜行对桌子或实心方块的顶面使用，可放成烤串盘；回收时保留盘内内容。','取得：主手持烤串，潛行對桌子或實心方塊的頂面使用，可放成烤串盤；回收時保留盤內內容。','Acquisition: sneak-use a main-hand skewer on the top of a table or solid block to place a skewer plate. Recovering the plate preserves its contents.'));known(entries[NS+'skewer_plate'],'scripts/a25_plate_recipe_runtime.js')
    text(entries[NS+'skewer_recipe_book'],tri('取得：主手持 Cookery 空白食谱、副手持完整生串并使用，会消耗一份空白食谱，得到已记录的串谱；生串不消耗。','取得：主手持 Cookery 空白食譜、副手持完整生串並使用，會消耗一份空白食譜，得到已記錄的串譜；生串不消耗。','Acquisition: use a Cookery blank recipe in the main hand with a complete raw skewer in the off hand. One blank recipe becomes a recorded skewer recipe book; the skewer is not consumed.'));known(entries[NS+'skewer_recipe_book'],'scripts/a25_plate_recipe_runtime.js')
    p=entries[NS+'grill'];borrow(p,'guide_quick_start');borrow(p,'guide_grill_timing',[1,2,3])
    text(p,tri('中途破坏：未刷油返生串；正常完成返熟串；过熟返黑暗烧烤；其它已刷油中间阶段返谜之烧烤。','中途破壞：未刷油返生串；正常完成返熟串；過熟返黑暗燒烤；其它已刷油中間階段返謎之燒烤。','Breaking mid-process: unoiled returns raw skewers; completed returns cooked; overcooked returns Dark Grilling; other oiled intermediate stages return Mysterious Skewers.'))
    for sh,oldkey in [('oil_press','guide_oil_press'),('big_vat','guide_big_vat'),('advanced_rack','guide_advanced_rack'),('skewer_plate','guide_plate'),('skewer_recipe_book','guide_recipe_book')]:borrow(entries[NS+sh],oldkey)
    for sh in tools:borrow(entries[NS+sh],'guide_seasoning_base')
    for sh in ('pending_seasoning','special_seasoning'):known(entries[NS+sh],'scripts/main.js')
    for sh,key in [('houttuynia_powder','guide_seasoning_houttuynia'),('totem_powder','guide_seasoning_totem'),('dragon_egg_powder','guide_seasoning_dragon'),('sichuan_pepper','guide_seasoning_pepper')]:borrow(entries[NS+sh],key)
    for sh,key,ico in [('redstone','guide_seasoning_redstone','textures/items/redstone_dust'),('gunpowder','guide_seasoning_gunpowder','textures/items/gunpowder')]:
        p=entry('minecraft:'+sh,['food_other'],ico);borrow(p,key);known(p,'scripts/a2743_seasoning_contract_core.js');p['acquisition']='host_owned'
    for sh in ('green_chili_powder','onion_powder'):text(entries[NS+sh],tri('用途：特制调料的三种基础料之一；每瓶至少加入青辣椒粉、花椒、洋葱粉各 1 份。','用途：特製調料的三種基礎料之一；每瓶至少加入青辣椒粉、花椒、洋蔥粉各 1 份。','Use: one of the three required seasoning bases. Each bottle needs at least one Green Chili Powder, Sichuan Pepper and Onion Powder.'))
    for sh in ('canola_oil_bucket','secret_chili_oil_bucket','premium_chili_oil_bucket'):
        p=entries[NS+sh];borrow(p,'guide_world_oil');borrow(p,'guide_hot_food',[0])
        text(p,tri('使用：以油桶向大缸或 Cookery 油壶转移；刷烤架用装油的油壶，不是旧版油刷。','使用：以油桶向大缸或 Cookery 油壺轉移；刷烤架用裝油的油壺，不是舊版油刷。','Use: transfer oil with buckets, vats and the Cookery Oil Pot. Brush the grill with the filled Oil Pot, not a legacy oil brush.'))
    known(entries[NS+'canola_oil_bucket'],'scripts/a26_oil_machine_runtime.js')
    text(entries[NS+'canola_oil_bucket'],tri('取得：榨油器完成一批后，从接收菜籽油的大缸用桶取出。','取得：榨油器完成一批後，從接收菜籽油的大缸用桶取出。','Acquisition: collect it with a bucket from the vat receiving a completed oil-press batch.'))
    borrow(entries[NS+'cold_houttuynia'],'guide_cold_houttuynia');known(entries[NS+'cold_houttuynia'],'scripts/a2722_cold_houttuynia_runtime.js')
    borrow(entries[NS+'secret_skewer'],'guide_secret_skewer');known(entries[NS+'secret_skewer'],'scripts/a24_skewering_core.js')
    borrow(entries[NS+'unfinished_skewer'],'guide_threading');known(entries[NS+'unfinished_skewer'],'scripts/a24_skewering_core.js')
    borrow(entries[NS+'ordinary_skewer'],'guide_ordinary_challenge')
    for sh,key in [('dark_grilling','guide_overcook_break'),('mysterious_skewer','guide_overcook_break')]:borrow(entries[NS+sh],key,[2 if sh=='dark_grilling' else 3]);known(entries[NS+sh],'scripts/main.js')
    text(entries[NS+'dark_grilling'],tri('食用副作用：失明约 10 秒。','食用副作用：失明約 10 秒。','Eating side effect: Blindness for about 10 seconds.'))
    text(entries[NS+'mysterious_skewer'],tri('食用副作用：反胃约 5 秒。','食用副作用：反胃約 5 秒。','Eating side effect: Nausea for about 5 seconds.'))
    for row in fixed:
        raw=entries[row['id']];typ=row['id'].split(':')[1].removeprefix('raw_').removesuffix('_skewer');oldkey='guide_recipe_'+typ
        if oldkey not in old_entries:raise ValueError('Missing recipe evidence '+oldkey)
        borrow(raw,oldkey,[0]);borrow(raw,'guide_threading',[0,2]);known(raw,'scripts/a24_skewering_core.js')
        for combo in itertools.product(*row['slots']):rec(raw,'Hand Threading',['minecraft:stick',*combo])
        if row['cooked']:
            cooked=entries[row['cooked']];borrow(cooked,oldkey,[1]);borrow(cooked,'guide_quick_start',[1,2,3]);borrow(cooked,'guide_hot_food',[1,2]);rec(cooked,'Grill',[row['id']],source='scripts/core_logic.js')
            text(cooked,{l:tri('原料串：','原料串：','Raw skewer: ')[l]+names[l][row['id']] for l in LOCALES})
            text(raw,{l:tri('用途：按烧烤架流程制成','用途：按燒烤架流程製成','Use: follow the grill process to make ')[l]+names[l][row['cooked']] for l in LOCALES})
        if typ in {'caterpillar','ender_pearl','slime'}:text(raw,tri('生吃警告：反胃约 3 秒。','生吃警告：反胃約 3 秒。','Raw-food warning: Nausea for about 3 seconds.'))
        raw['fixed_recipe_id']=row['id']
    tag_names={'minecraft:logs':tri('任意原木','任意原木','Any log'),'minecraft:wooden_slabs':tri('任意木台阶','任意木半磚','Any wooden slab')}
    for path in sorted((BP/'recipes').glob('*.json')):
        doc=load(path);key=next(k for k in doc if k.startswith('minecraft:recipe_'));rr=doc[key]
        result=rr.get('result',rr.get('output'));iid=result if isinstance(result,str) else result.get('item')
        if iid not in entries:continue
        r=entries[iid];known(r,'recipes/'+path.name);r['recipe_sources']=r.get('recipe_sources',[])+[path.relative_to(ROOT).as_posix()]
        if key.endswith('shaped'):
            def label(v,l):return tag_names[v['tag']][l] if 'tag' in v else names[l].get(v['item'],v['item'])
            text(r,{l:tri('工作台图样（空位为 ·）：\n','工作台圖樣（空位為 ·）：\n','Crafting-table pattern (· = empty):\n')[l]+'\n'.join(line.replace(' ','·') for line in rr['pattern'])+'\n'+'；'.join(k+' = '+label(v,l) for k,v in rr['key'].items()) for l in LOCALES})
        elif key.endswith('shapeless'):rec(r,'Crafting',[x['item'] for x in rr['ingredients']],result.get('count',1),source='recipes/'+path.name)
        elif key.endswith('furnace'):
            methods={'furnace':'Furnace','smoker':'Smoker','campfire':'Campfire','soul_campfire':'Soul Campfire'}
            for tag in rr['tags']:rec(r,methods.get(tag,tag),[rr['input']],source='recipes/'+path.name)
    for reg in host_rows:
        rr=reg['payload']['recipe'];kind=reg['payload']['kind'];src='scripts/a2727_cookery_host_recipes_core.js'
        if kind=='millstone':
            for out in rr['outputs']:
                if out['id'] in entries:rec(entries[out['id']],'Millstone',[rr['input']],out['count'],source=src)
        elif kind=='chopping_board':
            r=entries[rr['result']];rec(r,'Chopping Board',[rr['input']],rr['count'],source=src)
            text(r,tri(f'加工：在 Cookery 砧板上用厨房刀切 {rr["cuts"]} 次。',f'加工：在 Cookery 砧板上用廚房刀切 {rr["cuts"]} 次。',f'Processing: make {rr["cuts"]} cuts with a Kitchen Knife on the Cookery Chopping Board.'))
        elif kind in {'wok','stockpot_exact'}:
            iid=rr['result'];r=entries[iid];method='Wok' if kind=='wok' else 'Stockpot'
            for combo in itertools.product(*[x if isinstance(x,list) else [x] for x in rr['ingredients']]):rec(r,method,list(combo),rr.get('count',1),rr.get('time',0),source=src)
            if method=='Stockpot':text(r,tri('操作：汤锅使用水作为汤底，配方加热 15 秒，以碗盛出。这里只列精确配方，不把灵活配方误写成随意减料。','操作：湯鍋使用水作為湯底，配方加熱 15 秒，以碗盛出。這裡只列精確配方，不把靈活配方誤寫成隨意減料。','Use water as the stockpot base; cook for 15 seconds and serve with a bowl. Exact recipes are listed; flexible recipes are not presented as reduced quantities.'))
            else:text(r,tri('操作：按 Cookery 炒锅流程加油、投入配方食材，加热 10 秒后以碗盛出。','操作：按 Cookery 炒鍋流程加油、投入配方食材，加熱 10 秒後以碗盛出。','Use the Cookery wok: add oil and the listed ingredients, cook for 10 seconds, then serve with a bowl.'))
            if reg.get('requiresItems'):
                text(r,tri('附属需求：酸辣粉的醋来自森罗物语：酒馆；没有对应醋物品时，此配方不会注册。','附屬需求：酸辣粉的醋來自森羅物語：酒館；沒有對應醋物品時，此配方不會註冊。','Add-on requirement: the vinegar comes from Kaleidoscope Tavern. Without a matching vinegar item, this recipe is not registered.'));r['requires_any_item']=reg['requiresItems']
    rec(entries[NS+'beef_chunks'],'Chopping Board',['minecraft:beef'],2,source='scripts/a279_beef_board_core.js')
    text(entries[NS+'beef_chunks'],tri('加工：用厨房刀在砧板切 4 次，得到 2 份牛肉块。','加工：用廚房刀在砧板切 4 次，得到 2 份牛肉塊。','Processing: four Kitchen Knife cuts on a Chopping Board yield two Beef Chunks.'))
    borrow(entries[NS+'chicken_skin'],'guide_chicken_processing',[0,2]);known(entries[NS+'chicken_skin'],'scripts/a2710_chicken_acquisition_runtime.js')
    borrow(entries[NS+'chicken_wing'],'guide_chicken_processing',[1,2]);known(entries[NS+'chicken_wing'],'scripts/a2710_chicken_acquisition_runtime.js')
    text(entries[NS+'squid_tentacle'],tri('取得：主手持 Cookery 厨房刀击杀普通鱿鱼，有机会掉落鱿鱼须；掠夺影响数量。','取得：主手持 Cookery 廚房刀擊殺普通魷魚，有機會掉落魷魚鬚；掠奪影響數量。','Acquisition: kill a normal squid while holding a Cookery Kitchen Knife in the main hand for a chance of tentacle drops; Looting affects the count.'));known(entries[NS+'squid_tentacle'],'scripts/a2712_remaining_knife_drops_runtime.js')
    for sh in ('canola_seeds','onion','sweet_potato'):
        text(entries[NS+sh],tri('取得与种植：戴 Cookery 草帽在生存模式打短草，有机会取得；种在耕地上，成熟后收获。','取得與種植：戴 Cookery 草帽在生存模式打短草，有機會取得；種在耕地上，成熟後收穫。','Acquisition and farming: break short grass in Survival while wearing a Cookery Straw Hat for a chance to obtain it. Plant on farmland and harvest when mature.'));known(entries[NS+sh],'scripts/a2731_farmland_crop_host_runtime.js')
    borrow(entries[NS+'canola_seeds'],'guide_canola',[0,1]);borrow(entries[NS+'sweet_potato'],'guide_sweet_potato',[0,2])
    borrow(entries[NS+'sweet_potato_powder'],'guide_sweet_potato',[1]);known(entries[NS+'raw_sweet_potato_sheet'],'scripts/a271_sweet_potato_core.js')
    text(entries[NS+'houttuynia'],tri('种植与用途：折耳根可种植；可切成碎折耳根，或用于凉拌折耳根与炒肉。初始种源请按当前世界生成情况确认。','種植與用途：折耳根可種植；可切成碎折耳根，或用於涼拌折耳根與炒肉。初始種源請按目前世界生成情況確認。','Farming and use: Houttuynia can be planted, chopped, used in Cold Houttuynia or stir-fried pork. Initial access depends on the current world-generation setup.'));known(entries[NS+'houttuynia'],'scripts/a2714_houttuynia_crop_runtime.js')
    text(entries[NS+'sichuan_pepper'],tri('取得：空手采收结果的花椒树叶，一次掉落 1–2 份。','取得：空手採收結果的花椒樹葉，一次掉落 1–2 份。','Acquisition: empty-hand harvest a fruiting pepper leaf for 1–2 Sichuan Peppers.'));known(entries[NS+'sichuan_pepper'],'scripts/a2748_pepper_tree_runtime.js')
    text(entries[NS+'oil_cake'],tri('用途：4 个油饼装满一台榨油器；完整一批产 4 桶菜籽油与 4 个油渣。','用途：4 個油餅裝滿一台榨油器；完整一批產 4 桶菜籽油與 4 個油渣。','Use: four Oil Cakes fill an Oil Press. A completed batch yields four buckets of Canola Oil and four Oil Residues.'))
    text(entries[NS+'oil_residue'],tri('取得与使用：榨油副产物；对具有受支持生长阶段的作物使用可促进生长。','取得與使用：榨油副產物；對具有受支援生長階段的作物使用可促進生長。','Acquisition and use: an oil-press by-product. Use it on crops with supported growth states to advance their growth.'));known(entries[NS+'oil_residue'],'scripts/a26_oil_machine_runtime.js')
    text(entries[NS+'wedding_candy'],tri('取得限制：代码中的活动为上海时间 2026-09-01 至 09-12；第 d 日在线累计 d 分钟发 d 颗，每日一次。不是全年可合成食品。','取得限制：程式中的活動為上海時間 2026-09-01 至 09-12；第 d 日在線累計 d 分鐘發 d 顆，每日一次。不是全年可合成食品。','Availability: the coded event runs September 1–12, 2026, Shanghai time. On day d, d minutes online awards d candies once that day. This is not a year-round crafting recipe.'));known(entries[NS+'wedding_candy'],'scripts/a2747_wedding_candy_core.js')
    effect_names={'warmth':tri('温暖','溫暖','Warmth'),'flatulence':tri('胀气','脹氣','Flatulence'),'invincible':tri('无敌','無敵','Invincibility'),'numb':tri('麻木','麻木','Numb'),'fire_resistance':tri('抗火','抗火','Fire Resistance')}
    for row in data['a2732_standalone_food_effect_core.js']:
        r=entries[row['itemId']]
        if row['itemId']==NS+'cold_houttuynia':continue
        text(r,{l:tri('食用效果：','食用效果：','Eating effects: ')[l]+'；'.join(effect_names[e['effect']][l]+' '+str(e['ticks']//20)+tri(' 秒',' 秒',' seconds')[l] for e in row['effects']) for l in LOCALES});r['source_refs'].append('projects/grilling/gameplay_core/behavior_pack/scripts/a2732_standalone_food_effect_core.js')
    for key,icon in [('guide_quick_start','guide_grill'),('guide_hot_food','guide_oil')]:
        p=entry('kg_a1:'+key,['progression_guide'],'textures/ui/kg_grilling/'+icon,title=old_entries[key]['title']);p['kinds']=[];p['acquisition']='not_applicable';borrow(p,key)
        if key=='guide_hot_food':borrow(p,'guide_storage_heat')
    for rr in fixed:
        if not rr['cooked']:continue
        raw=entries.pop(rr['id']);cooked=entries.pop(rr['cooked']);typ=rr['id'].split(':')[1].removeprefix('raw_').removesuffix('_skewer')
        family=entry('kg_a1:guide_recipe_'+typ,['food_threading','food_grill'],cooked['icon'],old_entries['guide_recipe_'+typ]['title'])
        family['related_ids']=[rr['id'],rr['cooked']];family['recipes']=raw['recipes']+cooked['recipes'];family['food']=cooked['food'];family['food_item']=rr['cooked'];family['food_source']=cooked['food_source'];family['stack']=cooked['stack']
        family['nutrition_variants']={rr['id']:raw['food'],rr['cooked']:cooked['food']};family['source_refs']=list(dict.fromkeys(raw['source_refs']+cooked['source_refs']));family['acquisition']='verified';family['fixed_recipe_id']=rr['id']
        for l in LOCALES:
            b=old_entries['guide_quick_start']['body'][l];rs=raw['food'];cs=cooked['food']
            line=tri(f'营养：主面板为熟串。生串饱食 {rs["nutrition"]} / 饱和度 {rs["saturation"]:g}；熟串饱食 {cs["nutrition"]} / 饱和度 {cs["saturation"]:g}。',f'營養：主面板為熟串。生串飽食 {rs["nutrition"]} / 飽和度 {rs["saturation"]:g}；熟串飽食 {cs["nutrition"]} / 飽和度 {cs["saturation"]:g}。',f'Nutrition panel: cooked skewer. Raw: hunger {rs["nutrition"]}, saturation {rs["saturation"]:g}; cooked: hunger {cs["nutrition"]}, saturation {cs["saturation"]:g}.')[l]
            family['body'][l]=[line,old_entries['guide_recipe_'+typ]['body'][l][0],old_entries['guide_threading']['body'][l][0]+' '+b[0],' '.join(b[1:]),old_entries['guide_recipe_'+typ]['body'][l][1],' '.join(old_entries['guide_hot_food']['body'][l][1:3]),old_entries['guide_threading']['body'][l][2]]
            if typ in {'caterpillar','ender_pearl','slime'}:family['body'][l].append(tri('生吃警告：反胃约 3 秒。','生吃警告：反胃約 3 秒。','Raw-food warning: Nausea for about 3 seconds.')[l])
    special=entries[NS+'special_seasoning'];special['related_ids']=[NS+'empty_seasoning_bottle',NS+'pending_seasoning'];special['title']=tri('调料瓶与特制调料','調料瓶與特製調料','Seasoning Bottle & Special Seasoning');special['body']={l:list(old_entries['guide_seasoning_base']['body'][l]) for l in LOCALES}
    text(special,tri('搭配：红石提供速度，火药提供力量，折耳根粉延时；不死图腾粉与龙蛋粉提供特殊效果。各材料的数量门槛见其同名条目。','搭配：紅石提供速度，火藥提供力量，折耳根粉延時；不死圖騰粉與龍蛋粉提供特殊效果。各材料的數量門檻見其同名條目。','Mixing: Redstone grants Speed, Gunpowder grants Strength, and Houttuynia Powder extends effects. Totem and Dragon Egg Powders add special effects; see their material entries for thresholds.'))
    text(special,tri('初始空瓶：当前候选未核实空调料瓶的生存取得途径；不把原作配方当作已经实装。','初始空瓶：目前候選未核實空調料瓶的生存取得途徑；不把原作配方當作已經實裝。','Initial empty bottle: no checked survival acquisition route in this candidate. An upstream recipe is not treated as implemented.'));special['initial_item_gap']=NS+'empty_seasoning_bottle'
    del entries[NS+'empty_seasoning_bottle'];del entries[NS+'pending_seasoning'];entries[NS+'skewer_plate']['title']=tri('烤串盘','烤串盤','Skewer Plate')
    oilpot=entry('kaleidoscope_cookery:oil_pot_filled',['tools_gear','storage_utilities'],'textures/items/kc_oil_pot_filled',tri('Cookery 油壶：烟火油','Cookery 油壺：煙火油','Cookery Oil Pot: Grilling Oils'))
    oilpot['acquisition']='host_owned';oilpot['related_ids']=['kaleidoscope_cookery:oil_pot']
    text(oilpot,tri('取得：这是本体油壶，不是烟火新增物品；基础油壶的制作见本体指南。以下只说明烟火油适配。','取得：這是本體油壺，不是煙火新增物品；基礎油壺的製作見本體指南。以下只說明煙火油適配。','Acquisition: this is the host Oil Pot, not a new Grilling item. See the host guide for its base recipe; this page covers Grilling oil integration only.'))
    text(oilpot,tri('烟火油容量：64 点。主手油桶配合副手油壶可灌油；也可从油源或大缸取油，每桶增加 8 点。','煙火油容量：64 點。主手油桶配合副手油壺可灌油；也可從油源或大缸取油，每桶增加 8 點。','Grilling-oil capacity: 64 points. Use a main-hand oil bucket with an offhand pot, or draw oil from a source/vat; each bucket supplies 8 points.'))
    text(oilpot,tri('刷油：用装有对应烟火油的油壶点击烤架；一次消耗量等于架上串数。不同油种不能混入同一壶。','刷油：用裝有對應煙火油的油壺點擊烤架；一次消耗量等於架上串數。不同油種不能混入同一壺。','Brushing: use the filled pot on the grill. The action costs one oil point per loaded skewer. Different oils cannot be mixed in the same pot.'))
    oilpot['source_refs']=['projects/grilling/gameplay_core/behavior_pack/scripts/a2737_offhand_oil_fill_runtime.js','projects/grilling/gameplay_core/behavior_pack/scripts/a26_oil_machine_core.js']
    used=defaultdict(set)
    for row in fixed:
        for slot in row['slots']:
            for iid in slot:used[iid].add(row['id'])
    for r in entries.values():
        for recipe in r['recipes']:
            for iid in recipe['ingredients']:
                if iid!=r['id']:used[iid].add(r['id'])
    for iid,r in entries.items():
        if not r['body']['zh_TW'] and used.get(iid):text(r,{l:tri('用途：用于','用途：用於','Used in: ')[l]+'、'.join(names[l].get(x,x) for x in sorted(used[iid])[:5]) for l in LOCALES})
        if r['acquisition']=='unverified':
            issues.append({'item':iid,'reason':'No checked acquisition path in current canonical recipes/curated runtime evidence.'})
            if len(r['body']['en_US'])>=8:
                for l in LOCALES:r['body'][l][-2:]=[' '.join(r['body'][l][-2:])]
            text(r,tri('取得说明：当前候选未核实此物品的生存合成或首份取得途径；这里不把原作配方当成已经实装。','取得說明：目前候選未核實此物品的生存合成或首份取得途徑；這裡不把原作配方當成已經實裝。','Acquisition: this candidate has no verified survival recipe or initial acquisition route for this item. An upstream recipe is not treated as implemented.'))
        if not r['body']['en_US']:text(r,tri('用途与取得：请查看本页配方；未列出额外操作或固定效果。','用途與取得：請查看本頁配方；未列出額外操作或固定效果。','Use and acquisition: see the recipes on this page. No additional interaction or fixed effect is documented.'))
        replacements={'zh_CN':{'见「进阶与排错」':'见「凉拌折耳根」','见「调料与烟火气」':'见「折耳根粉」','详见「进阶与排错」':'见本页警告'},'zh_TW':{'見「進階與排錯」':'見「涼拌折耳根」','見「調料與煙火氣」':'見「折耳根粉」','詳情先看「進階與排錯」':'先看本頁警告'},'en_US':{}}
        for l in LOCALES:
            for a,b in replacements[l].items():r['body'][l]=[x.replace(a,b) for x in r['body'][l]]
        if len(r['recipes'])>24 or any(len(v)>8 for v in r['body'].values()):raise ValueError('Host entry budget '+iid)
        for l,lines in r['body'].items():
            if any(len(x.encode('utf-16-le'))//2>512 for x in lines):raise ValueError('Host would truncate '+iid+' '+l)
    needed=set(entries)
    for r in entries.values():
        needed.update(r.get('related_ids',[]))
        for rr in r['recipes']:needed.update(rr['ingredients']);needed.add(rr['result'])
    names={l:{k:names[l][k] for k in sorted(needed) if k in names[l]} for l in LOCALES}
    for r in entries.values():
        for l in LOCALES:names[l][r['id']]=r['title'][l]
    used_icons={r['icon'] for r in [*categories,*entries.values()]};icon_sources={k:v for k,v in icon_sources.items() if k in used_icons}
    output={'schema_version':3,'version':'0.3.0','revision':'a3_0_0','module_id':'kg_a1:grilling','order':300,'icon':'textures/ui/kg_grilling/guide_grill','locales':list(LOCALES),'fallback_locale':'zh_TW','showAll':False,'showIds':False,'showKinds':False,'showCategoryOnEntry':False,
      'ui':{l:{**old['ui'][l],'intro':tri('按物品类型与制作方式查阅；每项合并取得、配方、操作与效果。','按物品類型與製作方式查閱；每項合併取得、配方、操作與效果。','Browse by item type and preparation method. Acquisition, recipes, use and effects share one entry.')[l],'select':tri('选择分类；食物按制作方式分组。','選擇分類；食物按製作方式分組。','Choose a category; foods are grouped by preparation method.')[l]} for l in LOCALES},
      'categories':categories,'entries':list(entries.values()),'names':names,'icon_sources':icon_sources,'excluded_items':excluded,'host_reference':{'version':'1.0.6','guide_path':'scripts/events/guidebook.js','guide_sha256':digest,'root_category_ids':list(root_icons),'supported_shape':'root categories, one child layer, multi-category entries; no host UI override'},'acquisition_gaps':issues}
    for l in LOCALES:output['ui'][l]['food_groups_body']=tri('按制作方式查找食物与原料；同一烤串的生熟信息在同一页。','按製作方式查找食物與原料；同一烤串的生熟資訊在同一頁。','Find food and ingredients by preparation method. Raw and cooked skewer details share one page.')[l]
    dump(GUIDE/'catalog.a3.json',output)
    print(json.dumps({'entries':len(entries),'categories':len(categories),'roots':len(root_icons),'copied_item_icons':len(icon_sources),'acquisition_gaps':len(issues)},indent=2))
if __name__=='__main__':main()
