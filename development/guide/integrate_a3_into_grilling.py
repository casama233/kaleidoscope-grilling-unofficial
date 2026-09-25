"""One-time packaging correction, not the normal build entry.

Keep gameplay UUIDs and the Cookery guide module ID. Move the existing A3
publisher/catalog assets into the product; do not introduce a second pack.
Historical standalone material is moved to history, not destroyed.
"""
from __future__ import annotations
import hashlib, json, shutil, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
G=ROOT/'projects/grilling';PRODUCT=G/'gameplay_core';OLD=G/'integration/cookery106'
BP,RP=PRODUCT/'behavior_pack',PRODUCT/'resource_pack'
ARCHIVE=ROOT/'history/standalone-guide-a3'
BP_UUID='c68005c5-23ff-54e8-a3ff-da6349ad43c2'
RP_UUID='bbbd2d60-52e5-53a6-8b9a-c09b0f516389'

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,s):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
def dump(p,o):write(p,json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def replace(p,a,b):
    text=p.read_text(encoding='utf-8-sig')
    if text.count(a)!=1:raise ValueError(f'Expected one anchor in {p}: {a[:90]}')
    write(p,text.replace(a,b,1))
def checked_copy(src,dst):
    if dst.exists() and dst.read_bytes()!=src.read_bytes():raise ValueError('Asset collision: '+str(dst))
    dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    target=load(ROOT/'.repo-target.json')
    assert target['repository']=='casama233/kaleidoscope-grilling-unofficial' and target['repository_id']==1377218440
    assert load(BP/'manifest.json')['header']['uuid']==BP_UUID
    assert load(RP/'manifest.json')['header']['uuid']==RP_UUID
    assert load(BP/'manifest.json')['header']['version']==[2,7,64]
    assert not ARCHIVE.exists(), 'Migration already archived; do not replay'
    catalog=load(G/'guide/catalog.a3.json')
    assert catalog['module_id']=='kg_a1:grilling' and len(catalog['entries'])==76
    # Every pre-existing gameplay/resource file, except language/manifests/startup,
    # must remain byte-identical. New files are checked separately below.
    unchanged={p:sha(p) for pack in (BP,RP) for p in pack.rglob('*') if p.is_file()
        and p not in {BP/'manifest.json',RP/'manifest.json',BP/'scripts/main.js'}
        and p.suffix!='.lang'}
    langs={p:p.read_bytes() for p in (RP/'texts').glob('*.lang')}
    original_main=(BP/'scripts/main.js').read_bytes()
    assert b"./guide/main.js" not in original_main
    for p in (OLD/'behavior_pack/scripts').glob('*.js'):
        checked_copy(p,BP/'scripts/guide'/p.name)
    # This is a child module of the ONLY product script entry, not another module.
    (BP/'scripts/main.js').write_bytes(b"import './guide/main.js';\n"+original_main)
    guide_main="""import { system } from '@minecraft/server';
import { installPublisher } from './publisher.js';
import { GUIDE_PAYLOAD } from './payload.js';
// Loaded once by Grilling scripts/main.js. The chapter UI belongs to Cookery.
try { installPublisher(system, GUIDE_PAYLOAD); }
catch (error) { console.warn(`[Grilling guide] Initialization failed: ${String(error)}`); }
"""
    write(BP/'scripts/guide/main.js',guide_main)
    replace(BP/'scripts/guide/publisher.js',' * Guide-only: no items, recipes, world writes, itemUse hooks, or extra guidebook.',
            ' * Built into Grilling: no separate pack, world writes, itemUse hooks, or extra guidebook.')
    for p in (OLD/'resource_pack/textures').rglob('*'):
        if p.is_file():checked_copy(p,RP/'textures'/p.relative_to(OLD/'resource_pack/textures'))
    for p in (OLD/'behavior_pack/THIRD_PARTY_NOTICES.txt',OLD/'resource_pack/ATTRIBUTION.md'):
        if p.exists():checked_copy(p,RP/'documentation/guide'/p.name)

    builder=ROOT/'tools/build_grilling_guide.py'
    replace(builder,"PROJECT=ROOT/'projects/grilling/integration/cookery106'","PROJECT=ROOT/'projects/grilling/gameplay_core'")
    replace(builder,"BP/'scripts/payload.js'","BP/'scripts/guide/payload.js'")
    replace(builder,"    for l in LOCALES:write_or_check(RP/'texts'/f'{l}.lang',lang_text(s,l),a.check)",
            "    for l in LOCALES:write_or_check(RP/'texts'/f'{l}.lang',merged_lang(RP/'texts'/f'{l}.lang,lang_text(s,l)),a.check)")
    merge_func='''LANG_BEGIN='## BEGIN GRILLING GUIDE A3 (generated)'
LANG_END='## END GRILLING GUIDE A3 (generated)'
def merged_lang(path,guide_text):
    text=path.read_text(encoding='utf-8-sig') if path.exists() else ''
    if LANG_BEGIN in text or LANG_END in text:
        if text.count(LANG_BEGIN)!=1 or text.count(LANG_END)!=1:raise ValueError('Guide language markers are malformed')
        prefix,rest=text.split(LANG_BEGIN,1);_old,suffix=rest.split(LANG_END,1)
        if suffix.strip():raise ValueError('Do not append gameplay text inside/after the generated guide section')
        text=prefix
    if any(line.startswith('guide.kg.') for line in text.splitlines()):raise ValueError('Duplicate unmanaged guide language keys')
    return text.rstrip('\\r\\n')+'\\n\\n'+LANG_BEGIN+'\\n'+guide_text+LANG_END+'\\n'

'''
    replace(builder,'def write_or_check(p,b,check):',merge_func+'def write_or_check(p,b,check):')
    check=ROOT/'tools/check_grilling_guide.py'
    replace(check,"BP_UUID='f8c367c2-84d6-5bf6-b5a8-1bbe6cdb93ab'",f"BP_UUID='{BP_UUID}'")
    replace(check,"RP_UUID='32baef08-6b04-5115-9d5b-2d4ba2d3a7b4'",f"RP_UUID='{RP_UUID}'")
    text=check.read_text(encoding='utf-8')
    start=text.index("    require(not (BP/'items').exists()")
    end=text.index("    pub=(BP/'scripts/publisher.js')",start)
    replacement='''    # The guide is part of the EXISTING product, not a guide pack.
    require(not (ROOT/'projects/grilling/integration/cookery106/behavior_pack/manifest.json').exists(),'Standalone guide BP resurrected')
    require(not (ROOT/'projects/grilling/integration/cookery106/resource_pack/manifest.json').exists(),'Standalone guide RP resurrected')
    require(not (ROOT/'.github/workflows/guide-canonical.yml').exists(),'Standalone guide publication workflow resurrected')
    require(not (BP/'items/guidebook.json').exists(),'Do not create a second physical guidebook')
    require(not (RP/'entity/player.entity.json').exists(),'Do not replace the host player definition')
    require(set(p.name for p in (BP/'scripts/guide').glob('*.js'))=={'main.js','payload.js','publisher.js'},'Guide module contents drift')
    startup=(BP/'scripts/main.js').read_text(encoding='utf-8')
    require(startup.count("import './guide/main.js';")==1,'Guide must load exactly once from the product entry')
    version=load(BP/'manifest.json')['header']['version']
    for pack,uid in [(BP,BP_UUID),(RP,RP_UUID)]:
        m=load(pack/'manifest.json');require(m['header']['uuid']==uid and m['header']['version']==version,'Product UUID/version drift')
        require(all(x['version']==version for x in m['modules']),'Module version drift')
    bm=load(BP/'manifest.json')
    require([m.get('entry') for m in bm['modules'] if m.get('type')=='script']==['scripts/main.js'],'Product has a second script entry')
    require(any(d.get('uuid')==RP_UUID and d['version']==version for d in bm['dependencies']),'BP/RP dependency drift')
    require(not any(d.get('uuid') in {'f8c367c2-84d6-5bf6-b5a8-1bbe6cdb93ab','32baef08-6b04-5115-9d5b-2d4ba2d3a7b4'} for d in bm['dependencies']),'Legacy guide pack dependency')
'''
    write(check,text[:start]+replacement+text[end:])
    replace(check,"pub=(BP/'scripts/publisher.js')","pub=(BP/'scripts/guide/publisher.js')")
    replace(check,"for p in (BP/'scripts').glob('*.js')","for p in (BP/'scripts/guide').glob('*.js')")
    replace(check,"str(BP/'scripts')","str(BP/'scripts/guide')")
    replace(check,"{'guide':s['version'],'entries'","{'built_into_grilling':True,'product_version':version,'guide_data_version':s['version'],'entries'")

    for pack,uid,label in [(BP,BP_UUID,'BP'),(RP,RP_UUID,'RP')]:
        p=pack/'manifest.json';m=load(p);assert m['header']['uuid']==uid
        m['header']['version']=[2,7,65]
        m['header']['name']='Kaleidoscope Grilling A2.7.65 Built-in Guide '+label
        m['header']['description']='煙火玩法、渲染與指南一體；指南自動加入 Cookery 既有附屬章節。需要 Cookery 1.0.6。'
        for module in m['modules']:module['version']=[2,7,65]
        for dep in m.get('dependencies',[]):
            if dep.get('uuid')==RP_UUID:dep['version']=[2,7,65]
        dump(p,m)
    cfg=load(PRODUCT/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.65 Built-in Guide'
    cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_65_Built_In_Guide';dump(PRODUCT/'config.json',cfg)

    # Retire standalone publishing, preserving all previous bytes in history.
    ARCHIVE.mkdir(parents=True)
    shutil.move(str(OLD),str(ARCHIVE/'cookery106'))
    shutil.move(str(ROOT/'.github/workflows/guide-canonical.yml'),str(ARCHIVE/'guide-canonical.yml.txt'))
    checked_copy(ROOT/'tools/build_grilling_guide_release.py',ARCHIVE/'build_grilling_guide_release.py.txt')
    write(ROOT/'tools/build_grilling_guide_release.py','''"""Deprecated guide-only command: build the complete Grilling product instead."""
import sys
from build_grilling_release import main
if __name__=='__main__':
    print('Guide-only packaging is retired. Building Grilling with its built-in chapter.',file=sys.stderr)
    main()
''')
    write(ARCHIVE/'README.md','# 歷史封存：錯誤的獨立指南交付\n\n不安裝、不發布、不作預設建置來源。A2.7.65 已將指南併入煙火同一組 BP/RP。這裡只保留舊交付取證。\n')
    write(OLD/'README.zh-TW.md','# 此獨立交付入口已停用\n\n指南已併入 `projects/grilling/gameplay_core` 的同一組 BP/RP。只安裝 Cookery 本體與煙火；在 Cookery 指南內開啟煙火附屬章節。不安裝第三個指南 addon。\n')

    release=ROOT/'tools/build_grilling_release.py'
    replace(release,'import zipfile\n','import zipfile\nimport subprocess\nimport sys\n')
    replace(release,'    bm = load_json(BP / "manifest.json")',
            '    subprocess.run([sys.executable, str(ROOT / "tools/check_grilling_guide.py")], check=True)\n    bm = load_json(BP / "manifest.json")')
    replace(release,'    digest = hashlib.sha256(output.read_bytes()).hexdigest()',
'''    with zipfile.ZipFile(output) as zf:
        names=set(zf.namelist())
        if {n for n in names if n.endswith('/manifest.json')} != {'behavior_pack/manifest.json','resource_pack/manifest.json'}:
            raise RuntimeError('Product must contain exactly its original BP/RP, not bundled guide packs')
        for n in ('main.js','publisher.js','payload.js'):
            key='behavior_pack/scripts/guide/'+n
            if key not in names or zf.read(key)!=(BP/'scripts/guide'/n).read_bytes():
                raise RuntimeError('Built-in guide missing or stale in package: '+key)
        if b"import './guide/main.js';" not in zf.read('behavior_pack/scripts/main.js'):
            raise RuntimeError('Packaged guide is not connected to the main entry')
        for p in (RP/'textures/ui/kg_grilling').rglob('*.png'):
            key='resource_pack/'+p.relative_to(RP).as_posix()
            if key not in names or zf.read(key)!=p.read_bytes():raise RuntimeError('Packaged guide icon mismatch')
    digest = hashlib.sha256(output.read_bytes()).hexdigest()''')
    replace(release,'        "contains_canonical_bp_rp": True,','        "contains_canonical_bp_rp": True,\n        "built_in_guide": True,\n        "standalone_guide_packs": 0,')

    wf=ROOT/'.github/workflows/gameplay-core-canonical.yml'
    text=wf.read_text(encoding='utf-8')
    text=text.replace("      - 'projects/grilling/gameplay_core/**'","      - 'projects/grilling/gameplay_core/**'\n      - 'projects/grilling/guide/**'\n      - 'tools/*grilling_guide*.py'\n      - 'docs/STATUS-A2.7.65.md'")
    text=text.replace('    timeout-minutes: 30','    timeout-minutes: 30\n    env:\n      PYTHONUTF8: \'1\'')
    text=text.replace('      - name: Audit canonical render chain', '''      - name: Check built-in guide and source facts
        shell: pwsh
        run: |
          python tools/check_grilling_guide.py | Tee-Object -FilePath "$env:RUNNER_TEMP/grilling-guide-check.json"
          if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

      - name: Audit canonical render chain''')
    text=text.replace('      - name: Build deterministic candidate addon', '''      - name: Compare compiled built-in guide with source
        shell: pwsh
        run: |
          python tools/check_grilling_guide.py --compiled
          if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

      - name: Build deterministic candidate addon''')
    text=text.replace('            ${{ runner.temp }}/grilling-render-audit.json','            ${{ runner.temp }}/grilling-render-audit.json\n            ${{ runner.temp }}/grilling-guide-check.json')
    write(wf,text)
    subprocess.run([sys.executable,str(ROOT/'tools/build_grilling_guide.py')],check=True)
    for p,expected in unchanged.items():assert sha(p)==expected, 'Unrelated gameplay/resource changed: '+str(p)
    for p,original in langs.items():
        # Compare text because the canonical generator normalizes line endings.
        actual=p.read_text(encoding='utf-8').split('## BEGIN GRILLING GUIDE A3 (generated)')[0]
        assert actual.rstrip()==original.decode('utf-8-sig').replace('\r\n','\n').rstrip(), 'Gameplay localization lost: '+str(p)
    assert (BP/'scripts/main.js').read_bytes()==b"import './guide/main.js';\n"+original_main
    proof={'product_version':[2,7,65],'guide_module_id':'kg_a1:grilling','guide_entries':len(catalog['entries']),
           'same_bp_uuid':BP_UUID,'same_rp_uuid':RP_UUID,'script_entry':'scripts/main.js',
           'guide_entry_imports':1,'unchanged_existing_files':len(unchanged),'gameplay_languages_preserved':len(langs),
           'guide_pngs':len(list((RP/'textures/ui/kg_grilling').rglob('*.png'))),'separate_guide_packs_required':False,
           'host_scripts_copied':False,'host_patch_produced':False,'host_106_locale_fallback':'zh_TW mechanics on unpatched registry; per-locale payload retained'}
    dump(G/'guide/builtin-integration.verified.json',proof)
    print(json.dumps(proof,ensure_ascii=False,indent=2))
    subprocess.run([sys.executable,str(ROOT/'tools/check_grilling_guide.py')],check=True)
    subprocess.run([sys.executable,str(ROOT/'tools/check_grilling_release.py')],check=True)
    subprocess.run([sys.executable,str(ROOT/'tools/audit_grilling_render.py'),'--fail-on-error'],check=True)

if __name__=='__main__':main()
