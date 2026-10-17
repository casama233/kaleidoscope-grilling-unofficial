"""Geometric edge cases: do not weld intentional backfaces or different poses."""
import unittest
from copy import deepcopy
from a283_render_repair import deduplicate

def cube(face='up',uv=0):return {'origin':[0,0,0],'size':[2,2,2],'uv':{face:{'uv':[uv,0],'uv_size':[2,2]}}}
def mesh(*cubes):return {'bones':[{'name':'root','pivot':[0,0,0],'cubes':list(cubes)}]}
class Faces(unittest.TestCase):
 def test_same_facing_overlay_is_removed(self):
  g=mesh(cube(),cube(uv=4));self.assertEqual(len(deduplicate(g)),1);self.assertEqual(len(g['bones'][0]['cubes']),1)
 def test_inner_and_outer_faces_survive(self):
  a=cube();a['size'][1]=0;b=deepcopy(a);b['uv']={'down':b['uv']['up']}
  g=mesh(a,b);self.assertEqual(deduplicate(g),[])
 def test_different_rotation_is_not_duplicate(self):
  a=cube();b=cube();b['rotation']=[0,0,30];b['pivot']=[0,0,0]
  self.assertEqual(deduplicate(mesh(a,b)),[])
 def test_material_layers_not_merged(self):
  a=cube();b=cube();b['uv']['up']['material_instance']='fluid'
  self.assertEqual(deduplicate(mesh(a,b)),[])
 def test_adjacent_rectangles_not_removed(self):
  a=cube();b=cube();b['origin'][0]=2
  self.assertEqual(deduplicate(mesh(a,b)),[])
if __name__=='__main__':unittest.main()
