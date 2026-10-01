"""Read-only JSON validation for pre-commit.ci; UTF-8 BOM/CRLF are supported."""
from pathlib import Path
import json
import sys
errors=[]
for name in sys.argv[1:]:
    try:json.loads(Path(name).read_text(encoding='utf-8-sig'))
    except (ValueError,OSError) as error:errors.append(f'{name}: {error}')
if errors:raise SystemExit('\n'.join(errors))
print(f'Validated {len(sys.argv)-1} JSON files; no files rewritten')
