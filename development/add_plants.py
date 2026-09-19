"""Add pinned fish-mint and pepper display assets; no gameplay/worldgen claims."""
from __future__ import annotations
import base64, collections, copy, hashlib, io, json, math, os, re, sys, urllib.request, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'projects/grilling'
SHA = '9a1acdab27698457bec16c9362678e574895a28c'
PREFIX = 'common/src/main/resources/assets/'
NS = 'kaleidoscope_grilling'

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def sha(value): return hashlib.sha256(value).hexdigest()
def blob(value): return hashlib.sha1(b'blob '+str(len(value)).encode()+b'\0'+value).hexdigest()
def output_set():
    patterns=('resource_pack/models/entity/kg_a1/*.geo.json','editor/generated/*.bbmodel','resource_pack/textures/kg_a1/*.png')
    return {x.relative_to(P).as_posix():sha(x.read_bytes()) for pat in patterns for x in P.glob(pat)}

def get(url):
    request=urllib.request.Request(url,headers={'User-Agent':'Grilling-pinned-assets/1'})
    with urllib.request.urlopen(request,timeout=120) as r:return r.read(150_000_000)

# Templates are exact Minecraft 1.20.1 references served by an identified mirror.
# Their hashes pin bytes even if the mirror branch moves. They are not CC assets.
TEMPLATES={
 'crop':'1afe355cd203b0a6b432efd0587350bb981d3c83',
 'cube_column':'358b9847efe8bb17811ef48eedd219d8c9b51499',
 'cube':'1b9780b479aee527f79bde950656b82f1524128b',
 'block':'aefa892bfd7917a89c56d623aac8556cf80694ec',
 'leaves':'722173fdfa1ae2c081f8ac01e9c235e7057b4527',
 'cross':'37c8b09f251c5f319905ee14787be1442775e816',
}

NORMALIZER='''"""Explicitly selected Java reference-template lowering. No source mutation."""
import copy, math

def prepare(model, allow_unapplied_tint=False):
    out=copy.deepcopy(model); warnings=[]
    for index, element in enumerate(out['elements']):
        original_from=element['from'][:]; original_to=element['to'][:]
        for face, data in element['faces'].items():
            if 'uv' not in data:
                if original_from != [0,0,0] or original_to != [16,16,16]:
                    raise ValueError('Implicit UV outside verified full-cube scope')
                data['uv']=[0,0,16,16]
                warnings.append({'code':'FULL_CUBE_IMPLICIT_UV_MATERIALIZED','element':index,'face':face})
            if 'tintindex' in data:
                if not allow_unapplied_tint:
                    raise ValueError('Tint needs explicit unresolved-material permission')
                warnings.append({'code':'SOURCE_TINT_REQUIRES_ENGINE_BINDING','element':index,'face':face,'tintindex':data.pop('tintindex'),'applied':False})
        rotation=element.get('rotation',{})
        if rotation.get('rescale'):
            if rotation['angle'] not in (-45,-22.5,0,22.5,45):
                raise ValueError('Unsupported Java rescale angle')
            axis='xyz'.index(rotation['axis']); pivot=rotation['origin']
            factor=1/math.cos(math.radians(rotation['angle']))
            for key in ('from','to'):
                element[key]=[pivot[i]+(v-pivot[i])*(1 if i==axis else factor) for i,v in enumerate(element[key])]
            rotation['rescale']=False
            warnings.append({'code':'JAVA_RESCALE_BAKED_BEFORE_ROTATION','element':index,'factor':factor})
    return out,warnings
'''

def replace_once(text, old, new):
    if text.count(old)!=1:raise RuntimeError('Unexpected tool revision; refusing blind patch: '+old[:70])
    return text.replace(old,new,1)

