"""Source bounds, exact palette sampling and held dispatch; no client claim."""
import json
import re
import unittest
import subprocess
import tempfile
from unittest.mock import patch
from pathlib import Path
from PIL import Image
import a2861_bottle_held_visual_assets as held

ROOT=Path(__file__).resolve().parents[2]
RP=held.RP
BP=held.BP

def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

class BottleVisualAssets(unittest.TestCase):
    def test_generated_helpers_keep_native_no_damage_schema(self):
        for name in ['a2770_placed_seasoning','a2770_placed_oil']:
            actor=load(BP/f'entities/{name}.json')['minecraft:entity']
            self.assertEqual(actor['components']['minecraft:damage_sensor']['triggers'],[{'cause':'all','deals_damage':'no'}])

    def test_placed_single_pass_uses_every_pinned_ingredient_in_every_layer(self):
        source=load(ROOT/'development/gameplay_core/fixtures/a2770/grilling/kaleidoscope_grilling/models/item/seasoning_states/pending_8.json')
        g=load(RP/'models/entity/a2770_placed/pending_combined.geo.json')['minecraft:geometry'][0]
        self.assertEqual(g['description']['identifier'],'geometry.kg_a2770.pending_combined')
        self.assertEqual(g['bones'][0],{'name':'root','pivot':[0,0,0]})
        self.assertEqual(len(g['bones']),145)
        self.assertEqual((g['description']['texture_width'],g['description']['texture_height']),(128,64))
        desc=load(RP/'entity/a2770_placed_seasoning.entity.json')['minecraft:client_entity']['description']
        self.assertEqual(len(desc['render_controllers']),2)
        self.assertEqual(desc['render_controllers'][1],{'controller.render.kg_a2770.pending':"q.property('kaleidoscope_grilling:ready') && q.property('kaleidoscope_grilling:mode') == 1"})
        rc=load(RP/'render_controllers/a2770_placed.render_controllers.json')['render_controllers']['controller.render.kg_a2770.pending']
        self.assertEqual(rc['geometry'],'Geometry.pending')
        self.assertEqual(rc['textures'],['Texture.pending'])
        self.assertEqual(rc['materials'],[{'*':'Material.default'}])
        self.assertNotIn('arrays',rc)
        self.assertNotIn('uv_anim',rc)
        visible={k:v for row in rc['part_visibility'] for k,v in row.items()}
        self.assertEqual({k:v for k,v in visible.items() if not k.startswith('pending_')},{'*':False,'root':True})
        pairs=held.palette_pairs()
        with Image.open(RP/(desc['textures']['pending']+'.png')) as image:
            atlas=image.convert('RGBA')
        for bone in g['bones'][1:]:
            match=re.fullmatch(r'pending_(\d+)_color_(\d+)',bone['name'])
            self.assertIsNotNone(match)
            tint,value=map(int,match.groups())
            self.assertEqual(bone['parent'],'root')
            self.assertNotIn('binding',bone)
            element=next(e for e in source['elements'] if any(f.get('tintindex')==tint for f in e['faces'].values()))
            cube=bone['cubes'][0]
            self.assertEqual(cube['origin'],[8-element['to'][0],element['from'][1],element['from'][2]-8])
            self.assertEqual(cube['size'],[element['to'][i]-element['from'][i] for i in range(3)])
            self.assertEqual(set(cube['uv']),set(element['faces']))
            self.assertEqual(visible[bone['name']],f"q.property('kaleidoscope_grilling:layer_{tint//2}') == {value}")
            rgb=pairs[value][tint%2];rgba=((rgb>>16)&255,(rgb>>8)&255,rgb&255,255)
            for uv in cube['uv'].values():
                x,y=uv['uv'];self.assertEqual(uv['uv_size'],[8,8])
                self.assertEqual(atlas.crop((x-4,y-4,x+12,y+12)).getcolors(),[(256,rgba)])
        props=load(BP/'entities/a2770_placed_seasoning.json')['minecraft:entity']['description']['properties']
        self.assertEqual(len(props),12)
        for i in range(8):
            self.assertEqual(props[f'kaleidoscope_grilling:layer_{i}'],{'type':'int','range':[0,9],'default':0,'client_sync':True})
        self.assertFalse(any(':color_' in name for name in props))

    def test_placed_bounds_and_opaque_palette_match_source(self):
        source=load(ROOT/'development/gameplay_core/fixtures/a2770/grilling/kaleidoscope_grilling/models/item/seasoning_states/pending_8.json')
        geos={g['description']['identifier']:g for g in load(RP/'models/entity/a2770_placed/seasoning.geo.json')['minecraft:geometry']}
        for tint in range(16):
            element=next(e for e in source['elements'] if any(f.get('tintindex')==tint for f in e['faces'].values()))
            g=geos['geometry.kg_a2770.pending_'+str(tint)]
            cube=g['bones'][0]['cubes'][0]
            self.assertEqual(cube['origin'],[8-element['to'][0],element['from'][1],element['from'][2]-8])
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
        pending=rc['controller.render.kg_a2770.pending']
        self.assertNotIn('uv_anim',pending)
        self.assertNotIn('arrays',pending)
        self.assertEqual(pending['textures'],['Texture.pending'])

    def test_held_layers_share_shell_socket_without_changing_native_id(self):
        placed={g['description']['identifier']:g for g in load(RP/'models/entity/a2770_placed/seasoning.geo.json')['minecraft:geometry']}
        geos=load(RP/'models/entity/bottle_held_contents.geo.json')['minecraft:geometry']
        self.assertEqual(len(geos),65)
        g=geos[0];root=g['bones'][0]
        self.assertEqual(g['description']['identifier'],'geometry.kg_bottle_held.combined')
        self.assertEqual(root,{'name':'grip','pivot':[0,24,0],
            'binding':'q.item_slot_to_bone_name(context.item_slot)'})
        bones={b['name']:b for b in g['bones']}
        self.assertEqual(set(bones),{'grip','shell'}|{f'pending_{i}_color_{j}' for i in range(16) for j in range(1,10)})
        self.assertEqual(g['description']['texture_width'],128)
        self.assertEqual(g['description']['texture_height'],128)
        shell=load(RP/'models/entity/a286_hand/kg_a2733.seasoning_bottle_hand.geo.json')['minecraft:geometry'][0]
        self.assertEqual(bones['shell']['cubes'],shell['bones'][0]['cubes'])
        for child in g['bones'][1:]:
            self.assertEqual(child['parent'],'grip')
            self.assertEqual(child['pivot'],root['pivot'])
            self.assertNotIn('binding',child)
            self.assertNotIn('rotation',child)
        pairs=held.palette_pairs()
        with Image.open(RP/(held.ATLAS+'.png')) as image:
            atlas=image.convert('RGBA')
        for tint in range(16):
            for value in range(1,10):
                c=bones[f'pending_{tint}_color_{value}']['cubes'][0]
                p=placed[f'geometry.kg_a2770.pending_{tint}']['bones'][0]['cubes'][0]
                self.assertEqual(c['origin'],[p['origin'][0],p['origin'][1]+18,p['origin'][2]])
                self.assertEqual(c['size'],p['size'])
                self.assertEqual(set(c['uv']),set(p['uv']))
                rgb=pairs[value][tint%2]
                rgba=((rgb>>16)&255,(rgb>>8)&255,rgb&255,255)
                for uv in c['uv'].values():
                    x,y=uv['uv'];self.assertEqual(uv['uv_size'],[8,8])
                    self.assertEqual(atlas.crop((x,y,x+8,y+8)).getcolors(),[(64,rgba)])
                for axis in range(3):
                    self.assertGreaterEqual(c['origin'][axis],[-3,18,-3][axis])
                    self.assertLessEqual(c['origin'][axis]+c['size'][axis],[3,24.5,3][axis])
        for item in ['empty_seasoning_bottle','pending_seasoning']:
            d=load(RP/f'attachables/{item}.attachable.json')['minecraft:attachable']['description']
            self.assertEqual(d['identifier'],'kaleidoscope_grilling:'+item)
            self.assertEqual(d['geometry'],{'default':'geometry.kg_bottle_held.combined'})
            self.assertEqual(d['materials']['contents'],'entity')
            self.assertEqual(d['render_controllers'],['controller.render.kg_bottle_held.dynamic'])
            self.assertEqual(d['textures'],{'default':held.ATLAS})
        controllers=load(RP/'render_controllers/bottle_held_contents.render_controllers.json')['render_controllers']
        for name,rc in controllers.items():
            self.assertEqual(rc['geometry'],'Geometry.default')
            self.assertEqual(rc['textures'],['Texture.default'])
            self.assertEqual(rc['materials'],[{'*':'Material.contents'},{'shell':'Material.default'}])
        visible={k:v for row in controllers['controller.render.kg_bottle_held.dynamic']['part_visibility'] for k,v in row.items()}
        self.assertEqual({k:v for k,v in visible.items() if not k.startswith('pending_')},{'*':False,'grip':True,'shell':True})
        for tint in range(16):
            for value in range(1,10):
                self.assertEqual(visible[f'pending_{tint}_color_{value}'],f'v.kg_bottle_layer_{tint//2} == {value}')

    def test_render_context_uses_initialized_numeric_animation_variables(self):
        controllers=load(RP/'render_controllers/bottle_held_contents.render_controllers.json')['render_controllers']
        for rc in controllers.values():
            # RC only selects static bones from initialized numeric variables.
            self.assertNotIn('uv_anim',rc)
            self.assertNotIn('arrays',rc)
            self.assertNotRegex(json.dumps(rc),r'\b(?:c|context|q|query)\.')
        for item in ['empty_seasoning_bottle','pending_seasoning']:
            d=load(RP/f'attachables/{item}.attachable.json')['minecraft:attachable']['description']
            self.assertNotRegex(json.dumps(d['render_controllers']),r'\b(?:c|context|q|query)\.')
            initial=[v for v in d['scripts']['initialize'] if v.startswith('v.kg_bottle_')];pre=[v for v in d['scripts']['pre_animation'] if v.startswith('v.kg_bottle_')]
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

    def test_all_bottle_gui_icons_cannot_change_particle_palette(self):
        # Canonical bottle particle sprite, independently pinned by the source
        # audit, must be sampled even when GUI keys, paths or pixels change.
        names = ['empty_seasoning_bottle', 'pending_seasoning', 'special_seasoning']
        names += [f'special_seasoning_r{r}_v{v}' for r in range(1, 9) for v in range(8)]
        names += [f'{state}_seasoning_f{fill}' for state in ['partial', 'pending'] for fill in range(1, 9)]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bp, rp = root / 'behavior_pack', root / 'resource_pack'
            for path in [bp / 'items', bp / 'scripts', rp / 'textures/items', rp / 'textures/blocks']:
                path.mkdir(parents=True)
            (bp / 'scripts/data.js').write_text('export const PROFILE_BY_ITEM=Object.freeze({});')
            (rp / 'textures/blocks/seasoning_bottle.png').write_bytes((RP / 'textures/blocks/seasoning_bottle.png').read_bytes())
            atlas = {}
            for name in [*names, 'ordinary_item']:
                key = 'rebaked_' + name
                atlas[key] = {'textures': 'textures/items/gui'}
                doc = {'minecraft:item': {'description': {'identifier': 'kaleidoscope_grilling:' + name},
                                         'components': {'minecraft:icon': key}}}
                (bp / f'items/{name}.json').write_text(json.dumps(doc))
            (rp / 'textures/item_texture.json').write_text(json.dumps({'texture_data': atlas}))
            gui = rp / 'textures/items/gui.png'
            with patch.object(held.placed, 'BP', bp), patch.object(held.placed, 'RP', rp):
                Image.new('RGBA', (16, 16), (255, 0, 255, 255)).save(gui)
                before = held.placed.ingredient_palette()
                Image.new('RGBA', (16, 16), (0, 255, 0, 255)).save(gui)
                after = held.placed.ingredient_palette()
            for name in names:
                with self.subTest(item=name):
                    identifier = 'kaleidoscope_grilling:' + name
                    self.assertEqual(before[identifier], [6756368, 8339631])
                    self.assertEqual(after[identifier], before[identifier])
            self.assertNotEqual(before['kaleidoscope_grilling:ordinary_item'], after['kaleidoscope_grilling:ordinary_item'])

    def test_generator_is_reproducible_and_player_budget_fits(self):
        for path,expected in held.build().items():
            self.assertEqual(path.read_bytes() if isinstance(expected,bytes) else load(path),expected,path)
        props=load(BP/'entities/player.json')['minecraft:entity']['description']['properties']
        self.assertLessEqual(len(props),32)
        for hand in ['main','off']:
            for i in range(8):
                self.assertEqual(props[f'kaleidoscope_grilling:bottle_{hand}_{i}'],{'type':'int','range':[0,9],'default':0,'client_sync':True})

if __name__=='__main__':
    unittest.main()
