"""Enumerate every gate that would fail for a PipelineNews release, not just the first.

The deploy gate stops at the first failed require(). That answers "why is it red" but not the
question the architect actually needs: if the schema constant were updated, would it deploy, or
is there a second wall? This replaces require() with a collector so one run walks as far as the
code physically can, and reports every assertion that failed on the way.

It modifies nothing in the repository. Run against a throwaway clone.

    python pn_walls.py <clone-root> <release-id>
"""
import importlib.util
import sys
import traceback
from pathlib import Path

root = Path(sys.argv[1]).resolve()
release_id = sys.argv[2]

mod_path = root / 'atman' / '202608262014-build-pages.py'
spec = importlib.util.spec_from_file_location('buildpages', mod_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

failures = []
_original = mod.require


def collecting_require(condition, message):
    if not condition:
        failures.append(message)
    # deliberately does not raise: we want the walls behind this one


mod.require = collecting_require

print('release:', release_id)
print('schema in its release-manifest:',
      (root / 'releases' / release_id / 'release-manifest.json').exists()
      and __import__('json').loads((root / 'releases' / release_id / 'release-manifest.json').read_text())
      .get('schema'))
print()

crashed = None
try:
    mod.validate_timestamp_folder_release(root, release_id)
except Exception as exc:
    crashed = ''.join(traceback.format_exception_only(type(exc), exc)).strip()

if failures:
    print('ASSERTIONS THAT FAILED (in order encountered):')
    for i, f in enumerate(failures, 1):
        print('  %2d. %s' % (i, f))
else:
    print('NO ASSERTION FAILED once the schema check was made non-fatal.')

if crashed:
    print()
    print('execution could not continue past that point:')
    print('  ' + crashed)
    print('  (a crash here usually means an earlier assertion guarded this code,')
    print('   so treat everything after it as unmeasured rather than passing)')
else:
    print()
    print('the validator ran to completion.')
