#!/usr/bin/env python3
"""Static/byte checks and pure algorithms only; no mocked players or Minecraft API."""
from __future__ import annotations
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,os,re,shutil,subprocess,sys

ROOT=Path(__file__).resolve().parents[1]
HERE=Path(__file__).resolve().parent

def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def require(condition,message):
    if not condition: raise RuntimeError(message)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    node=shutil.which('node')
    require(node is not None,'Node.js is required; no checks have been skipped.')
    baseline=load(HERE/'baseline-pack-sha256.json');allow=load(HERE/'change-allowlist.json')
    files={p.relative_to(ROOT).as_posix():p for name in ('behavior_pack','resource_pack') for p in (ROOT/name).rglob('*') if p.is_file()}
    changed=sorted(k for k in baseline if k in files and sha(files[k])!=baseline[k])
    added=sorted(set(files)-set(baseline));removed=sorted(set(baseline)-set(files))
    require(changed==allow['changed'],'Unexpected changed files: '+repr(changed))
    require(added==allow['added'] and removed==allow['removed'],'Unexpected added/removed runtime files.')
    require(not removed,'A candidate must not remove baseline pack files.')
    require(all(k=='resource_pack/manifest.json' or not k.startswith('resource_pack/') for k in changed),'Resource art or guide assets changed.')
    require(all(k.endswith('.js') or k in ('behavior_pack/manifest.json','resource_pack/manifest.json') for k in changed),'Items, blocks or recipes changed.')
    for k in changed:
        require('/guide/' not in k,'Guide content changed.')
    jsons=[p for p in files.values() if p.suffix=='.json']
    for p in jsons:load(p)
    scripts=[p for p in files.values() if p.suffix=='.js']
    def check_js(p):
        result=subprocess.run([node,'--check',str(p)],capture_output=True,text=True)
        require(result.returncode==0,f'{p}: {result.stderr}')
    with ThreadPoolExecutor(max_workers=min(8,os.cpu_count() or 1)) as pool:list(pool.map(check_js,scripts))
    externals=set();local_imports=0
    pattern=re.compile(r'''(?:\bfrom\s*|\bimport\s*)['"]([^'"]+)['"]''')
    for p in scripts:
        for ref in pattern.findall(p.read_text(encoding='utf-8')):
            if ref.startswith('.'):
                target=(p.parent/ref).resolve();require(target.is_file() and target.is_relative_to(ROOT),'Missing/escaping import: '+ref)
                local_imports+=1
            else:externals.add(ref)
    require(externals=={'@minecraft/server','@minecraft/server-ui'},'Unexpected external dependencies.')
    bp=load(ROOT/'behavior_pack/manifest.json');rp=load(ROOT/'resource_pack/manifest.json')
    require(bp['header']['uuid']=='c68005c5-23ff-54e8-a3ff-da6349ad43c2','BP UUID changed')
    require(rp['header']['uuid']=='bbbd2d60-52e5-53a6-8b9a-c09b0f516389','RP UUID changed')
    require(bp['header']['version']==rp['header']['version']==[2,8,8],'Candidate versions differ')
    expected_modules={'dcf70052-c592-56e3-84d2-2a9b86abe7ab','d0bb6818-8187-5d20-8e1f-a2ab7b517795','e7d592db-f4a0-53ce-8b0a-cab7a0cee8d7'}
    require({m['uuid'] for p in [bp,rp] for m in p['modules']}==expected_modules,'Module UUIDs changed')
    require(all(m['version']==[2,8,8] for p in [bp,rp] for m in p['modules']),'Module versions differ')
    for p,host in [(bp,'10f37ae2-9ccf-435f-b34b-0eec8191cd94'),(rp,'c89dc8df-c3fc-4bc8-8bd0-527abba76681')]:
        require(any(d.get('uuid')==host and d.get('version')==[1,0,6] for d in p['dependencies']),'Public Cookery 1.0.6 dependency changed')
        require(p['header']['min_engine_version']==[1,26,50],'Minimum engine version changed')
    require(any(d.get('uuid')==rp['header']['uuid'] and d.get('version')==[2,8,8] for d in bp['dependencies']),'BP/RP pair mismatch')
    require(rp.get('capabilities')==['pbr'],'Vibrant capability changed')
    api={d['module_name']:d['version'] for d in bp['dependencies'] if 'module_name' in d}
    require(api=={'@minecraft/server':'2.9.0','@minecraft/server-ui':'2.2.0'},'Script API versions changed')
    pure=subprocess.run([node,'--experimental-default-type=module','--test',str(HERE/'pure_checks.mjs')],capture_output=True,text=True,env={**os.environ,'GRILLING_PROJECT':str(ROOT)})
    (HERE/'pure-checks.tap').write_text(pure.stdout+pure.stderr,encoding='utf-8')
    require(pure.returncode==0,'Pure algorithm checks failed; see pure-checks.tap')
    report={'version':'A2.8.8 Local Review','baseline_version':'A2.8.7','baseline_git_commit':'707d28edab4ea9af76878e0e29d8244848971db3',
        'js_checked':len(scripts),'json_checked':len(jsons),'relative_imports_checked':local_imports,
        'baseline_pack_files':len(baseline),'candidate_pack_files':len(files),
        'unchanged_baseline_pack_files':len(baseline)-len(changed)-len(removed),
        'changed_pack_files':changed,'added_pack_files':added,'removed_pack_files':removed,
        'pure_algorithm_tests_passed':int(re.search(r'^# pass (\d+)',pure.stdout,re.M)[1]),
        'tests_import_minecraft_api':False,'simulated_player_tests_run':False,
        'minecraft_tested':False,'bds_tested':False,'client_visuals_tested':False,'multiplayer_tested':False,
        'performance_benchmarked':False,'official_dash_run_for_candidate':False,'full_repository_ci_run_for_candidate':False,
        'pushed_to_github':False,'release_published':False,'server_deployed':False,
        'all_checks_above_passed':True}
    (HERE/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':
    try:main()
    except Exception as error:
        print('Candidate validation FAILED: '+str(error),file=sys.stderr)
        raise SystemExit(1)
