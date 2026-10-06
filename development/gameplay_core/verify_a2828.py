"""Immersion audio and truthful shared-guide regressions; client gate is separate."""
from pathlib import Path
import hashlib,json,subprocess,sys
from verify_a2827 import main as baseline
ROOT=Path(__file__).resolve().parents[2]
RP=ROOT/'projects/grilling/gameplay_core/resource_pack'
def main():
    baseline()
    subprocess.run(['node','--test','development/gameplay_core/test_immersion_audio.mjs','development/gameplay_core/test_localized_heat_lore.mjs','development/gameplay_core/test_pending_audio.mjs','development/gameplay_core/test_full_skewer_flow.mjs'],cwd=ROOT,check=True)
    subprocess.run(['node','--experimental-vm-modules','development/gameplay_core/test_hot_food_manual_merge.mjs'],cwd=ROOT,check=True)
    proof=json.loads((ROOT/'development/gameplay_core/fixtures/released-audio-1.1.1.json').read_text())
    assert len(proof['assets'])==17 and len(proof['sound_events'])==13
    assert proof['audio_transformations'] is False and proof['client_acceptance'] is False
    for row in proof['assets']:
        assert hashlib.sha256((ROOT/row['target']).read_bytes()).hexdigest()==row['sha256'],row['target']
    defs=json.loads((RP/'sounds/sound_definitions.json').read_text())['sound_definitions']
    assert len(defs)==21
    for event,row in proof['sound_events'].items():
        expected=[]
        for sound in row['sounds']:
            sound={'name':sound} if isinstance(sound,str) else dict(sound)
            sound['name']='sounds/kg_imm/'+sound['name'].split(':',1)[-1]
            expected.append(sound)
        assert defs['kg_imm.'+event]['sounds']==expected,event
    catalog=json.loads((ROOT/'projects/grilling/guide/catalog.a3.json').read_text())
    if tuple(json.loads((ROOT/'baseline.json').read_text())['version'])>=(2,8,72):
        ref=json.loads((ROOT/'tools/fixtures/cookery-160-reference.json').read_text())
        assert all(catalog['host_reference'][key]==value for key,value in ref.items())
    else:
        assert catalog['host_reference']['version']=='1.0.8'
        assert catalog['host_reference']['guide_sha256']=='49ea47f9dc7511af210562118c7d2164ab5e185296a5a8c8d678e7d7ff8dc959'
    assert len(catalog['categories'])<=32
    if catalog.get('host_extension'):
        assert catalog['acquisition_gaps']==[] and catalog['host_extension']['capability']=='chopping_board_v2'
    else:
        assert {r['item'] for r in catalog['acquisition_gaps']}=={'kaleidoscope_grilling:beef_chunks','kaleidoscope_grilling:chicken_skin'}
    quick=next(e for e in catalog['entries'] if e['id']=='kg_a1:guide_quick_start')
    for locale in catalog['locales']:
        assert len(quick['body'][locale])==8
        assert '1.25' in '\n'.join(quick['body'][locale])
        assert 'Hold a stick or unfinished skewer' not in json.dumps(catalog,ensure_ascii=False)
        language=(RP/'texts'/f'{locale}.lang').read_text()
        assert language.count('tooltip.kaleidoscope_grilling.smoky_warmth=')==1
    subprocess.run([sys.executable,'tools/build_grilling_guide.py','--check'],cwd=ROOT,check=True)
    print('A2.8.28 original audio, scoped lifecycle and shared-guide regressions PASS; no client acceptance implied')
if __name__=='__main__':main()
