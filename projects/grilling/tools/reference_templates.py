"""Explicitly selected Java reference-template lowering. No source mutation."""
import copy, math

def prepare(model, allow_unapplied_tint=False):
    out=copy.deepcopy(model); warnings=[]
    for index, element in enumerate(out['elements']):
        original_from=element['from'][:]; original_to=element['to'][:]
        for face, data in element['faces'].items():
            if 'uv' not in data:
                if original_from != [0,0,0] or original_to != [16,16,16]:
                    raise ValueError('Implicit UV outside verified full-cube scope')
                data['uv']=[0,0,16,16]
                warnings.append({'code':'FULL_CUBE_IMPLICIT_UV_MATERIALIZED','element':index,'face':face})
            if 'tintindex' in data:
                if not allow_unapplied_tint:
                    raise ValueError('Tint needs explicit unresolved-material permission')
                warnings.append({'code':'SOURCE_TINT_REQUIRES_ENGINE_BINDING','element':index,'face':face,'tintindex':data.pop('tintindex'),'applied':False})
        rotation=element.get('rotation',{})
        if rotation.get('rescale'):
            if rotation['angle'] not in (-45,-22.5,0,22.5,45):
                raise ValueError('Unsupported Java rescale angle')
            axis='xyz'.index(rotation['axis']); pivot=rotation['origin']
            factor=1/math.cos(math.radians(rotation['angle']))
            for key in ('from','to'):
                element[key]=[pivot[i]+(v-pivot[i])*(1 if i==axis else factor) for i,v in enumerate(element[key])]
            rotation['rescale']=False
            warnings.append({'code':'JAVA_RESCALE_BAKED_BEFORE_ROTATION','element':index,'factor':factor})
    return out,warnings
