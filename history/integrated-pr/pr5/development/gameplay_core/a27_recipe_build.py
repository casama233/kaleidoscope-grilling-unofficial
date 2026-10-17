from __future__ import annotations
import hashlib,json,urllib.request
from pathlib import Path

UP='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
PREFIX='common/src/main/resources/data/kaleidoscope_grilling/recipes/'

def blob(v:bytes)->str:return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def load(p:Path):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p:Path,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def fetch_recipe(row):
    path=PREFIX+row['path']
    req=urllib.request.Request(UP+path,headers={'User-Agent':'Grilling-A2.7/1'})
    with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
    if blob(v)!=row['sha']:raise RuntimeError('pinned recipe mismatch '+row['path'])
    return json.loads(v.decode('utf-8-sig'))

def shaped(identifier,pattern,key,result,count=1):
    return {'format_version':'1.20.10','minecraft:recipe_shaped':{
        'description':{'identifier':'kaleidoscope_grilling:'+identifier},'tags':['crafting_table'],
        'pattern':pattern,'key':key,'result':{'item':result,'count':count}
    }}
def shapeless(identifier,ingredients,result):
    return {'format_version':'1.20.10','minecraft:recipe_shapeless':{
        'description':{'identifier':'kaleidoscope_grilling:'+identifier},'tags':['crafting_table'],
        'ingredients':ingredients,'result':result
    }}
def furnace(identifier,input_id,output_id):
    return {'format_version':'1.20.10','minecraft:recipe_furnace':{
        'description':{'identifier':'kaleidoscope_grilling:'+identifier},
        'tags':['furnace','smoker','campfire','soul_campfire'],'input':input_id,'output':output_id
    }}

def build_native(BP:Path):
    R=BP/'recipes';R.mkdir(parents=True,exist_ok=True)
    # Reconcile the three A2.6 machine recipes to the actual Java ingredient intent.
    write(R/'big_vat.json',shaped('big_vat',['B B','BUB','BBB'],{
        'B':{'item':'minecraft:brick'},'U':{'item':'minecraft:bucket'}
    },'kaleidoscope_grilling:big_vat'))
    write(R/'oil_cake.json',shaped('oil_cake',['PPP','PWP','PPP'],{
        'P':{'item':'kaleidoscope_grilling:canola_powder'},'W':{'item':'minecraft:wheat'}
    },'kaleidoscope_grilling:oil_cake'))
    write(R/'oil_press.json',shaped('oil_press',['LIL','F F','LHL'],{
        'L':{'tag':'minecraft:logs'},'I':{'item':'minecraft:iron_ingot'},
        # Bedrock has no stable vanilla recipe-input tag equivalent to Java minecraft:fences.
        'F':{'item':'minecraft:oak_fence'},'H':{'item':'minecraft:hopper'}
    },'kaleidoscope_grilling:oil_press'))

    write(R/'grill.json',shaped('grill',['III','BCB','I I'],{
        'I':{'item':'minecraft:iron_ingot'},'B':{'item':'minecraft:brick'},'C':{'tag':'minecraft:coals'}
    },'kaleidoscope_grilling:grill'))
    write(R/'empty_seasoning_bottle.json',shaped('empty_seasoning_bottle',[' B ','GGG','GGG'],{
        # Java accepts all wooden buttons/colorless glass; stable Bedrock recipe tags do not expose those groups.
        'B':{'item':'minecraft:oak_button'},'G':{'item':'minecraft:glass'}
    },'kaleidoscope_grilling:empty_seasoning_bottle'))

    write(R/'pepper_honey.json',shapeless('pepper_honey',[
        {'item':'kaleidoscope_grilling:sichuan_pepper'},{'item':'kaleidoscope_grilling:sichuan_pepper'},
        {'item':'kaleidoscope_grilling:sichuan_pepper'},{'item':'minecraft:honey_bottle'}
    ],[
        {'item':'kaleidoscope_grilling:pepper_honey','count':1},{'item':'minecraft:glass_bottle','count':1}
    ]))
    write(R/'sugared_tomato.json',shapeless('sugared_tomato',[
        {'item':'kaleidoscope_cookery:tomato'},{'item':'minecraft:sugar'}
    ],{'item':'kaleidoscope_grilling:sugared_tomato','count':1}))
    write(R/'secret_chili_oil.json',shapeless('secret_chili_oil',[
        {'item':'kaleidoscope_grilling:canola_oil_bucket'},
        {'item':'kaleidoscope_grilling:red_chili_powder'},{'item':'kaleidoscope_grilling:red_chili_powder'},{'item':'kaleidoscope_grilling:red_chili_powder'}
    ],[
        {'item':'kaleidoscope_grilling:secret_chili_oil_bucket','count':1},{'item':'minecraft:bucket','count':1}
    ]))
    write(R/'premium_chili_oil.json',shapeless('premium_chili_oil',[
        {'item':'kaleidoscope_grilling:secret_chili_oil_bucket'},{'item':'minecraft:lava_bucket'},
        {'item':'minecraft:redstone'},{'item':'kaleidoscope_grilling:houttuynia_powder'}
    ],[
        {'item':'kaleidoscope_grilling:premium_chili_oil_bucket','count':1},{'item':'minecraft:bucket','count':2}
    ]))

    # Java clear recipe outputs Cookery recipe_item. Cookery Bedrock 1.0.6's observed public item registry
    # does not expose that ID, so A2.7 clears the dynamic book by crafting it into a fresh blank book.
    write(R/'clear_skewer_recipe_book.json',shapeless('clear_skewer_recipe_book',[
        {'item':'kaleidoscope_grilling:skewer_recipe_book'}
    ],{'item':'kaleidoscope_grilling:skewer_recipe_book','count':1}))
    for suffix,item in [('pending','kaleidoscope_grilling:pending_seasoning'),('special','kaleidoscope_grilling:special_seasoning'),('data_bottle','kaleidoscope_grilling:empty_seasoning_bottle')]:
        write(R/f'clear_seasoning_{suffix}.json',shapeless('clear_seasoning_'+suffix,[{'item':item}],{'item':'kaleidoscope_grilling:empty_seasoning_bottle','count':1}))

    # Bedrock furnace recipes have station tags but no Java-equivalent per-recipe cookingtime/experience fields.
    write(R/'roasted_chicken_wing.json',furnace('roasted_chicken_wing','kaleidoscope_grilling:chicken_wing','kaleidoscope_grilling:roasted_chicken_wing'))
    write(R/'roasted_sweet_potato.json',furnace('roasted_sweet_potato','kaleidoscope_grilling:sweet_potato','kaleidoscope_grilling:roasted_sweet_potato'))

