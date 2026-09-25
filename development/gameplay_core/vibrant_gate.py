"""Manifest/export contract only, not proof of in-game Vibrant Visuals support."""
import json
import zipfile
from pathlib import Path


def check_pair(bp, rp):
    def ver(v):
        if not isinstance(v, list) or len(v) != 3 or any(type(x) is not int or x < 0 for x in v):
            raise ValueError(f'invalid numeric manifest version: {v!r}')
        return tuple(v)
    a, b = ver(bp['header']['version']), ver(rp['header']['version'])
    if a != b:
        raise ValueError('BP/RP versions differ')
    for doc in (bp, rp):
        for module in doc['modules']:
            if ver(module['version']) != a:
                raise ValueError('module/header version drift')
    caps = rp.get('capabilities', [])
    if not isinstance(caps, list) or 'pbr' not in caps:
        raise ValueError('Grilling RP lost the required pbr capability')
    if ver(rp['header']['min_engine_version']) < (1, 21, 120):
        raise ValueError('pbr requires min_engine_version >= 1.21.120')
    deps = [d for d in bp.get('dependencies', []) if d.get('uuid') == rp['header']['uuid']]
    if len(deps) != 1 or ver(deps[0]['version']) != b:
        raise ValueError('BP resource-pack dependency is stale')
    return {'pbr': True, 'version': list(a), 'client_tested': False}


def check_paths(bp, rp):
    docs = [json.loads((Path(p) / 'manifest.json').read_text(encoding='utf-8-sig')) for p in (bp, rp)]
    check_pair(*docs)
    return docs


def check_archive(path, source):
    with zipfile.ZipFile(path) as z:
        if len(z.namelist()) != len(set(z.namelist())):
            raise ValueError('duplicate archive member')
        built = [json.loads(z.read(f'{p}/manifest.json').decode('utf-8-sig')) for p in ('behavior_pack','resource_pack')]
    check_pair(*built)
    if built != source:
        raise ValueError('packaged manifests differ from canonical source')
