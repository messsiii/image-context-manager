"""Run with installed wheel and -I, outside the source checkout.

python -I /path/tools/verify_install.py --tests /path/tests --out NEW_DIR
Does not create a venv or install packages; run after the README installation.
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import sys
import unittest

parser = argparse.ArgumentParser()
parser.add_argument('--tests',type=Path,required=True)
parser.add_argument('--out',type=Path,required=True)
args=parser.parse_args()
blocked=[]
def no_network(event, details):
    if event in {'socket.connect','socket.getaddrinfo','subprocess.Popen','os.system'}:
        blocked.append(event)
        raise RuntimeError('Offline verification forbids network/process execution: '+event)
sys.addaudithook(no_network)
import image_context_manager
from image_context_manager.demo import run
installed_path=Path(image_context_manager.__file__).resolve()
assert str(installed_path).startswith(str(Path(sys.prefix).resolve())+os.sep), 'Not using venv-installed package'
report=run(args.out/'demo')
suite=unittest.defaultTestLoader.discover(str(args.tests.resolve()))
result=unittest.TextTestRunner(verbosity=2).run(suite)
record={'python':platform.python_version(),'platform':platform.system()+' '+platform.machine(),
        'distribution_version':importlib.metadata.version('image-context-manager'),
        'pillow_version':importlib.metadata.version('Pillow'),
        'package_loaded_from_venv_site_packages':True,
        'runtime_network_and_process_guard_enabled':True,'blocked_events':blocked,
        'tests_run':result.testsRun,'tests_passed':result.wasSuccessful(),
        'demo':report,
        'installed_modules_sha256':{name:hashlib.sha256((installed_path.parent/name).read_bytes()).hexdigest() for name in ['core.py','history.py','local.py','demo.py','agent.py','cli.py']},
        'scope':'Same-implementer clean install validation; not independent developer reproduction, model/network benchmark, ASC or UI review'}
(args.out/'verification.json').write_text(json.dumps(record,indent=2)+'\n')
assert result.wasSuccessful() and not blocked
print(json.dumps(record,indent=2))
