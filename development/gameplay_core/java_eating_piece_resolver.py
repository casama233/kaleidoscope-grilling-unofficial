"""Pinned Java resolver for the helper-hand food mesh; no inventory mutation.

Model resolution is intentionally separate from renderer admission. In
particular, a missing asset must not be replaced by a guessed food model.
"""
import hashlib
import json
from pathlib import Path
import re

FIXTURE = Path(__file__).parent / 'fixtures/java-eating-piece-1.1.1.json'
SOURCE = json.loads(FIXTURE.read_text())
assert hashlib.sha256(SOURCE['content'].encode()).hexdigest() == SOURCE['sha256']
assert SOURCE['sha256'] == 'f89f3eb1dd742fa5ba79407ce11d5388c889599f4f211e0f0f9bec889b5676af'
NAMESPACE = 'kaleidoscope_grilling'
INGREDIENT_MODELS = frozenset(('secret_skewer', 'mysterious_skewer', 'dark_grilling'))

def fixed_model(item_id, profile):
    """SkewerEatingPiece.fixedModel's exact model identifier, not an existence guess."""
    if not isinstance(item_id, str) or ':' not in item_id:
        return None
    namespace, path = item_id.split(':', 1)
    if namespace != NAMESPACE or path in INGREDIENT_MODELS:
        return None
    raw = path.startswith('raw_')
    base = re.sub(r'^(raw_|grilled_)', '', path, count=1)
    group = 1 if profile == 'ONE' else 3
    suffix = '_raw' if raw else ''
    folder = base[:-7] if base.endswith('_skewer') else base
    return f'{NAMESPACE}:item/fixed_skewers/{folder}/{base}{suffix}_piece_{group}'

def ingredient_index(profile, ingredient_count):
    """Choose a snapshot row only. Java clones it to count one at render time."""
    if not isinstance(ingredient_count, int) or ingredient_count <= 0:
        return None
    return 0 if profile == 'ONE' else ingredient_count - 1

def model_path(root, model_id):
    namespace, path = model_id.split(':', 1)
    return Path(root) / 'projects/grilling/source_snapshots/common/src/main/resources/assets' / namespace / 'models' / (path + '.json')

def available_fixed_piece(root, item_id, profile):
    model = fixed_model(item_id, profile)
    return model if model is not None and model_path(root, model).is_file() else None
