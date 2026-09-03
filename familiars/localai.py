"""localai.py - the clerical mind that runs on this machine's own silicon.

WHY THIS EXISTS

A large model's attention is the scarce resource in this estate. Reading a 4,000-line
CI log to find which step died, describing what an untracked file appears to be, turning
a diff into two lines - none of that needs a frontier model. It needs a competent reader
that is already resident in VRAM and answers in under a second.

So it runs here. Two adapters on this laptop, both working:

    gpu   RTX 5070 Laptop, CUDA 13.1, sm_120   qwen3:4b-instruct-2507-q4_K_M   :11434
    igpu  Intel(R) Graphics, Vulkan            qwen3:0.6b                      :11435

The discrete card carries the model that needs to be right. The integrated GPU - which
Ollama drops by default, and which cost nothing because it is soldered to the CPU - carries
the short classifications. Measured together they do more work than either alone.

    python familiars/localai.py --health
    python familiars/localai.py --bench
    python familiars/localai.py --job classify-ci-failure --input <log path>
    python familiars/localai.py --job classify-ci-failure --input Ventusltd/cvaa#33715076001
    python familiars/localai.py --job summarise-commit    --input <sha> [--repo gridatlas]
    python familiars/localai.py --job triage-untracked    --input gridatlas
    python familiars/localai.py --serve-igpu     # start the Intel-pinned server

MEASURED, NOT ASSUMED

The failure mode this file is written against is a model that silently ran on the CPU, or
an endpoint that was never up, while the caller got a fluent answer and believed it. So:

  - --health FAILS with a non-zero exit when the endpoint is down. It never falls back to a
    cheerful default, and it never substitutes one device for another silently.
  - Offload is read from /api/ps as size_vram / size. Anything below 100% is reported as the
    number, not as a pass. A model half on the CPU is a measurement, not an error - but it is
    never described as "on the GPU".
  - Every job that cannot find its subject RAISES. A missing log, an unknown sha, a repo that
    is not there: these exit non-zero. A skip is not a pass.
  - Throughput is read from Ollama's own eval_count / eval_duration, which counts generated
    tokens against the generation clock only. Load time is reported separately, because
    folding a cold start into tokens/s is how a fast model gets reported as a slow one.

WINDOWS NOTES

python3 is a broken Store stub here; this file is run with `python`. Requests are stdlib
urllib - no dependency is added to requirements.txt for this. Per-request num_ctx is
deliberately NOT sent: it differs from the server's loaded context and forces a full model
reload, which was measured costing ~5 s and evicting the resident weights. Context is set
once on the server via OLLAMA_CONTEXT_LENGTH.
"""

import argparse
import io
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor

GITHUB = r'C:\Users\vikra\OneDrive\Documents\GitHub'
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OLLAMA_EXE = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Ollama', 'ollama.exe')

DEVICES = {
    'gpu': {
        'endpoint': 'http://127.0.0.1:11434',
        'model': 'qwen3:4b-instruct-2507-q4_K_M',
        'adapter': 'NVIDIA GeForce RTX 5070 Laptop GPU',
        'backend': 'CUDA',
        # The -instruct-2507 line has no thinking mode; sending think=false is a 400 here.
        'thinking': False,
    },
    'igpu': {
        'endpoint': 'http://127.0.0.1:11435',
        'model': 'qwen3:0.6b',
        'adapter': 'Intel(R) Graphics',
        'backend': 'Vulkan',
        # Plain qwen3:0.6b IS a thinking model, and that is a trap for short clerical jobs:
        # measured on 2026-09-03 it spent all 90 permitted tokens inside <think> and returned
        # response="" with done_reason="length" - 392 thinking characters, nothing to show the
        # caller. Thinking is switched off explicitly rather than paid for in a budget this
        # small. See the empty-completion guard in generate().
        'thinking': True,
    },
}

# Jobs are routed to the device that suits them. The 0.6B on the iGPU is competent at
# "name this file" and is not trusted with a diff.
JOB_DEVICE = {
    'classify-ci-failure': 'gpu',
    'summarise-commit': 'gpu',
    'triage-untracked': 'igpu',
}

