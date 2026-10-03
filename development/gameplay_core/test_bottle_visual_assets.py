"""Source bounds, exact palette sampling and held dispatch; no client claim."""
import json
import re
import unittest
import subprocess
from pathlib import Path
from PIL import Image
import a2861_bottle_held_visual_assets as held

ROOT=Path(__file__).resolve().parents[2]
RP=held.RP
BP=held.BP

def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

class BottleVisualAssets(unittest.TestCase):
    def test_placed_bounds_and_opaque_palette_match_source(self):
        source=load(ROOT/'development/gameplay_core/fixtures/a2770/grilling/kaleidoscope_grilling/models/item/seasoning_states/pending_8.json')
        geos={g['description']['identifier']:g for g in load(RP/'models/entity/a2770_placed/seasoning.geo.json')['minecraft:geometry']}
        for tint in range(16):
            element=next(e for e in source['elements'] if any(f.get('tintindex')==tint for f in e['faces'].values()))
            g=geos['geometry.kg_a2770.pending_'+str(tint)]
            cube=g['bones'][0]['cubes'][0]
            self.assertEqual(cube['origin'],[element['from'][0]-8,element['from'][1],element['from'][2]-8])
            self.assertEqual(cube['size'],[element['to'][i]-element['from'][i] for i in range(3)])
            self.assertEqual(set(cube['uv']),set(element['faces']))
        data=(BP/'scripts/a2770_placed_visual_data.js').read_text()
        palette=json.loads(re.search(r'INGREDIENT_COLORS=Object.freeze\((\{.*?\})\)',data).group(1))
        pinned=load(ROOT/'development/gameplay_core/fixtures/java-seasoning-colors-1.1.1.json')
        self.assertEqual(len(pinned['ingredients']),8)
        for identifier,row in pinned['ingredients'].items():
            self.assertEqual(palette[identifier],row['rgb'],identifier)
        colors=json.loads(re.search(r'PLACED_TINT_INDEX=Object.freeze\((\{.*?\})\)',data).group(1))
        for rgb,index in colors.items():
            rgb=int(rgb)
            with Image.open(RP/f'textures/a2770_placed/pending_color_{index}.png') as im:
                self.assertEqual(im.size,(16,16))
                self.assertEqual(im.convert('RGBA').getcolors(),[(256,((rgb>>16)&255,(rgb>>8)&255,rgb&255,255))])
        rc=load(RP/'render_controllers/a2770_placed.render_controllers.json')['render_controllers']
        for tint in range(16):
            self.assertNotIn('uv_anim',rc['controller.render.kg_a2770.pending_'+str(tint)])

    def test_held_layers_share_shell_socket_without_changing_native_id(self):
        placed={g['description']['identifier']:g for g in load(RP/'models/entity/a2770_placed/seasoning.geo.json')['minecraft:geometry']}
        geos=load(RP/'models/entity/bottle_held_contents.geo.json')['minecraft:geometry']
        self.assertEqual(len(geos),1)
        g=geos[0];root=g['bones'][0]
        self.assertEqual(g['description']['identifier'],'geometry.kg_bottle_held.combined')
        self.assertEqual(root,{'name':'grip','pivot':[0,24,0],
            'binding':'q.item_slot_to_bone_name(context.item_slot)'})
        bones={b['name']:b for b in g['bones']}
        self.assertEqual(set(bones),{'grip','shell'}|{f'pending_{i}' for i in range(16)})
        shell=load(RP/'models/entity/a286_hand/kg_a2733.seasoning_bottle_hand.geo.json')['minecraft:geometry'][0]
        self.assertEqual(bones['shell']['cubes'],shell['bones'][0]['cubes'])
        for child in g['bones'][1:]:
            self.assertEqual(child['parent'],'grip')
            self.assertEqual(child['pivot'],root['pivot'])
            self.assertNotIn('binding',child)
            self.assertNotIn('rotation',child)
        for tint in range(16):
            c=bones['pending_'+str(tint)]['cubes'][0];p=placed['geometry.kg_a2770.pending_'+str(tint)]['bones'][0]['cubes'][0]
            self.assertEqual(c['origin'],[p['origin'][0],p['origin'][1]+18,p['origin'][2]])
            self.assertEqual(c['size'],p['size'])
            self.assertEqual(set(c['uv']),set(p['uv']))
            for uv in c['uv'].values():
                self.assertEqual(uv,{'uv':[0,0],'uv_size':[32,32]})
            # Every half-cuboid lies inside the physical bottle body before
            # their common parent transform; this holds for FP and TP alike.
            for axis in range(3):
                self.assertGreaterEqual(c['origin'][axis],[-3,18,-3][axis])
                self.assertLessEqual(c['origin'][axis]+c['size'][axis],[3,24.5,3][axis])
        for item in ['empty_seasoning_bottle','pending_seasoning']:
            d=load(RP/f'attachables/{item}.attachable.json')['minecraft:attachable']['description']
            self.assertEqual(d['identifier'],'kaleidoscope_grilling:'+item)
            self.assertEqual(d['geometry'],{'default':'geometry.kg_bottle_held.combined'})
            self.assertEqual(d['materials']['contents'],'entity')
            self.assertEqual(len(d['render_controllers']),17)
            for tint,rc in enumerate(d['render_controllers'][:-1]):
                condition=next(iter(rc.values()))
                self.assertEqual(condition,'v.kg_bottle_layer_'+str(tint//2)+' > 0')
        controllers=load(RP/'render_controllers/bottle_held_contents.render_controllers.json')['render_controllers']
        for name,rc in controllers.items():
            self.assertEqual(rc['geometry'],'Geometry.default')
            visible={k:v for row in rc['part_visibility'] for k,v in row.items()}
            child=name.rsplit('.',1)[-1]
            self.assertEqual(visible,{'*':False,'grip':True,child:True})
        self.assertEqual(controllers['controller.render.kg_bottle_held.shell']['materials'],[{'*':'Material.default'}])

    def test_render_context_uses_initialized_numeric_animation_variables(self):
        controllers=load(RP/'render_controllers/bottle_held_contents.render_controllers.json')['render_controllers']
        ids=held.ingredient_ids()
        data=(BP/'scripts/a2770_placed_visual_data.js').read_text()
        palette=json.loads(re.search(r'INGREDIENT_COLORS=Object.freeze\((\{.*?\})\)',data).group(1))
        color_index=json.loads(re.search(r'PLACED_TINT_INDEX=Object.freeze\((\{.*?\})\)',data).group(1))
        pairs=[[0xB86B45,0xE0A56A]]+[palette[i] for i in ids]+[[0xB86B45,0xE0A56A]]
        for tint in range(16):
            rc=controllers['controller.render.kg_bottle_held.pending_'+str(tint)]
            self.assertEqual(rc['textures'],['Array.colors[v.kg_bottle_layer_'+str(tint//2)+']'])
            self.assertEqual(rc['arrays']['textures']['Array.colors'],
                ['Texture.pending_color_'+str(color_index[str(pair[tint%2])]) for pair in pairs])
            # No attachable-only context or entity query executes during texture
            # selection. Index 0 is valid before the first pre_animation pass.
            self.assertNotRegex(json.dumps(rc),r'\b(?:c|context|q|query)\.')
        for item in ['empty_seasoning_bottle','pending_seasoning']:
            d=load(RP/f'attachables/{item}.attachable.json')['minecraft:attachable']['description']
            self.assertNotRegex(json.dumps(d['render_controllers']),r'\b(?:c|context|q|query)\.')
            initial=d['scripts']['initialize'];pre=d['scripts']['pre_animation']
            self.assertEqual(initial,['v.kg_bottle_off_hand = 0;']+
                [f'v.kg_bottle_layer_{i} = 0;' for i in range(8)])
            self.assertEqual(pre[0],"v.kg_bottle_off_hand = c.item_slot == 'off_hand';")
            for i,expression in enumerate(pre[1:]):
                for hand in ['main','off']:
                    self.assertIn(f"c.owning_entity->q.property('kaleidoscope_grilling:bottle_{hand}_{i}')",expression)
                    self.assertIn(f"c.owning_entity->q.has_property('kaleidoscope_grilling:bottle_{hand}_{i}')",expression)
                self.assertIn('math.floor(math.clamp(',expression)
            # Evaluate the generated expressions with disjoint hand data. Also
            # exercise invalid/fractional values to prove every index is numeric,
            # integral and bounded before either layer's texture array reads it.
            source=json.dumps(pre)
            script="""
const expressions=EXPRESSIONS.map(s=>s.replaceAll('c.owning_entity->q.','owner_q.'));
for(const slot of ['main_hand','off_hand']) {
 const c={item_slot:slot},v={},main=[0,1,2,3,4,5,6,9],off=[8,7,6,5,4,3,2,1];
 const q={property:()=>{throw Error('Property read from attachable instead of owning entity')}};
 const owner_q={has_property:()=>true,property:name=>name.includes(':bottle_off_')?off[Number(name.split('_').at(-1))]:main[Number(name.split('_').at(-1))]};
 const math={floor:Math.floor,clamp:(x,a,b)=>Math.max(a,Math.min(b,x))};
 const evaluate=()=>{for(const expression of expressions)new Function('c','v','q','owner_q','math',expression)(c,v,q,owner_q,math)};
 evaluate();
 const expected=slot==='off_hand'?off:main;
 for(let i=0;i<8;i++)if(v['kg_bottle_layer_'+i]!==expected[i])throw Error('Hand data crossed: '+slot+' layer '+i);
 for(const value of [-8,2.9,20]) {
  owner_q.property=()=>value;
  evaluate();
  for(let i=0;i<8;i++)if(v['kg_bottle_layer_'+i]!==Math.floor(Math.max(0,Math.min(9,value))))throw Error('Unbounded texture index');
 }
 owner_q.has_property=()=>false;owner_q.property=()=>{throw Error('Missing property read')};evaluate();
 for(let i=0;i<8;i++)if(v['kg_bottle_layer_'+i]!==0)throw Error('Missing property did not clear layer');
}
""".replace('EXPRESSIONS',source)
            subprocess.run(['node','-e',script],check=True,capture_output=True,text=True)

    def test_generator_is_reproducible_and_player_budget_fits(self):
        for path,expected in held.build().items():
            self.assertEqual(load(path),expected,path)
        props=load(BP/'entities/player.json')['minecraft:entity']['description']['properties']
        self.assertLessEqual(len(props),32)
        for hand in ['main','off']:
            for i in range(8):
                self.assertEqual(props[f'kaleidoscope_grilling:bottle_{hand}_{i}'],{'type':'int','range':[0,9],'default':0,'client_sync':True})

if __name__=='__main__':
    unittest.main()
