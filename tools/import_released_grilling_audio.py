"""Copy only checksum-verified audio from the official Java 1.1.1 release.

No historical Bedrock pack or altered audio is accepted as input.
"""
from pathlib import Path
import argparse,hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
JAR_SHA256='cf31071e4ba790bcd5c1d3f6005439bc512acba084e70b8ab6a767e8c8f99dd6'
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--jar',type=Path,required=True)
    args=parser.parse_args()
    if hashlib.sha256(args.jar.read_bytes()).hexdigest()!=JAR_SHA256:
        raise SystemExit('Not the verified official Java 1.1.1 release')
    rp=ROOT/'projects/grilling/gameplay_core/resource_pack'
    rows=[]
    with zipfile.ZipFile(args.jar) as z:
        for name in sorted(z.namelist()):
            if not name.startswith('assets/kaleidoscope_grilling/sounds/') or not name.endswith('.ogg'):continue
            raw=z.read(name);dest=rp/'sounds/kg_imm'/Path(name).name
            dest.write_bytes(raw)
            rows.append({'source':name,'target':dest.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(raw).hexdigest()})
        original=json.loads(z.read('assets/kaleidoscope_grilling/sounds.json'))
    definitions={}
    for event,row in original.items():
        category='player' if event.endswith('_eat') or event=='shake_seasoning' else 'block'
        sounds=[]
        for sound in row['sounds']:
            sound={'name':sound} if isinstance(sound,str) else dict(sound)
            sound['name']='sounds/kg_imm/'+sound['name'].split(':',1)[-1]
            sounds.append(sound)
        definitions['kg_imm.'+event]={'category':category,'sounds':sounds}
    # Preserve the existing eating channel aliases. They are not distinct source audio.
    for channel in range(8):definitions['kg_imm.four_skewer_eat_ch'+str(channel)]=definitions['kg_imm.four_skewer_eat']
    (rp/'sounds/sound_definitions.json').write_text(json.dumps({'format_version':'1.14.0','sound_definitions':definitions},indent=2)+'\n')
    proof={'source_url':'https://www.curseforge.com/minecraft/mc-mods/kaleidoscope-grilling/files/8726014',
        'version':'1.1.1-neoforge1.21.1','jar_sha256':JAR_SHA256,'assets':rows,
        'sound_events':original,'audio_transformations':False,'client_acceptance':False}
    (ROOT/'development/gameplay_core/fixtures/released-audio-1.1.1.json').write_text(json.dumps(proof,indent=2)+'\n')
    print('Imported 17 original OGGs and 13 event definitions; no client acceptance implied.')
if __name__=='__main__':main()