def install_template_support():
    build=P/'tools/build_assets.py'; text=build.read_text()
    if 'reference_templates' in text:raise RuntimeError('Template support already installed')
    text=replace_once(text,'    if identifier in chain or len(chain) >= 48:',
       '    if isinstance(identifier, str) and ":" not in identifier:\n        identifier = "minecraft:" + identifier\n    if identifier in chain or len(chain) >= 48:')
    text=replace_once(text,'        uv_model, uv_changes = lower_uv_half_turns(original, allow_quarter_turns=native)',
       '        prepared, template_warnings = original, []\n        if spec.get("reference_template"):\n            from reference_templates import prepare\n            prepared, template_warnings = prepare(original, spec.get("source_tint_pending", False))\n        uv_model, uv_changes = lower_uv_half_turns(prepared, allow_quarter_turns=native)')
    text=replace_once(text,'+ metadata_warnings(original)','+ metadata_warnings(original) + template_warnings')
    build.write_text(text)
    (P/'tools/reference_templates.py').write_text(NORMALIZER)
    audit=P/'tools/audit_multiview.py'; text=audit.read_text()
    text=replace_once(text,' ns,name=identifier.split(\':\',1)', ' ns,name=identifier.split(\':\',1)') # anchor check
    needle=' if not isinstance(identifier,str) or not re.fullmatch'
    text=replace_once(text,needle,' if isinstance(identifier,str) and ":" not in identifier:identifier="minecraft:"+identifier\n'+needle)
    text=replace_once(text,"    tex=textures[ref];uv=rectangle(f['uv'])", "    tex=textures[ref]\n    if 'uv' not in f:\n     if e['from'] != [0,0,0] or e['to'] != [16,16,16]:raise ValueError('Implicit source UV outside full cube')\n     uv=rectangle([0,0,16,16])\n    else:uv=rectangle(f['uv'])")
    text=replace_once(text,"    points=(vertices(e['from'],e['to'],face)-pivot)@mat.T+pivot+offset", "    relative=vertices(e['from'],e['to'],face)-pivot\n    if r.get('rescale'):\n     factors=np.full(3,1/np.cos(np.radians(r['angle'])));factors['xyz'.index(r['axis'])]=1\n     relative=relative*factors\n    points=relative@mat.T+pivot+offset")
    audit.write_text(text)

