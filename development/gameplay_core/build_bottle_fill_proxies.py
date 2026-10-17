"""Hidden fill-only inventory proxies; mechanics remain canonical EMPTY/PENDING.

Static sprites use the pinned Java pending_8 shell/fill geometry and GUI pose.
The fixed brown preview palette communicates amount, never arbitrary ingredient
colors. Held/placed ingredient colors remain dynamic. No native client claim.
"""
from copy import deepcopy
from pathlib import Path
import argparse, hashlib, io, json
from PIL import Image
import a281_bottle_icons as sprites

ROOT=Path(__file__).resolve().parents[2]
BP=ROOT/'projects/grilling/gameplay_core/behavior_pack'
RP=sprites.RP
NS='kaleidoscope_grilling:'
SOURCE=ROOT/'development/gameplay_core/fixtures/a2770/grilling/kaleidoscope_grilling/models/item/seasoning_states/pending_8.json'
SOURCE_SHA256='ee7cc9297c08610291db9ff21db647f33f02aa4261fa4e60871b5a5222ffd7e3'
GENERIC_PALETTE=(0xB86B45,0xE0A56A)
STATES=tuple((kind,fill) for kind in ['partial','pending'] for fill in range(1,9))
def load(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def name_for(kind,fill):
    assert (kind,fill) in STATES
    return f'{kind}_seasoning_f{fill}'
def fill_model(fill):
    assert 1<=fill<=8
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA256
    doc=load(SOURCE)
    doc['elements']=[e for e in doc['elements'] if not any(f.get('tintindex',-1)>=fill*2 for f in e['faces'].values())]
    return doc

def fill_faces(fill):
    doc=fill_model(fill)
    shell=deepcopy(doc);shell['elements']=[e for e in doc['elements'] if not any('tintindex' in f for f in e['faces'].values())]
    faces=sprites.make_faces(shell)
    # Convert geometry/GUI projection using the same renderer. Replace only the
    # sampled fill-face texels with an explicitly generic opaque palette.
    for e in doc['elements']:
        tint=next((f['tintindex'] for f in e['faces'].values() if 'tintindex' in f),None)
        if tint is None:continue
        part=deepcopy(doc);part['elements']=[deepcopy(e)]
        for face in part['elements'][0]['faces'].values():face['texture']='#0'
        color=GENERIC_PALETTE[tint%2]
        texture=Image.new('RGBA',(32,32),((color>>16)&255,(color>>8)&255,color&255,255))
        faces.extend((points,uv,texture) for points,uv,_ in sprites.make_faces(part))
    return faces

def images():return {name_for(kind,fill):sprites.render(fill_faces(fill)) for kind,fill in STATES}
def documents():
    result={}
    for kind,fill in STATES:
        name=name_for(kind,fill);base='empty_seasoning_bottle' if kind=='partial' else 'pending_seasoning'
        item=load(BP/'items'/f'{base}.json');item['minecraft:item']['description'].update(identifier=NS+name,menu_category={'category':'none'})
        item['minecraft:item']['components']['minecraft:icon']['textures']['default']=name
        result[BP/'items'/f'{name}.json']=item
        recipe=load(BP/'recipes'/f'clear_{base}.json');r=recipe['minecraft:recipe_shapeless'];r['description']['identifier']=NS+'clear_'+name
        r['ingredients']=[{'item':NS+name}];r['unlock']=[{'item':NS+name}]
        result[BP/'recipes'/f'clear_{name}.json']=recipe
    return result

def build(check=False):
    for path,doc in documents().items():
        if check:assert load(path)==doc,path
        else:path.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
    for name,image in images().items():
        path=RP/'textures/items'/f'{name}.png'
        if check:
            with Image.open(path) as actual:assert actual.convert('RGBA').tobytes()==image.tobytes(),path
        else:image.save(path,compress_level=9)
    # Always merge from the latest atlas; finished variants have another owner.
    atlas_path=RP/'textures/item_texture.json';atlas=load(atlas_path)
    for kind,fill in STATES:
        name=name_for(kind,fill);entry={'textures':'textures/items/'+name}
        if check:assert atlas['texture_data'][name]==entry,name
        else:atlas['texture_data'][name]=entry
    if not check:atlas_path.write_text(json.dumps(atlas,ensure_ascii=False,indent=2)+'\n')
    return {'fill_proxies':len(STATES),'source_sha256':SOURCE_SHA256,'inventory_palette':'generic fixed amount preview; ingredient colors remain dynamic only in held/placed view','minecraft_tested':False}
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args();print(json.dumps(build(args.check),indent=2))
