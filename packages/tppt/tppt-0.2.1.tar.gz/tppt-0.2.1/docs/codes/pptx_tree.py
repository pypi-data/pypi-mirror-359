import json

import tppt

print(json.dumps(tppt.Presentation("your.pptx").tree, indent=2, ensure_ascii=False))
