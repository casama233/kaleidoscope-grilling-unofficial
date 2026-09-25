"""Deterministic guide-only mcaddon. Never bundle the host or a private server pack."""
from __future__ import annotations
import argparse, hashlib, json, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT/'projects/grilling/integration/cookery106'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path);a=ap.parse_args()
    version=json.loads((PROJECT/'behavior_pack/manifest.json').read_text())['header']['version']
    out=a.output or ROOT/'artifacts/candidates'/('Kaleidoscope_Grilling_Guide_A'+'_'.join(map(str,version))+'.mcaddon')
    out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(out,'w') as z:
        for label in ['behavior_pack','resource_pack']:
            for p in sorted((PROJECT/label).rglob('*')):
                if not p.is_file() or p.name.startswith('.'):continue
                info=zipfile.ZipInfo(label+'/'+p.relative_to(PROJECT/label).as_posix(),(1980,1,1,0,0,0));info.create_system=3;info.external_attr=0o100644<<16
                z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(out) as z:
        if z.testzip():raise ValueError('Archive integrity failure')
        for label in ['behavior_pack','resource_pack']:
            if json.loads(z.read(label+'/manifest.json'))['header']['version']!=version:raise ValueError('Packaged version mismatch')
    digest=hashlib.sha256(out.read_bytes()).hexdigest();out.with_name(out.name+'.sha256').write_text(digest+'  '+out.name+'\n')
    print(json.dumps({'path':str(out),'sha256':digest,'version':version,'contains_host':False},indent=2))
if __name__=='__main__':main()
