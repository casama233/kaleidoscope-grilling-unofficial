"""Source-derived active first-person frames; native clips remain separate."""
from pathlib import Path
import subprocess,sys,json
from verify_a2857 import main as previous

def main():
    previous()
    root=Path(__file__).resolve().parents[2]
    version=json.loads((root/'baseline.json').read_text())['version']
    config=json.loads((root/'config.json').read_text())
    rewrite=[p[1]['packName'] for p in config['compiler']['plugins'] if isinstance(p,list) and p[0]=='simpleRewrite']
    assert rewrite==['Kaleidoscope_Grilling_'+'_'.join(map(str,version))+'_Canonical'], 'bridge build name drifted from canonical version'

    subprocess.run([sys.executable,'development/gameplay_core/test_java_active_eating_frames.py'],cwd=Path(__file__).resolve().parents[2],check=True)
    subprocess.run([sys.executable,'development/gameplay_core/test_native_eating_clock.py'],cwd=Path(__file__).resolve().parents[2],check=True)
    subprocess.run([sys.executable,'development/gameplay_core/test_native_offhand_idle.py'],cwd=Path(__file__).resolve().parents[2],check=True)
    print('A2.8.58 active Java matrix source checks PASS; complete client parity unclaimed')

if __name__=='__main__':main()
