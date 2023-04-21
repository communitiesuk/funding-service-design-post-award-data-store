from pathlib import Path
from typing import Any, Dict

import prance


def get_bundled_specs(main_file: str) -> Dict[str, Any]:
    path_string = str(Path(__file__).parent / main_file)
    parser = prance.ResolvingParser(path_string, strict=False)
    parser.parse()
    return parser.specification