MAX_CHARS = 12000  # ~3k tokens, comfortably inside the 8192 context with room to answer


class LocalAIError(RuntimeError):
    """Raised when the local stack cannot be measured. Never caught to produce a default."""


# --------------------------------------------------------------------------- transport

def _url(device, path):
    return DEVICES[device]['endpoint'] + path


def _get(device, path, timeout=10):
    try:
        with urllib.request.urlopen(_url(device, path), timeout=timeout) as r:
            return json.load(r)
    except urllib.error.URLError as e:
        raise LocalAIError(
            'endpoint DOWN for device %r at %s%s (%s). '
            'Start it: `ollama serve` for gpu, or `python familiars/localai.py --serve-igpu` '
            'for the Intel adapter. Not falling back to another device.'
            % (device, DEVICES[device]['endpoint'], path, e))
    except OSError as e:
        raise LocalAIError('endpoint unreadable for device %r: %s' % (device, e))


def _post(device, path, payload, timeout=600):
    body = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(_url(device, path), data=body,
                                 headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise LocalAIError('device %r returned HTTP %s: %s'
                           % (device, e.code, e.read()[:400].decode('utf-8', 'replace')))
    except urllib.error.URLError as e:
        raise LocalAIError(
            'endpoint DOWN for device %r at %s (%s). Not falling back.'
            % (device, DEVICES[device]['endpoint'], e))


def generate(device, prompt, system=None, num_predict=320, temperature=0.0):
    """One completion. Returns the text and the metrics Ollama measured for it."""
    if device not in DEVICES:
        raise LocalAIError('unknown device %r; known: %s' % (device, ', '.join(DEVICES)))
    payload = {
        'model': DEVICES[device]['model'],
        'prompt': prompt,
        'stream': False,
        'keep_alive': '30m',
        'options': {'temperature': temperature, 'num_predict': num_predict},
    }
    if system:
        payload['system'] = system
    if DEVICES[device].get('thinking'):
        payload['think'] = False
    t0 = time.time()
    r = _post(device, '/api/generate', payload)
    wall = time.time() - t0
    ev, ed = r.get('eval_count') or 0, r.get('eval_duration') or 0
    pe, pd = r.get('prompt_eval_count') or 0, r.get('prompt_eval_duration') or 0
    text = (r.get('response') or '').strip()
    # An empty completion is a failure, not a blank cell. Left unguarded it prints as None in
    # a results table and reads as "nothing to report" - the cheerful default this file exists
    # to prevent. Say what was actually spent, so the cause is in the message.
    if not text:
        raise LocalAIError(
            'device %r returned an EMPTY completion (done_reason=%r, %d tokens generated, '
            '%d thinking chars). The token budget was spent without producing an answer; '
            'raise num_predict or disable thinking for this model.'
            % (device, r.get('done_reason'), ev, len(r.get('thinking') or '')))
    return {
        'device': device,
        'model': DEVICES[device]['model'],
        'text': text,
        'eval_tokens': ev,
        'eval_s': round(ed / 1e9, 3) if ed else 0.0,
        'tok_s': round(ev / (ed / 1e9), 1) if ed else None,
        'prompt_tokens': pe,
        'prefill_tok_s': round(pe / (pd / 1e9), 1) if pd else None,
        'load_s': round((r.get('load_duration') or 0) / 1e9, 3),
        'wall_s': round(wall, 2),
    }


# --------------------------------------------------------------------------- hardware

def nvidia_smi():
    """Free/used VRAM and utilisation straight from nvidia-smi. None if there is no card."""
    try:
        out = subprocess.run(
            ['nvidia-smi', '--query-gpu=name,memory.total,memory.used,memory.free,'
             'utilization.gpu,driver_version', '--format=csv,noheader,nounits'],
            capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0 or not out.stdout.strip():
        return None
    f = [p.strip() for p in out.stdout.strip().splitlines()[0].split(',')]
    if len(f) < 6:
        return None
    return {'name': f[0], 'total_mib': int(f[1]), 'used_mib': int(f[2]),
            'free_mib': int(f[3]), 'util_pct': int(f[4]), 'driver': f[5]}


def resident(device):
    """What /api/ps says is loaded, including how much of it actually sits in VRAM."""
    ps = _get(device, '/api/ps')
    rows = []
    for m in ps.get('models') or []:
        size, vram = m.get('size') or 0, m.get('size_vram') or 0
        rows.append({
            'name': m.get('name'),
            'size_gb': round(size / 1e9, 2),
            'vram_gb': round(vram / 1e9, 2),
            'offload_pct': round(100.0 * vram / size, 1) if size else 0.0,
            'context': m.get('context_length'),
            'quant': (m.get('details') or {}).get('quantization_level'),
        })
    return rows


# --------------------------------------------------------------------------- git / gh

def repo_path(name_or_path):
    """Resolve a repo name to its canonical checkout. Raises if it is not a git repo."""
    if os.path.isdir(os.path.join(name_or_path, '.git')) or os.path.isfile(
            os.path.join(name_or_path, '.git')):
        return os.path.abspath(name_or_path)
    cand = os.path.join(GITHUB, name_or_path)
    if os.path.exists(os.path.join(cand, '.git')):
        return cand
    raise LocalAIError('no git repo at %r (tried %r and %r)'
                       % (name_or_path, os.path.abspath(name_or_path), cand))


def git(cwd, *args, **kw):
    out = subprocess.run(['git'] + list(args), cwd=cwd, capture_output=True,
                         text=True, errors='replace', timeout=kw.get('timeout', 120))
    if out.returncode != 0 and not kw.get('allow_fail'):
        raise LocalAIError('git %s failed in %s: %s'
                           % (' '.join(args), cwd, (out.stderr or '').strip()[:400]))
    return out.stdout


def fetch_run_log(full_repo, run_id):
    """Pull a failing run's logs through scripts/gh-api.sh, which holds the credential."""
    if not os.path.exists(os.path.join(REPO_ROOT, 'scripts', 'gh-api.sh')):
        raise LocalAIError('scripts/gh-api.sh not found under %s' % REPO_ROOT)
    # Git Bash mangles a Windows path handed to it as an argument: C:\Users\...\gh-api.sh
    # arrived as "C:UsersvikraOneDrive..." with every backslash eaten, and bash reported
    # "No such file or directory". The script is invoked by a RELATIVE posix path with
    # cwd set instead, which needs no conversion and no MSYS_NO_PATHCONV.
    path = 'repos/%s/actions/runs/%s/logs' % (full_repo, run_id)
    out = subprocess.run(['bash', 'scripts/gh-api.sh', path, '--raw'], cwd=REPO_ROOT,
                         capture_output=True, timeout=180)
    if out.returncode != 0 or not out.stdout:
        raise LocalAIError('gh-api.sh could not fetch %s: %s'
                           % (path, (out.stderr or b'')[:300].decode('utf-8', 'replace')))
    try:
        zf = zipfile.ZipFile(io.BytesIO(out.stdout))
    except zipfile.BadZipFile:
        raise LocalAIError('run %s logs were not a zip; API said: %s'
                           % (run_id, out.stdout[:300].decode('utf-8', 'replace')))
    chunks = []
    for n in zf.namelist():
        if n.endswith('.txt'):
            chunks.append('===== %s =====\n%s' % (n, zf.read(n).decode('utf-8', 'replace')))
    if not chunks:
        raise LocalAIError('run %s logs contained no .txt entries' % run_id)
    return '\n'.join(chunks)


def _tail(text, limit=MAX_CHARS):
    """Logs fail at the end; diffs matter at the top. Callers pick which end to keep."""
    if len(text) <= limit:
        return text
    return '...[%d chars elided]...\n' % (len(text) - limit) + text[-limit:]


def _head(text, limit=MAX_CHARS):
    if len(text) <= limit:
        return text
    return text[:limit] + '\n...[%d chars elided]...' % (len(text) - limit)


# --------------------------------------------------------------------------- jobs

SYS_TERSE = ('You are a terse build engineer. Answer in plain text only. '
             'No preamble, no markdown headings, no bullet characters unless asked. '
             'If the evidence does not support a conclusion, say so plainly.')


def job_classify_ci_failure(target):
    """Name the failing step and the one-line cause of a failing Actions run."""
    m = re.match(r'^([\w.-]+/[\w.-]+)#(\d+)$', str(target).strip())
    if m:
        log, source = fetch_run_log(m.group(1), m.group(2)), '%s run %s' % (m.group(1), m.group(2))
    else:
        if not os.path.isfile(target):
            raise LocalAIError(
                'no such log file: %r. Give a path, or owner/repo#run_id to fetch it. '
                '(Run ids come from `python scripts/audit_estate.py --json out.json`.)' % target)
        with open(target, 'r', encoding='utf-8', errors='replace') as fh:
            log = fh.read()
        source = os.path.abspath(target)
    if not log.strip():
        raise LocalAIError('log %r is empty; nothing to classify' % source)

    prompt = (
        'Below is the log of a failing GitHub Actions job.\n\n'
        'Reply in exactly this shape, two lines:\n'
        'STEP: <the name of the step that failed>\n'
        'CAUSE: <one sentence, the actual cause, quoting the decisive error text>\n\n'
        'If the log does not show which step failed, write STEP: unknown and say why '
        'in CAUSE. Do not guess a plausible step name.\n\n'
        '--- LOG (%s) ---\n%s' % (source, _tail(log)))
    r = generate(JOB_DEVICE['classify-ci-failure'], prompt, system=SYS_TERSE, num_predict=200)
    r['source'] = source
    r['log_chars'] = len(log)
    return r


def job_summarise_commit(sha, repo=None):
    """Two lines describing what a commit did, read from its own diff."""
    path = repo_path(repo or REPO_ROOT)
    sha = str(sha).strip()
    resolved = git(path, 'rev-parse', '--verify', '%s^{commit}' % sha).strip()
    subject = git(path, 'log', '-1', '--format=%s', resolved).strip()
    stat = git(path, 'show', '--stat', '--format=', resolved)
    diff = git(path, 'show', '--format=', '--unified=2', resolved)
    if not diff.strip() and not stat.strip():
        raise LocalAIError('commit %s in %s has no diff to read' % (resolved[:12], path))

    prompt = (
        'Below is a git commit from the repository %r.\n\n'
        'Write exactly two lines:\n'
        'Line 1: what changed, concretely, naming the files or functions.\n'
        'Line 2: why it matters, or "effect unclear from the diff" if the diff does not say.\n'
        'Do not restate the commit subject verbatim. Do not speculate beyond the diff.\n\n'
        '--- SUBJECT ---\n%s\n\n--- STAT ---\n%s\n\n--- DIFF ---\n%s'
        % (os.path.basename(path), subject, _head(stat, 2000), _head(diff, MAX_CHARS)))
    r = generate(JOB_DEVICE['summarise-commit'], prompt, system=SYS_TERSE, num_predict=180)
    r['repo'] = path
    r['sha'] = resolved
    r['subject'] = subject
    return r


def job_triage_untracked(repo, device=None):
    """Describe every untracked file, so uncommitted work is never deleted unread.

    Device is worth choosing deliberately. Measured 2026-09-03 on cvaa's two untracked files,
    qwen3:0.6b on the Intel iGPU called a markdown vaccine note "a deterministic, non-viable
    repository" - fluent and wrong. The 4B on the discrete card reads the same file correctly.
    The iGPU earns its place on bulk triage when the discrete card is contended by another
    lane, not on accuracy.
    """
    dev = device or JOB_DEVICE['triage-untracked']
    path = repo_path(repo)
    porcelain = git(path, 'status', '--porcelain', '--untracked-files=all')
    files = [ln[3:].strip().strip('"') for ln in porcelain.splitlines() if ln.startswith('??')]
    if not files:
        return {'repo': path, 'untracked': 0, 'files': [],
                'note': 'no untracked files in %s' % path}

    results = []
    for rel in files:
        full = os.path.join(path, rel)
        try:
            size = os.path.getsize(full)
        except OSError as e:
            results.append({'file': rel, 'error': 'unreadable: %s' % e})
            continue
        if os.path.isdir(full):
            results.append({'file': rel, 'error': 'directory, not a file'})
            continue
        try:
            with open(full, 'r', encoding='utf-8', errors='replace') as fh:
                head = fh.read(2000)
        except OSError as e:
            results.append({'file': rel, 'error': 'unreadable: %s' % e})
            continue
        if '\x00' in head:
            results.append({'file': rel, 'bytes': size, 'verdict': 'binary file, not read'})
            continue
        prompt = (
            'An untracked file was found in the git repository %r. Say in ONE sentence what '
            'it appears to be and whether it looks like work worth keeping. Judge only from '
            'the content shown. If the content is too thin to tell, say so.\n\n'
            'FILENAME: %s  (%d bytes)\n--- FIRST BYTES ---\n%s'
            % (os.path.basename(path), rel, size, head))
        try:
            g = generate(dev, prompt, system=SYS_TERSE, num_predict=160)
        except LocalAIError as e:
            # One file failing must not silently vanish from the listing, and must not abort
            # the other files either. It is recorded against its own name.
            results.append({'file': rel, 'bytes': size, 'error': str(e)})
            continue
        results.append({'file': rel, 'bytes': size, 'verdict': g['text'],
                        'tok_s': g['tok_s'], 'device': g['device']})
    return {'repo': path, 'untracked': len(files), 'files': results}


# --------------------------------------------------------------------------- health

def health(devices=('gpu', 'igpu')):
    smi = nvidia_smi()
    report = {'measured_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
              'nvidia_smi': smi, 'devices': {}}
    failures = []
    for d in devices:
        try:
            ver = _get(d, '/api/version').get('version')
            rows = resident(d)
            probe = generate(d, 'Reply with the single word: ready.', num_predict=24)
            rows = resident(d) or rows
            report['devices'][d] = {
                'endpoint': DEVICES[d]['endpoint'],
                'adapter': DEVICES[d]['adapter'],
                'backend': DEVICES[d]['backend'],
                'ollama': ver,
                'model': DEVICES[d]['model'],
                'resident': rows,
                'tok_s': probe['tok_s'],
                'prefill_tok_s': probe['prefill_tok_s'],
                'load_s': probe['load_s'],
                'ok': True,
            }
        except LocalAIError as e:
            report['devices'][d] = {'endpoint': DEVICES[d]['endpoint'],
                                    'adapter': DEVICES[d]['adapter'],
                                    'ok': False, 'error': str(e)}
            failures.append(d)
    report['failed_devices'] = failures
    return report


def print_health(rep):
    smi = rep['nvidia_smi']
    print('measured %s' % rep['measured_utc'])
    if smi:
        print('nvidia-smi : %s  %d MiB total, %d used, %d free, util %d%%, driver %s'
              % (smi['name'], smi['total_mib'], smi['used_mib'], smi['free_mib'],
                 smi['util_pct'], smi['driver']))
    else:
        print('nvidia-smi : NOT AVAILABLE (no NVIDIA card, or driver not on PATH)')
    for d, v in rep['devices'].items():
        print('')
        print('[%s] %s via %s  -> %s' % (d, v['adapter'], v.get('backend', '?'), v['endpoint']))
        if not v['ok']:
            print('  STATUS   : DOWN')
            print('  ERROR    : %s' % v['error'])
            continue
        print('  ollama   : %s' % v['ollama'])
        print('  model    : %s' % v['model'])
        for m in v['resident']:
            print('  resident : %s  %.2f GB, %.2f GB in VRAM = %.1f%% offloaded, ctx %s, %s'
                  % (m['name'], m['size_gb'], m['vram_gb'], m['offload_pct'],
                     m['context'], m['quant']))
        if not v['resident']:
            print('  resident : nothing loaded right now')
        print('  measured : %s tok/s generate, %s tok/s prefill, %.3f s load'
              % (v['tok_s'], v['prefill_tok_s'], v['load_s']))


# --------------------------------------------------------------------------- bench

BENCH_PROMPT = ('Write a detailed technical explanation of how electricity transmission '
                'substations transform and switch high voltage power.')


def bench(devices=('gpu', 'igpu'), concurrency=2, num_predict=400):
    """Saturate the adapters and report what they actually sustained."""
    jobs = []
    for d in devices:
        _get(d, '/api/version')  # fail loudly before timing anything
        jobs.extend([d] * concurrency)

    samples = []
    stop = {'go': True}

    def sampler():
        while stop['go']:
            s = nvidia_smi()
            if s:
                samples.append((s['util_pct'], s['used_mib']))
            time.sleep(0.4)

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=len(jobs) + 1) as ex:
        ex.submit(sampler)
        futs = [(d, ex.submit(generate, d, BENCH_PROMPT, None, num_predict)) for d in jobs]
        out = []
        for d, f in futs:
            out.append(f.result())
        stop['go'] = False
    wall = time.time() - t0

    per = {}
    for r in out:
        per.setdefault(r['device'], []).append(r)
    result = {'wall_s': round(wall, 2), 'concurrency_per_device': concurrency, 'devices': {}}
    total_tokens = 0
    for d, rs in per.items():
        toks = sum(r['eval_tokens'] for r in rs)
        total_tokens += toks
        result['devices'][d] = {
            'adapter': DEVICES[d]['adapter'],
            'model': DEVICES[d]['model'],
            'requests': len(rs),
            'tokens': toks,
            'per_request_tok_s': [r['tok_s'] for r in rs],
            'aggregate_tok_s': round(toks / wall, 1),
        }
    result['total_tokens'] = total_tokens
    result['aggregate_tok_s_all_devices'] = round(total_tokens / wall, 1)
    if samples:
        result['nvidia_util_pct_peak'] = max(s[0] for s in samples)
        result['nvidia_util_pct_mean'] = round(sum(s[0] for s in samples) / len(samples), 1)
        result['nvidia_used_mib_peak'] = max(s[1] for s in samples)
        result['nvidia_samples'] = len(samples)
    return result


def print_bench(b):
    print('bench: %d requests, %.2f s wall' % (
        sum(v['requests'] for v in b['devices'].values()), b['wall_s']))
    for d, v in b['devices'].items():
        print('  [%s] %-36s %d req, %d tok, per-request %s tok/s, aggregate %s tok/s'
              % (d, v['adapter'], v['requests'], v['tokens'],
                 v['per_request_tok_s'], v['aggregate_tok_s']))
    print('  TOTAL across adapters: %s tok/s (%d tokens in %.2f s)'
          % (b['aggregate_tok_s_all_devices'], b['total_tokens'], b['wall_s']))
    if 'nvidia_util_pct_peak' in b:
        print('  nvidia-smi during run: peak %d%% util, mean %s%%, peak %d MiB used, %d samples'
              % (b['nvidia_util_pct_peak'], b['nvidia_util_pct_mean'],
                 b['nvidia_used_mib_peak'], b['nvidia_samples']))


# --------------------------------------------------------------------------- serve

def serve_igpu():
    """Start an Ollama pinned to the Intel adapter. Ollama drops iGPUs unless told twice:
    OLLAMA_IGPU_ENABLE=1 admits it, GGML_VK_VISIBLE_DEVICES=1 hides the NVIDIA card from
    the Vulkan backend, and CUDA_VISIBLE_DEVICES=-1 stops it being picked up as CUDA."""
    if not os.path.exists(OLLAMA_EXE):
        raise LocalAIError('ollama.exe not found at %s' % OLLAMA_EXE)
    env = dict(os.environ)
    env.update({'OLLAMA_HOST': '127.0.0.1:11435', 'CUDA_VISIBLE_DEVICES': '-1',
                'GGML_VK_VISIBLE_DEVICES': '1', 'OLLAMA_IGPU_ENABLE': '1',
                'OLLAMA_KEEP_ALIVE': '30m'})
    subprocess.Popen([OLLAMA_EXE, 'serve'], env=env,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(15):
        time.sleep(2)
        try:
            v = _get('igpu', '/api/version', timeout=3)
            return 'igpu server up on %s, ollama %s' % (DEVICES['igpu']['endpoint'],
                                                        v.get('version'))
        except LocalAIError:
            continue
    raise LocalAIError('igpu server did not answer on %s within 30 s'
                       % DEVICES['igpu']['endpoint'])


# --------------------------------------------------------------------------- cli

def main():
    ap = argparse.ArgumentParser(
        description='Local inference on this machine, and the clerical jobs it does.')
    ap.add_argument('--health', action='store_true',
                    help='report model, backend, offload and measured tokens/s; '
                         'exits 2 if any endpoint is down')
    ap.add_argument('--bench', action='store_true', help='saturate the adapters, report throughput')
    ap.add_argument('--serve-igpu', action='store_true', help='start the Intel-pinned server')
    ap.add_argument('--job', choices=sorted(JOB_DEVICE), help='run one clerical job')
    ap.add_argument('--input', help='the job subject: log path or owner/repo#run_id, '
                                    'a commit sha, or a repo name')
    ap.add_argument('--repo', help='repo for summarise-commit (name under GitHub/ or a path)')
    ap.add_argument('--device', choices=sorted(DEVICES) + ['both'], default='both',
                    help='which adapter to use for --health/--bench')
    ap.add_argument('--concurrency', type=int, default=2, help='--bench requests per device')
    ap.add_argument('--json', action='store_true', help='machine-readable output')
    args = ap.parse_args()

    devices = tuple(DEVICES) if args.device == 'both' else (args.device,)

    if not (args.health or args.bench or args.serve_igpu or args.job):
        ap.error('nothing to do: pass --health, --bench, --serve-igpu or --job')

    try:
        if args.serve_igpu:
            print(serve_igpu())

        if args.health:
            rep = health(devices)
            print(json.dumps(rep, indent=2)) if args.json else print_health(rep)
            if rep['failed_devices']:
                sys.stderr.write('\nFAIL: endpoint down for: %s\n'
                                 % ', '.join(rep['failed_devices']))
                return 2

        if args.bench:
            b = bench(devices, concurrency=args.concurrency)
            print(json.dumps(b, indent=2)) if args.json else print_bench(b)

        if args.job:
            if not args.input:
                ap.error('--job %s needs --input' % args.job)
            if args.job == 'classify-ci-failure':
                r = job_classify_ci_failure(args.input)
            elif args.job == 'summarise-commit':
                r = job_summarise_commit(args.input, args.repo)
            else:
                # --device is an explicit override; without it the job keeps its routing.
                r = job_triage_untracked(
                    args.input, None if args.device == 'both' else args.device)
            if args.json:
                print(json.dumps(r, indent=2))
            elif args.job == 'triage-untracked':
                print('%s: %d untracked' % (r['repo'], r['untracked']))
                for f in r.get('files', []):
                    print('  %-52s %s' % (f['file'], f.get('verdict') or f.get('error')))
                if not r.get('files'):
                    print('  %s' % r.get('note', ''))
            else:
                print(r['text'])
                print('\n[%s on %s: %s tok/s, %d tokens]'
                      % (r['model'], DEVICES[r['device']]['adapter'],
                         r['tok_s'], r['eval_tokens']))
    except LocalAIError as e:
        sys.stderr.write('FAIL: %s\n' % e)
        return 2
    return 0


if __name__ == '__main__':
    # The model may emit any Unicode it likes, emoji included. Windows stdout defaults
    # to cp1252 and raises UnicodeEncodeError on the first one, throwing away an answer
    # that was already computed correctly. Fail on the work, never on the printing.
    for _s in (sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass

    sys.exit(main())