def main():
    guard=json.loads((ROOT/'.repo-target.json').read_text())
    if guard['repository']!='casama233/kaleidoscope-grilling-unofficial' or guard['repository_id']!=1377218440:raise RuntimeError('Wrong repository')
    specs=json.loads((P/'config/asset_specs.json').read_text())
    if len(specs['candidates'])!=366:raise RuntimeError('Expected verified 366-candidate baseline')
    baseline=output_set()
    if len(baseline)!=888:raise RuntimeError('Incomplete baseline outputs')
    manifest=json.loads((P/'source_manifest.json').read_text());old_sources={x['path']:x['local_sha256'] for x in manifest['files']}
    ages=[str(i) for i in range(8)]+['5_2','6_2','7_2']
    models=[f'houttuynia_crop_stage{i}' for i in ages]+['pepper_log','pepper_leaves','pepper_leaves_fruiting','pepper_sapling']
    textures=[f'block/crop/houttuynia/stage{i}' for i in ages]+[f'block/{i}' for i in ('pepper_log','pepper_log_top','pepper_leaves','pepper_leaves_fruiting','pepper_sapling')]
    states=['houttuynia_crop','pepper_log','pepper_leaves','pepper_sapling']
    paths=[f'{NS}/models/block/{n}.json' for n in models]+[f'{NS}/textures/{n}.png' for n in textures]+[f'{NS}/blockstates/{n}.json' for n in states]
    sources={};references={}
    offline=os.environ.get('GRILLING_PLANTS_INPUTS')
    if offline:
        packed=json.loads(Path(offline).read_text());sources={k:base64.b64decode(v) for k,v in packed['files'].items()};references=packed['references']
    else:
        with zipfile.ZipFile(io.BytesIO(get(f'https://codeload.github.com/breezeth-CN/KaleidoscopeGrilling/zip/{SHA}'))) as z:
            top=z.namelist()[0].split('/')[0]+'/'
            for path in paths:
                logical=PREFIX+path;sources[logical]=z.read(top+logical)
                references[logical]={'repository':'breezeth-CN/KaleidoscopeGrilling','ref':SHA,'remote_path':logical,'license':'CC-BY-NC-SA-4.0'}
        for name,expected in TEMPLATES.items():
            remote=f'assets/minecraft/models/block/{name}.json';logical=PREFIX+f'minecraft/models/block/{name}.json'
            value=get('https://raw.githubusercontent.com/InventivetalentDev/minecraft-assets/1.20.1/'+remote)
            if blob(value)!=expected:raise RuntimeError('Minecraft reference hash mismatch: '+name)
            sources[logical]=value;references[logical]={'repository':'InventivetalentDev/minecraft-assets','ref':'1.20.1','remote_path':remote,'license':'Minecraft reference template; Mojang/Microsoft rights, not CC-BY-NC-SA','expected_git_blob':expected}
    expected_paths={PREFIX+x for x in paths}|{PREFIX+f'minecraft/models/block/{n}.json' for n in TEMPLATES}
    if set(sources)!=expected_paths:raise RuntimeError('Wrong source bundle')
    for logical,value in sources.items():
        meta=references[logical]
        if meta.get('expected_git_blob') and blob(value)!=meta['expected_git_blob']:raise RuntimeError('Pinned parent changed')
        if logical in old_sources:raise RuntimeError('Refusing to overwrite baseline source')
        dest=P/'source_snapshots'/logical;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(value)
        manifest['files'].append({'path':logical,'source_url':f"https://github.com/{meta['repository']}/blob/{meta['ref']}/{meta['remote_path']}",'upstream_git_blob_sha1':blob(value),'local_git_blob_sha1':blob(value),'local_sha256':sha(value),'representation':'binary-exact' if logical.endswith('.png') else 'raw-utf8-exact','upstream_byte_match':True,'license':meta['license']})
    write(P/'source_manifest.json',manifest)
    write(P/'reports/plants/source-bundle.json',{'files':{k:base64.b64encode(v).decode() for k,v in sources.items()},'references':references})
    for i in ages:
        specs['candidates'].append({'name':'houttuynia_stage_'+i,'source_model':NS+':block/houttuynia_crop_stage'+i,'atlas_name':'houttuynia_stage_'+i,'label_zh':'魚腥草・階段 '+i,'group':'houttuynia','offsets':[[0,0]],'reference_template':True})
    for name,title in [('pepper_log','花椒原木'),('pepper_leaves','花椒樹葉・未結果'),('pepper_leaves_fruiting','花椒樹葉・結果'),('pepper_sapling','花椒樹苗')]:
        specs['candidates'].append({'name':name,'source_model':NS+':block/'+name,'atlas_name':name,'label_zh':title,'group':'pepper','offsets':[[0,0]],'reference_template':True,'source_tint_pending':name.startswith('pepper_leaves')})
    specs['version']='A1.14.0';write(P/'config/asset_specs.json',specs)
    install_template_support()
    sys.path.insert(0,str(P/'tools'))
    import build_assets as build
    import audit_multiview as audit
    import numpy as np
    from PIL import Image,ImageDraw
    report=build.build()
    current=output_set()
    if any(current.get(k)!=v for k,v in baseline.items()):raise RuntimeError('Old geometry/editor/atlas changed')
    if any(sha((P/'source_snapshots'/k).read_bytes())!=v for k,v in old_sources.items()):raise RuntimeError('Old source changed')
    all_surface=[]
    byspec={x['name']:x for x in specs['candidates']}
    for r in report['candidates']:
        a=audit.source_faces(r,byspec[r['name']]);b=audit.bedrock_faces(r)
        same=collections.Counter(map(audit.signature,a))==collections.Counter(map(audit.signature,b))
        if not same:raise RuntimeError('Surface mismatch: '+r['name'])
        all_surface.append({'name':r['name'],'equal':same})
    rows=audit.run(start=366)
    if any(not r['directed_faces_and_uv_equal'] or any(v['max_channel_error_255']!=0 for v in r['views']) for r in rows):raise RuntimeError('Multiview mismatch')
    contacts=P/'reports/plants';contacts.mkdir(exist_ok=True)
    def sheet(names,views,file):
        records={r['name']:r for r in report['candidates']}
        faces={n:audit.bedrock_faces(records[n]) for n in names}
        frame=np.concatenate([f['points'] for n in names for f in faces[n]]).tolist()
        im=Image.new('RGB',(320*len(names),286*len(views)),(23,27,33));d=ImageDraw.Draw(im)
        for y,view in enumerate(views):
            for x,name in enumerate(names):
                im.paste(audit.render(faces[name],view,frame).convert('RGB'),(x*320,y*286+26));d.text((x*320+8,y*286+6),f'{name} / {view}',fill=(230,230,230))
        im.save(contacts/file)
    sheet(['houttuynia_stage_'+str(i) for i in range(8)],['front_oblique','front'],'houttuynia-ages.png')
    sheet(['houttuynia_stage_'+i for i in ('5','5_2','6','6_2','7','7_2')],['front_oblique','front'],'houttuynia-red-variants.png')
    sheet(['pepper_sapling','pepper_log','pepper_leaves','pepper_leaves_fruiting'],['front_oblique','back_oblique','top'],'pepper-parts.png')
    mutant=copy.deepcopy(next(r for r in report['candidates'] if r['name']=='pepper_sapling'))
    # Source-side omission of rescale must not compare equal to the export.
    raw,_=audit.read_source_model(byspec['pepper_sapling']['source_model'])
    orig_reader=audit.read_source_model
    damaged=copy.deepcopy(raw)
    for e in damaged['elements']:e['rotation']['rescale']=False
    audit.read_source_model=lambda *args,**kwargs:(damaged,[])
    unequal=collections.Counter(map(audit.signature,audit.source_faces(mutant,byspec['pepper_sapling'])))!=collections.Counter(map(audit.signature,audit.bedrock_faces(mutant)))
    audit.read_source_model=orig_reader
    if not unequal:raise RuntimeError('Rescale mutation was not detected')
    from reference_templates import prepare
    leaf,_=audit.read_source_model(NS+':block/pepper_leaves')
    try:prepare(leaf)
    except ValueError:tint_guard=True
    else:tint_guard=False
    if not tint_guard:raise RuntimeError('Unresolved tint must not silently pass')
    variants=[]
    for name in states:
        document=json.loads(sources[PREFIX+NS+'/blockstates/'+name+'.json'])
        variants.append({'block':name,'source':document,'gameplay_implemented':False})
    write(contacts/'blockstate-reference.json',variants)
    summary={'version':'A1.14.0','added_candidates':15,'candidate_count':report['candidate_count'],'unique_geometry_bases':report['unique_geometry_bases'],'atlas_count':report['atlas_count'],'new_sources':len(sources),'baseline_outputs_unchanged':len(baseline),'baseline_sources_unchanged':len(old_sources),'directed_surfaces_equal':len(all_surface),'new_eight_view_pairs':len(rows)*8,'new_eight_view_pairs_equal':sum(v['max_channel_error_255']==0 for r in rows for v in r['views']),'mutation_missing_rescale_detected':unequal,'unresolved_tint_guard':tint_guard,'minecraft_tested':False,'bridge_tested':False,'tree_worldgen_implemented':False,'tinted_leaves_color_validation':'untinted source reference only; biome tint and culling remain pending'}
    write(contacts/'verification.json',summary)
    manifest_path=P/'resource_pack/manifest.json';pack=json.loads(manifest_path.read_text());pack['header']['version']=[0,1,14];pack['header']['name']='KG Assets A1.14.0 — REVIEW ONLY'
    for m in pack['modules']:m['version']=[0,1,14]
    write(manifest_path,pack)
    config=json.loads((P/'config.json').read_text());config['name']='Grilling A1.14.0 Assets';write(P/'config.json',config)
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
