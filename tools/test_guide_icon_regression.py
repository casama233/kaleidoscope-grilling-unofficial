"""Reject atlas-as-icon regressions from the user's 2026-10-01 screenshots."""
import copy,unittest
from build_grilling_guide import SOURCE,load,validate_source
class GuideIconRegression(unittest.TestCase):
 def test_correct_icons(self):
  d=load(SOURCE);validate_source(d);self.assertEqual(d['icon'],'textures/ui/kg_grilling/grill_legged_lit')
  roots={c['id']:c for c in d['categories']};self.assertEqual(roots['workstations']['icon'],d['icon']);self.assertEqual(roots['tools_gear']['icon'],'textures/ui/kg_grilling/catalog/special_seasoning')
 def test_raw_atlas_is_rejected_in_every_menu_layer(self):
  for icon in ['textures/ui/kg_grilling/guide_grill','textures/ui/kg_grilling/guide_seasoning']:
   for layer in ['root','category','entry']:
    d=copy.deepcopy(load(SOURCE))
    if layer=='root':d['icon']=icon
    elif layer=='category':d['categories'][0]['icon']=icon
    else:d['entries'][0]['icon']=icon
    with self.assertRaisesRegex(ValueError,'Raw material atlas'):validate_source(d)
if __name__=='__main__':unittest.main()