def build_catalog(DEV:Path,BP:Path,P:Path):
    manifest=load(DEV/'a27_recipe_sources.json')
    if manifest.get('count')!=61 or len(manifest.get('recipes',[]))!=61:raise RuntimeError('A2.7 recipe source manifest must contain exactly 61 rows')
    docs={row['path']:fetch_recipe(row) for row in manifest['recipes']}
    def cls(path):
        if path in {'stockpot/sour_spicy_noodles.json','flex_stockpot/sour_spicy_noodles.json'}:return 'tavern_conditional'
        if path.startswith(('crushing/','milling/','filling/','mixing/')):return 'create_optional'
        if path in {'clear_seasoning.json','cold_houttuynia.json','skewer_recipe_book.json'}:return 'grilling_custom'
        if path.startswith(('chopping_board/','millstone/','pot/','flex_pot/','stockpot/','flex_stockpot/')):return 'cookery_machine'
        return 'vanilla_direct'
    rows=[{'path':p,'class':cls(p),'source':docs[p]} for p in sorted(docs)]
    cookery=[r for r in rows if r['class']=='cookery_machine']
    js='export const A27_COOKERY_RECIPES=Object.freeze('+json.dumps(cookery,ensure_ascii=False,separators=(',',':'))+');\n'
    (BP/'scripts/a27_cookery_recipes.js').write_text(js,encoding='utf-8')
    write(P/'reports/a27-java-recipes.json',{
        'version':'A2.7.0','baseline':manifest['java_baseline'],'count':61,
        'counts':{
            'vanilla_direct':sum(r['class']=='vanilla_direct' for r in rows),
            'cookery_machine':sum(r['class']=='cookery_machine' for r in rows),
            'tavern_conditional':sum(r['class']=='tavern_conditional' for r in rows),
            'create_optional':sum(r['class']=='create_optional' for r in rows),
            'grilling_custom':sum(r['class']=='grilling_custom' for r in rows)
        },
        'rows':rows,
        'core_cookery_catalog_count':len(cookery),
        'cookery_runtime_registration_bound':False,
        'cookery_registration_note':'Exact KC_EXTENSION_API register_recipe payload schema must be verified from Cookery 1.0.6 package before publishing; raw pinned Java recipe contracts are generated now so publisher/fallback share one source.',
        'native_bedrock_generated':[
            'big_vat','oil_cake','oil_press','grill','empty_seasoning_bottle','pepper_honey','sugared_tomato',
            'secret_chili_oil','premium_chili_oil','clear_skewer_recipe_book','clear_seasoning_pending',
            'clear_seasoning_special','clear_seasoning_data_bottle','roasted_chicken_wing','roasted_sweet_potato'
        ],
        'deferred_inputs_or_outputs':['advanced_rack.json','oak_planks_from_pepper_log.json'],
        'dynamic_custom':['cold_houttuynia.json'],
        'already_runtime_custom':['skewer_recipe_book.json'],
        'create_optional_count':16
    })

def build_all(DEV:Path,BP:Path,P:Path):
    build_native(BP);build_catalog(DEV,BP,P)
