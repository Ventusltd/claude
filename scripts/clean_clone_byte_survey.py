"""clean_clone_byte_survey.py - what the bytes are, measured where the bytes are true.

WHY THIS CANNOT RUN ON THE LAPTOP

`git status` compares THROUGH `.gitattributes` normalisation. It reports a tree clean while
the disk holds CRLF and the blob holds LF. Fifteen of eighteen repositories here are in that
state. So every measurement that depends on file bytes - a digest, a checksum manifest, a
character ceiling - reads a different number on this Windows working tree than it will read
anywhere the artefact is actually served. A ceiling check run on the laptop is not wrong by
a rounding error; it is measuring a different file.

A GitHub runner checks out from the blob. It is the cheapest clean clone in the estate, it
is free on a public repository, and it can hold several repositories side by side. That is
why this survey belongs in the cloud and not here.

WHAT IT MEASURES

1. LINE ENDINGS, per repository, from `git ls-files --eol` on a fresh checkout:
   `i/crlf` (the blob itself is CRLF) is a different fact from `w/crlf` (only the disk is),
   and they are counted separately. One repository legitimately ships CRLF in the blob, so a
   single combined number would report a correct repository as broken.

   AND THE TRAP IN RUNNING THIS IN THE CLOUD AT ALL: on a Linux runner `w/crlf` is 0 for
   every repository BY CONSTRUCTION, because git only writes CRLF into a checkout on a
   platform that asks for it. Reading that as "the CRLF problem is fixed" would be a wrong
   conclusion delivered by this instrument. The runner answers what the repository SHIPS
   (`i/crlf`, and whether renormalising changes anything); the laptop answers what its own
   disk HOLDS. The board says so in as many words so the two are never confused.

2. `.gitattributes` CLASSIFICATION. The canonical line is `* text=auto eol=lf`. GitHub's
   default template is the bare `* text=auto`, which normalises on commit but lets the
   checkout be CRLF - the exact trap the estate's own note names. Bare is reported as `bare`,
   not as `present`, because "has a .gitattributes" is the answer that hides the problem.

3. RENORMALISATION. `git add --renormalize .` on a clean checkout must change nothing. Files
   it changes are stored differently from what `.gitattributes` requires.

4. THE CHARACTER CEILING, measured three ways, because THREE DIFFERENT NUMBERS ARE ENFORCED
   in this estate and they are not the same:

       368640   characters  the ceiling the cartridge proof ASSERTS (0.9 x 409600)
       400000   bytes       the ceiling tools/scope/loop.mjs lint GATES
       409600   bytes       the composer boundary, reported but not enforced

   and because characters are not bytes. The proof measures `source.length` - UTF-16 code
   units - while the lint measures `statSync().size`. Cartridges contain non-ASCII, so the
   two diverge, and a file can pass one and fail the other. Both are reported per cartridge
   with the divergence named, so nobody has to remember which gauge they were reading.

5. MANIFEST IDENTITY. Every cartridge `sha256` in `atlas/current.json` recomputed with the
   estate's own publication rule: text extensions are LF-normalised before hashing, binaries
   are hashed raw. A mismatch here is a manifest that describes a file the repository does
   not contain.

THIS IS AN INFORMATIONAL SURVEY. IT EXITS 0 ON EVERY FINDING, ALWAYS.

The gates that must block already exist and already fail loudly - `202608312212-cartridge-proof.yml`
in gridatlas is the model. This is not one of them, and a non-zero exit here would both mail
the actor and misrepresent what the job is. Findings live in the JSON and the board. If you
are about to "fix" this into a gate: don't. The gate is elsewhere and it is already red when
it needs to be.

    python scripts/clean_clone_byte_survey.py --root /path/holding/clones \
        --out survey.json --board docs/boards/bytes.md
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time

# The estate's publication rule, from gridatlas tools/scope/lib.mjs sha256PublishedFile().
LF_NORMALISED = {'.js', '.mjs', '.cjs', '.css', '.html', '.htm', '.json', '.geojson',
                 '.txt', '.md', '.yml', '.yaml', '.svg'}

CARTRIDGE_CEILING_CHARS = 368640     # what the proof asserts
LOOP_GATE_BYTES = 400000             # what the lint gates
COMPOSER_BOUNDARY_BYTES = 409600     # what is reported

CANONICAL_ATTR = re.compile(r'^\s*\*\s+text=auto\s+eol=lf\s*$', re.M)
BARE_ATTR = re.compile(r'^\s*\*\s+text=auto\s*$', re.M)


def git(repo, *args, timeout=180):
    p = subprocess.run(['git', '-C', repo, *args], capture_output=True, text=True,
                       timeout=timeout, errors='replace')
    return p.returncode, p.stdout, p.stderr


def sha256_published(path):
    """Bytes as published: LF-normalised for text, raw for everything else."""
    with open(path, 'rb') as f:
        b = f.read()
    if os.path.splitext(path)[1].lower() in LF_NORMALISED:
        b = b.replace(b'\r\n', b'\n')
    return hashlib.sha256(b).hexdigest()


def eol_census(repo):
    rc, out, _ = git(repo, 'ls-files', '--eol')
    if rc != 0:
        return {'error': 'ls-files --eol failed'}
    c = {'files': 0, 'i_crlf': 0, 'i_mixed': 0, 'w_crlf': 0, 'w_mixed': 0}
    for line in out.splitlines():
        c['files'] += 1
        if 'i/crlf' in line:
            c['i_crlf'] += 1
        if 'i/mixed' in line:
            c['i_mixed'] += 1
        if 'w/crlf' in line:
            c['w_crlf'] += 1
        if 'w/mixed' in line:
            c['w_mixed'] += 1
    return c


def attributes(repo):
    p = os.path.join(repo, '.gitattributes')
    if not os.path.exists(p):
        return {'state': 'absent'}
    with open(p, 'rb') as f:
        raw = f.read()
    txt = raw.decode('utf-8', 'replace')
    if CANONICAL_ATTR.search(txt):
        state = 'canonical'
    elif BARE_ATTR.search(txt):
        # Normalises on commit, permits a CRLF checkout. The named trap.
        state = 'bare'
    else:
        state = 'other'
    return {'state': state, 'bytes': len(raw)}


def renormalise(repo):
    """On a clean checkout this must change nothing. Names the files if it does.

    The index is restored with `git reset` afterwards, which is safe ONLY because this runs
    on a fresh clone. On a working tree it would unstage whatever someone else had staged,
    so a dirty index is refused rather than surveyed - a measurement is never worth another
    lane's work in progress.
    """
    rc, staged, _ = git(repo, 'diff', '--cached', '--name-only')
    if rc != 0 or staged.strip():
        return {'skipped': 'index is not empty; this is not a fresh clone',
                'staged': len(staged.split())}
    rc, _, _ = git(repo, 'add', '--renormalize', '.')
    if rc != 0:
        return {'error': 'renormalize failed'}
    rc, out, _ = git(repo, 'diff', '--cached', '--name-only')
    files = [f for f in out.splitlines() if f]
    git(repo, 'reset', '-q')
    return {'changed': len(files), 'files': files[:40]}


def cartridges(repo):
    """gridatlas only: the character ceiling on all three gauges, plus manifest identity."""
    cur = os.path.join(repo, 'atlas', 'current.json')
    if not os.path.exists(cur):
        return None
    with open(cur, 'rb') as f:
        doc = json.loads(f.read().decode('utf-8'))
    rows = []
    for c in doc.get('cartridges', []):
        rel = (c.get('path') or '').lstrip('./')
        path = os.path.join(repo, 'atlas', rel)
        row = {'id': c.get('id'), 'generation': c.get('generation'), 'path': c.get('path'),
               'declared_sha256': c.get('sha256')}
        if not os.path.exists(path):
            row['state'] = 'missing'
            rows.append(row)
            continue
        with open(path, 'rb') as f:
            raw = f.read()
        src = raw.decode('utf-8', 'replace')
        row.update({
            'bytes': len(raw),
            'chars': len(src),
            # Characters and bytes diverge on every non-ASCII glyph. Naming the gap stops
            # the two gauges being quoted interchangeably.
            'bytes_minus_chars': len(raw) - len(src),
            'crlf_pairs': raw.count(b'\r\n'),
            'chars_vs_proof_ceiling': len(src) - CARTRIDGE_CEILING_CHARS,
            'bytes_vs_lint_gate': len(raw) - LOOP_GATE_BYTES,
            'bytes_vs_composer_boundary': len(raw) - COMPOSER_BOUNDARY_BYTES,
            'over_proof_ceiling': len(src) >= CARTRIDGE_CEILING_CHARS,
            'over_lint_gate': len(raw) > LOOP_GATE_BYTES,
            'measured_sha256': sha256_published(path),
        })
        row['sha256_matches'] = (row['measured_sha256'] == row['declared_sha256'])
        row['state'] = 'ok' if row['sha256_matches'] and not row['over_lint_gate'] else 'check'
        rows.append(row)
    return {'generation': doc.get('generation'), 'architecture': doc.get('architecture'),
            'cartridge_order': doc.get('cartridge_order'), 'rows': rows}


def survey_repo(root, name):
    repo = os.path.join(root, name)
    if not os.path.isdir(os.path.join(repo, '.git')):
        return {'repo': name, 'state': 'not-a-clone'}
    rc, head, _ = git(repo, 'rev-parse', 'HEAD')
    out = {'repo': name, 'state': 'surveyed', 'head': head.strip()[:12],
           'eol': eol_census(repo), 'gitattributes': attributes(repo),
           'renormalize': renormalise(repo)}
    carts = cartridges(repo)
    if carts:
        out['cartridges'] = carts
    return out


def board(res):
    L = []
    A = L.append
    A('# Clean-clone byte survey')
    A('')
    A('Measured on GitHub runners, which check out from the blob. The laptop cannot answer')
    A('these questions: `git status` compares through `.gitattributes`, so it reports clean')
    A('while the disk holds CRLF and the blob holds LF.')
    A('')
    A('INFORMATIONAL: this job exits 0 on every finding. The gates that must block already')
    A('exist and already fail loudly. This is a report.')
    A('')
    A('- surveyed at: `%s`' % res['generated_at'])
    A('- repositories: %d' % len(res['repos']))
    A('')
    A('## Line endings and `.gitattributes`')
    A('')
    A('`i/crlf` means the BLOB is CRLF - **the bytes that ship**, and the column to read')
    A('here. `w/crlf` means only the checkout is.')
    A('')
    A('**Do not read `w/crlf` from a Linux runner as good news.** Git only writes CRLF into')
    A('a checkout on a platform configured to want it, so on `ubuntu-24.04` this column is')
    A('0 by construction and says nothing about the Windows working tree, where 15 of 18')
    A('repositories hold CRLF on disk. Two different machines answer two different')
    A('questions: the runner says what the repository SHIPS, the laptop says what its own')
    A('disk HOLDS. `renormalize changes` and the `.gitattributes` column are the ones that')
    A('carry across both.')
    A('')
    A('| repo | head | tracked | i/crlf | w/crlf | mixed | .gitattributes | renormalize changes |')
    A('|---|---|---:|---:|---:|---:|---|---:|')
    for r in res['repos']:
        if r['state'] != 'surveyed':
            A('| `%s` | - | - | - | - | - | %s | - |' % (r['repo'], r['state']))
            continue
        e = r['eol']
        A('| `%s` | `%s` | %d | %d | %d | %d | %s | %d |'
          % (r['repo'], r['head'], e.get('files', 0), e.get('i_crlf', 0), e.get('w_crlf', 0),
             e.get('i_mixed', 0) + e.get('w_mixed', 0),
             r['gitattributes']['state'], r['renormalize'].get('changed', -1)))
    A('')
    bare = [r['repo'] for r in res['repos']
            if r.get('gitattributes', {}).get('state') == 'bare']
    if bare:
        A('`bare` means the file carries GitHub\'s default `* text=auto` with no `eol=lf`.')
        A('It normalises on commit and permits a CRLF checkout, which is the trap: %s.'
          % ', '.join('`%s`' % b for b in bare))
        A('')

    carts = [r for r in res['repos'] if r.get('cartridges')]
    for r in carts:
        c = r['cartridges']
        A('## Cartridge ceilings in `%s` (generation `%s`)' % (r['repo'], c['generation']))
        A('')
        A('Three ceilings are enforced in this estate and they are three different numbers:')
        A('**%d characters** is what the proof asserts, **%d bytes** is what `loop.mjs lint`'
          % (CARTRIDGE_CEILING_CHARS, LOOP_GATE_BYTES))
        A('gates, **%d bytes** is the composer boundary that is reported but not enforced.'
          % COMPOSER_BOUNDARY_BYTES)
        A('Characters are UTF-16 code units and bytes are bytes; the `b-c` column is how far')
        A('apart the two gauges are for that file.')
        A('')
        A('| cartridge | chars | bytes | b-c | clear of %d chars | clear of %d bytes | sha256 |'
          % (CARTRIDGE_CEILING_CHARS, LOOP_GATE_BYTES))
        A('|---|---:|---:|---:|---:|---:|---|')
        for x in c['rows']:
            if x['state'] == 'missing':
                A('| `%s` | - | - | - | - | - | MISSING |' % x['id'])
                continue
            A('| `%s` | %d | %d | %d | %d | %d | %s |'
              % (x['id'], x['chars'], x['bytes'], x['bytes_minus_chars'],
                 -x['chars_vs_proof_ceiling'], -x['bytes_vs_lint_gate'],
                 'matches' if x['sha256_matches'] else '**MISMATCH**'))
        A('')
    return '\n'.join(L) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', required=True, help='directory holding the fresh clones')
    ap.add_argument('--repos', nargs='*', default=None)
    ap.add_argument('--out', default='byte-survey.json')
    ap.add_argument('--board', default='')
    a = ap.parse_args()

    names = a.repos or sorted(d for d in os.listdir(a.root)
                              if os.path.isdir(os.path.join(a.root, d, '.git')))
    res = {'schema': 'ventus.clean-clone-byte-survey.v1',
           'generated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
           'ceilings': {'proof_chars': CARTRIDGE_CEILING_CHARS,
                        'lint_gate_bytes': LOOP_GATE_BYTES,
                        'composer_boundary_bytes': COMPOSER_BOUNDARY_BYTES},
           'repos': [survey_repo(a.root, n) for n in names]}

    with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(res, f, indent=1)
        f.write('\n')
    if a.board:
        os.makedirs(os.path.dirname(a.board) or '.', exist_ok=True)
        with open(a.board, 'w', encoding='utf-8', newline='\n') as f:
            f.write(board(res))

    surveyed = [r for r in res['repos'] if r['state'] == 'surveyed']
    print('repos %d · blob-CRLF files %d · checkout-CRLF files %d · renormalize would change %d '
          '· bare .gitattributes %d'
          % (len(surveyed),
             sum(r['eol'].get('i_crlf', 0) for r in surveyed),
             sum(r['eol'].get('w_crlf', 0) for r in surveyed),
             sum(r['renormalize'].get('changed', 0) for r in surveyed),
             sum(1 for r in surveyed if r['gitattributes']['state'] == 'bare')),
          file=sys.stderr)

    # Informational. Always 0. See the module docstring before changing this.
    return 0


if __name__ == '__main__':
    sys.exit(main())
