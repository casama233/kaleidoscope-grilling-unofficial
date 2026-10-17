from verify_a2843 import main as previous
import json
from pathlib import Path
def main():
 previous()
 p=Path(__file__).resolve().parents[2]/'projects/grilling/gameplay_core/resource_pack/models/entity/secret_held.geo.json'
 assert len(json.loads(p.read_text())['minecraft:geometry'])==7
 print('A2844 bounded shared secret geometries PASS; client rendering separate')
if __name__=='__main__':main()
