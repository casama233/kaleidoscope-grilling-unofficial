"""Keep regenerated helper actors on the current engine damage-sensor schema."""
import json
from verify_a2857 import main as previous
from verify_a2856 import BP
def main():
 previous()
 for name in ['a2770_placed_oil','a2770_placed_seasoning']:
  actor=json.loads((BP/f'entities/{name}.json').read_text())['minecraft:entity']
  assert actor['components']['minecraft:damage_sensor']['triggers']==[{'cause':'all','deals_damage':'no'}]
 print('Generated placed helpers preserve the native no-damage schema; client pending')
if __name__=='__main__':main()
