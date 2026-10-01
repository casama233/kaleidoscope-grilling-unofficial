"""Prepare a local-only input spec for the native Blockbench audit plugin."""
import argparse
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RP=ROOT/'projects/grilling/gameplay_core/resource_pack'
def prepare(output,all_held=False):
    output=output.resolve()
    if output==RP or RP in output.parents:raise ValueError('Reports must be outside canonical resource pack')
    output.mkdir(parents=True,exist_ok=True)
    entries=[];index={}
    for path in sorted((RP/'models').rglob('*.json')):
        raw=path.read_bytes();data=json.loads(raw)
        for i,g in enumerate(data.get('minecraft:geometry',[])):
            ident=g['description']['identifier']
            if ident in index:raise ValueError('Duplicate geometry '+ident)
            index[ident]=g
            entries.append({'path':str(path),'relative':path.relative_to(ROOT).as_posix(),'index':i,'identifier':ident,'sha256':hashlib.sha256(raw).hexdigest()})
    animations={k:v for path in (RP/'animations').glob('*.json') for k,v in json.loads(path.read_text()).get('animations',{}).items()}
    paths=sorted((RP/'attachables').glob('*.json')) if all_held else [RP/'attachables'/(name+'.attachable.json')for name in ['raw_beef_skewer','empty_seasoning_bottle','special_seasoning','advanced_rack']]
    held=[]
    for path in paths:
        a=json.loads(path.read_text())['minecraft:attachable']['description']
        ref=a['geometry'].get('default')or next(iter(a['geometry'].values()))
        geometry=json.loads(json.dumps(index[ref]));extra=a['geometry'].get('contents')
        if extra:
            for b in index[extra]['bones']:
                next(row for row in geometry['bones']if row['name']==b['name']).setdefault('cubes',[]).extend(b.get('cubes',[]))
        texture=a['textures'].get('default')or next(iter(a['textures'].values()))
        held.append({'name':path.name.removesuffix('.attachable.json'),'geometry':geometry,'texture':str(RP/(texture+'.png')),'animations':{k:{'id':v,'data':animations[v]}for k,v in a['animations'].items()},'merged_contents_for_preview_only':bool(extra)})
    spec={'input_root':str(ROOT),'output_root':str(output/'native-blockbench'),'entries':entries,'held_previews':held}
    target=output/'blockbench-input.json';target.write_text(json.dumps(spec,indent=2)+'\n');return target
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--all-held',action='store_true');args=p.parse_args();print(prepare(args.output,args.all_held))
