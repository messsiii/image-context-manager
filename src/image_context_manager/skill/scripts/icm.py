"""Run the installed ICM runtime; no dependency on the current shell environment."""
import json
import os
from pathlib import Path
import sys
runtime = json.loads((Path(__file__).resolve().parents[1] / '.runtime.json').read_text())
os.execv(runtime['python'], [runtime['python'], '-m', 'image_context_manager.cli'] + sys.argv[1:])
