from __future__ import annotations
from pathlib import Path
import argparse,json,re,subprocess,sys

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core'
BP=P/'behavior_pack';RP=P/'resource_pack'
COOKERY_BP='10f37ae2-9ccf-435f-b34b-0eec8191cd94'
COOKERY_RP='c89dc8df-c3fc-4bc8-8bd0-527abba76681'
VER=[1,0,6]

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
    for p in P.rglob('*.json'):load(p)
    report=load(P/'reports/build.json')
    assert report['cookable_fixed_skewers']==19
    assert report['formal_skewer_items']==41
    assert report['formal_support_items']==5
    assert report['grill_slots']==3 and report['finished_ticks']==800 and report['burnt_ticks']==400
    bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
    assert bm['header']['version']==[2,0,0] and rm['header']['version']==[2,0,0]
    assert {'uuid':COOKERY_BP,'version':VER} in bm['dependencies']
    assert {'uuid':COOKERY_RP,'version':VER} in rm['dependencies']
    block=load(BP/'blocks/grill.json')['minecraft:block']
    be=block['components']['minecraft:block_entity']
    assert be['container']['slot_count']==3 and be['dynamic_properties'] is True
    assert block['description']['identifier']=='kaleidoscope_grilling:grill'
    assert block['components']['minecraft:geometry']=='geometry.kg_core.grill'
    items=list((BP/'items').glob('*.json'))
    assert len(items)==46,len(items)
    raw=[p for p in items if p.stem.startswith('raw_')]
    cooked=[p for p in items if p.stem.startswith('grilled_')]
    assert len(raw)==19,len(raw)
    assert len(cooked)==19,len(cooked)
    foods=[]
    for p in items:
        doc=load(p)['minecraft:item'];ident=doc['description']['identifier'];comp=doc['components']
        assert ident.startswith('kaleidoscope_grilling:')
        assert not ident.startswith('kg_imm:')
        if p.stem in {x.stem for x in raw+cooked}|{'ordinary_skewer','mysterious_skewer','dark_grilling'}:
            foods.append(p.stem)
            assert comp['minecraft:max_stack_size']==1
            assert comp['minecraft:food']['nutrition']>=0
            assert comp['minecraft:food']['saturation_modifier']>=0
            assert comp['minecraft:use_animation']=={'value':'eat'}
            assert comp['minecraft:use_modifiers']['use_duration'] in (4.5,5.0)
            assert 'minecraft:is_food' in comp['minecraft:tags']['tags']
    assert len(foods)==41
    js=(BP/'scripts/data.js').read_text()
    raw_entries=re.findall(r'"kaleidoscope_grilling:raw_[^"]+":\s*"kaleidoscope_grilling:grilled_[^"]+"',js)
    assert len(raw_entries)==19,len(raw_entries)
    runtime=(BP/'scripts/main.js').read_text()
    for token in ['playerInteractWithBlock','playerPlaceBlock','playerBreakBlock','itemStartUse','itemStopUse','itemCompleteUse','entityHurt','minecraft:dynamic_properties','minecraft:inventory']:
        assert token in runtime,token
    assert 'FINISHED_TICKS=800' in (BP/'scripts/core_logic.js').read_text()
    assert 'BURNT_TICKS=400' in (BP/'scripts/core_logic.js').read_text()
    for p in BP.glob('scripts/*.js'):
        subprocess.run(['node','--check',str(p)],check=True)
    compiled=[]
    if a.compiled:
        build=P/'builds/dist'
        for name,source in [('behavior_pack',BP),('resource_pack',RP)]:
            manifest=load(source/'manifest.json')
            matches=[p.parent for p in build.rglob('manifest.json') if load(p).get('header',{}).get('uuid')==manifest['header']['uuid']]
            assert len(matches)==1,(name,matches)
            target=matches[0];count=0
            for p in source.rglob('*'):
                if not p.is_file() or p.name.startswith('.'):continue
                q=target/p.relative_to(source)
                assert q.is_file(),str(q)
                if p.suffix=='.json':assert load(p)==load(q),str(q)
                else:assert p.read_bytes()==q.read_bytes(),str(q)
                count+=1
            compiled.append({'pack':name,'compared_files':count,'matches_source':True})
    result={'version':'A2.0.0','formal_items':46,'formal_foods':41,'cookable_fixed_skewers':19,'real_grill_block_entity_slots':3,'cookery_dependency_verified':True,'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False,'block_entity_runtime_tested_in_engine':False}
    out=P/'reports'/('dash-verification.json' if a.compiled else 'structure-verification.json')
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(out.read_text())

if __name__=='__main__':main()
