"""triage.py - read every red run in the estate with the local models, and ground every answer.

WHY THIS EXISTS

The estate carries 40-odd red workflow runs at any moment, spread over 35 repositories, and
nobody reads them. audit_estate.py names WHICH runs are red and which job and step failed -
that is the API's own record and it is authoritative - but it cannot say WHY, because why is
in the log, and the logs are 50 kB each. Forty of those is two hours of human reading for a
question that gets asked every session.

The card was idle while that was true. Measured 2026-09-03 23:40: 10-20% GPU utilisation,
a 4B model resident in 3.95 GB of VRAM answering one question every few minutes. A model that
holds memory and answers nothing is worse than no model, because it costs the memory anyway.

So this is a work pump. It enumerates the reds, fetches every failing job's log, and fans them
across BOTH adapters with several requests in flight, so the cards are loaded rather than
idling between prompts. It writes logs/red-board.md: one line per red, grouped by cause, which
a human reads in thirty seconds.

THE THING THAT MAKES IT USABLE - GROUNDING

A model's paraphrase of a log is not evidence. Another lane measured this model at 98.3%
precision, and the one invention it made was a ONE-CHARACTER MUTATION of a real log line -
a sentence that reads exactly like the log and never appeared in it. No human reviewer catches
that, so it is prevented structurally rather than reviewed for:

  1. The model is never asked for facts we already hold. repo, workflow, run id, job name and
     FAILING STEP all come from the GitHub API through audit_estate.py. The model produces
     three things only: a class, a verbatim quote, and one sentence.
  2. The class must be one of seven strings. Anything else is coerced to `unknown` and counted.
  3. The quote must be a SUBSTRING of the excerpt the model was shown - character for
     character, after normalising whitespace and stripping ANSI and runner timestamps, which
     are layout, not content. Case is significant. A one-character mutation fails this test.
     A quote shorter than MIN_QUOTE characters fails it too, because "error" is in every log
     and grounds nothing.
  4. A row that fails the check is not repaired and not deleted. It is published as UNGROUNDED
     with the model's rejected claim shown as a claim, next to the log's own first error line,
     which is quoted deterministically by this file and not by any model.

An ungrounded row is a measurement, not a failure of the run.

DISCIPLINES CARRIED FROM CLAUDE.md

  - A missing input must FAIL, never skip. A log that will not fetch becomes a FETCH-FAILED row
    and the process exits non-zero; it never silently shrinks the denominator.
  - A red whose API record names no failing job (a startup_failure, usually) is its own row,
    NO-FAILING-JOB, and is never dropped just because there is nothing to read.
  - Report measurements, never grades. This file says "9 of 40 are missing-secret"; it never
    says the estate is healthy.
  - The tail of a runner log is post-job cleanup and a Node deprecation warning. Reading it as
    the cause was a measured mistake. The excerpt is built around the ##[error] lines instead,
    by localai.focus_errors.

USAGE

    python familiars/triage.py                       # full estate sweep -> logs/red-board.md
    python familiars/triage.py --limit 6             # a short sweep while developing
    python familiars/triage.py --calibrate-conc      # measure where concurrency stops paying
    python familiars/triage.py --calibrate-lines     # measure how much log the model needs
    python familiars/triage.py --loop 900            # run as a pump, one sweep every 15 min

Exit code is 0 only when every red the audit named produced a row and every input was read.
"""

import argparse
import json
import os
import queue
import re
import statistics
import subprocess
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import localai as L  # noqa: E402  - sibling module, same directory

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS = os.path.join(REPO_ROOT, 'logs')
CACHE = os.path.join(LOGS, 'triage-cache')
BOARD_MD = os.path.join(LOGS, 'red-board.md')
BOARD_JSON = os.path.join(LOGS, 'red-board.json')
ESTATE_JSON = os.path.join(LOGS, 'triage-estate.json')
OWNER = 'Ventusltd'

# The whole vocabulary. Seven strings, closed set. A model answer outside it is `unknown`,
# counted as a coercion, and never invented into a new category - a taxonomy that grows by
# one entry per run is not a taxonomy.
CLASSES = [
    'missing-secret',          # a credential, token or repository secret is absent or empty
    'contract-drift',          # a gate compared two things that were meant to be identical
    'nondeterministic-input',  # an upstream source moved: an API, a download, a live page
    'dead-route',              # a URL, path or artefact the job expected does not exist
    'timeout',                 # the job or a step ran out of time or was cancelled
    'by-design-refusal',       # a gate deliberately failed closed; the failure IS the product
    'unknown',                 # the log does not say
]
CLASS_HELP = {
    'missing-secret': 'a credential, token, or repository secret is absent, empty or unauthorised',
    'contract-drift': 'two things a gate required to be identical were not (bytes, digests, counts, pointers)',
    'nondeterministic-input': 'an upstream input moved under the job: an API response, a download, a live page',
    'dead-route': 'a URL, file path or artefact the job expected does not exist (404, No such file)',
    'timeout': 'the job or step exceeded its time limit, or was cancelled for running too long',
    'by-design-refusal': 'a gate refused on purpose and said so; the red is the gate working',
    'unknown': 'the log does not contain enough to say',
}

MIN_QUOTE = 24    # characters, normalised. Shorter than this grounds nothing.

# EXCERPT SIZE, MEASURED - `--calibrate-lines`, 6 real job logs (median 25,639 chars raw),
# qwen3:4b on the dGPU, 2026-09-04:
#
#     lines   prompt tokens   grounded   classes agreed with 160?
#        20             937        5/6   no  - one log read as by-design-refusal, not dead-route
#        40           1,586        6/6   YES - identical distribution
#        80           2,223        5/6   YES
#       160           3,766        6/6   YES
#       320           4,326        4/6   CUDA error: out of memory on a shared 8 GB card
#
# 40 lines is where the answers stop changing. Everything above it costs prefill on every
# request and buys no different answer; 320 costs the card itself. 20 is too few - the
# decisive line falls outside the window and the class flips. So the default is the smallest
# size that agreed, not the largest that fitted.
DEFAULT_LINES = 40

# CONCURRENCY, MEASURED - `--calibrate-conc`, 12 requests per rung, 2026-09-04:
#
#     dGPU   1 -> 63 tok/s aggregate | 2 -> 107 | 3 -> 107   (stops paying at 2)
#     iGPU   1 ->  5 tok/s aggregate | 2 ->  12 | 3 ->  12   (stops paying at 2)
#
# Both servers saturate at two requests in flight, which is Ollama's auto-chosen parallel
# slot count on this box (OLLAMA_NUM_PARALLEL is unset; OLLAMA_CONTEXT_LENGTH=8192 is not).
# Past two, requests queue in the HTTP server and aggregate throughput is flat while latency
# per answer grows. Raising OLLAMA_NUM_PARALLEL is the lever, and it belongs to whoever owns
# those servers, not to this file.
# THE MEASUREMENT ABOVE IS NOT THE POLICY. From 2026-09-04 the discrete card is committed to
# familiars/autopilot.py for an eight-hour overnight run, which is SERIAL by design, and
# localai.py now carries a governor that enforces one cross-process dGPU request at a time and
# refuses the iGPU outright. Two clients against one serial endpoint do not double throughput;
# they queue and double the resident pressure while queuing. So the shipped default is one
# request in flight and no iGPU, and the calibration above records what the hardware WOULD
# give if the card were free - which is the number to re-read when the autopilot ends.
DEFAULT_GPU_SLOTS = 1
DEFAULT_IGPU_SLOTS = 0

_ANSI = re.compile(r'\x1b\[[0-9;]*[A-Za-z]')
_TS = re.compile(r'^\s*\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d+Z ?', re.M)
_WS = re.compile(r'\s+')


# --------------------------------------------------------------------------- normalising

def strip_noise(text):
    """Runner timestamps and ANSI colour are layout, not content. Removing them before the
    model sees the log saves roughly a fifth of the prompt tokens, and - more importantly -
    means the string the model can copy is the same string this file will search. The
    grounding check and the prompt must share one normalisation or the check is theatre."""
    return _TS.sub('', _ANSI.sub('', text.replace('\r', '')))


def flatten(text):
    """Whitespace-insensitive, character-sensitive. Used only for the substring test."""
    return _WS.sub(' ', text).strip()


# --------------------------------------------------------------------------- enumeration

def reds_from_estate(estate):
    """Every failing JOB in the estate, newest first. One row per job, not per run: a run with
    three failing jobs is three separate things broken and gets three lines.

    A red carrying no failing job is kept as a row with job_id None. That is a real state -
    a startup_failure, or a run cancelled before any job started - and dropping it would make
    the board disagree with audit_estate.py's own count."""
    rows = []
    for repo in estate.get('ci') or []:
        for red in repo.get('reds') or []:
            jobs = red.get('failed_jobs') or []
            if not jobs:
                rows.append(_row(repo, red, None))
                continue
            for j in jobs:
                rows.append(_row(repo, red, j))
    rows.sort(key=lambda r: r['at'] or '', reverse=True)
    return rows


def _row(repo, red, job):
    job_id = None
    if job and job.get('url'):
        m = re.search(r'/job/(\d+)', job['url'])
        if m:
            job_id = m.group(1)
    steps = (job or {}).get('steps') or []
    return {
        'repo': repo['repo'],
        'full_repo': '%s/%s' % (OWNER, repo['repo']),
        'workflow': red.get('workflow'),
        'run_id': red.get('run_id'),
        'sha': red.get('sha'),
        'at': red.get('at'),
        'at_head': bool(red.get('at_head')),
        'job': (job or {}).get('name') or (job or {}).get('job'),
        'job_id': job_id,
        # The failing step is the API's, never the model's. One less surface to invent on.
        'failing_step': '; '.join(steps) if steps else None,
    }


# --------------------------------------------------------------------------- log transport

def cached_log(row, refresh=False):
    """Fetch a job log, once. A completed job's log is immutable, so it is cached by job id and
    every later calibration pass is free. Raises rather than returning empty: a missing input
    must FAIL."""
    if not row['job_id']:
        raise L.LocalAIError('the API recorded no failing job for %s run %s'
                             % (row['repo'], row['run_id']))
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, '%s-%s.log' % (row['repo'], row['job_id']))
    if not refresh and os.path.exists(path) and os.path.getsize(path) > 0:
        with open(path, 'r', encoding='utf-8', errors='replace') as fh:
            return fh.read()
    text = L.fetch_job_log(row['full_repo'], row['job_id'])
    if not text.strip():
        raise L.LocalAIError('job %s log was empty' % row['job_id'])
    with open(path, 'w', encoding='utf-8', errors='replace', newline='') as fh:
        fh.write(text)
    return text


def excerpt(log, keep_lines=DEFAULT_LINES):
    """The lines around the failure, normalised. Never the tail: the tail of a runner log is
    'Post job cleanup' and a Node 20 deprecation warning, and a classifier fed the tail
    reported the warning as the cause. Measured, on gridatlas run 33800308935."""
    clean = strip_noise(log)
    focused = L.focus_errors(clean, keep_lines=keep_lines)
    used_focus = focused is not None
    body = focused if used_focus else clean
    lines = body.splitlines()
    if len(lines) > keep_lines:
        body = ('... [%d earlier lines omitted] ...\n' % (len(lines) - keep_lines)
                + '\n'.join(lines[-keep_lines:]))
    return body, used_focus


def first_error_line(log):
    """The log's own decisive line, quoted by this file and not by any model. Shown next to
    an UNGROUNDED row so a human still has one true thing to read."""
    for ln in strip_noise(log).splitlines():
        s = ln.strip()
        if s.startswith('##[error]'):
            return s[9:].strip()[:400]
    for ln in strip_noise(log).splitlines():
        s = ln.strip()
        if 'Process completed with exit code' in s:
            return s[:400]
    return None


# --------------------------------------------------------------------------- the model call

SYSTEM = ('You are a build engineer reading one failing CI job log. You answer only in the '
          'three labelled lines you are asked for. You never write markdown, headings, bold '
          'or bullets. You never guess: if the log does not say, the class is unknown.')


def build_prompt(row, body, strict=False):
    vocab = '\n'.join('  %-24s %s' % (c, CLASS_HELP[c]) for c in CLASSES)
    extra = ''
    if strict:
        extra = ('\nYOUR PREVIOUS ANSWER WAS REJECTED: the QUOTE you gave does not appear in '
                 'the log. Do not summarise, do not retype from memory, do not fix spelling. '
                 'Find one line in the log above and COPY IT CHARACTER FOR CHARACTER.\n')
    return (
        'Below is the log of a FAILING GitHub Actions job, reduced to the lines around its '
        'errors.\n\n'
        'Repository: %s\nWorkflow: %s\nFailing job: %s\nFailing step (from the API, already '
        'known - do not repeat it): %s\n\n'
        '--- LOG ---\n%s\n--- END LOG ---\n%s\n'
        'Reply with exactly three lines, in this order, and nothing else:\n\n'
        'CLASS: <one word from the list below, exactly as spelled>\n'
        'QUOTE: <one line copied VERBATIM from the log above, at least %d characters, the '
        'line that shows the failure>\n'
        'CAUSE: <one sentence, under 25 words, saying what that quoted line means>\n\n'
        'The class vocabulary, and nothing outside it:\n%s\n\n'
        'Rules. The QUOTE must be text that is actually present in the log above - it will be '
        'checked by exact string search and your answer is discarded if it is not found, so '
        'copy, never paraphrase. A deprecation warning is not a failure. "Process completed '
        'with exit code 1" is true of every red and explains nothing - quote the line that '
        'says WHY. Do not name the failing step; it is already known.\n\n'
        '--- ANSWER ---\nCLASS:'
        % (row['repo'], row['workflow'], row['job'], row['failing_step'] or 'not recorded',
           body, extra, MIN_QUOTE, vocab))


_FIELD = re.compile(r'^(CLASS|QUOTE|CAUSE)\s*:\s*(.*)$')


def parse_answer(text):
    """Three labelled lines out of whatever the model actually produced."""
    if not text.startswith('CLASS:'):
        text = 'CLASS:' + text
    out = {}
    current = None
    for ln in text.splitlines():
        m = _FIELD.match(ln.strip())
        if m:
            current = m.group(1)
            out[current] = m.group(2).strip()
        elif current == 'CAUSE' and ln.strip():
            out['CAUSE'] = (out.get('CAUSE', '') + ' ' + ln.strip()).strip()
    return out


def ground(quote, body):
    """The whole point of the file. Returns (ok, reason).

    Character-for-character containment after whitespace flattening. Not fuzzy, not
    case-insensitive, not token-overlap - every one of those readmits the one-character
    mutation this check exists to catch."""
    if not quote:
        return False, 'model produced no QUOTE line'
    q = quote.strip().strip('`"\u201c\u201d\'')
    q = flatten(strip_noise(q))
    if len(q) < MIN_QUOTE:
        return False, 'quote is %d chars, under the %d-char floor' % (len(q), MIN_QUOTE)
    if 'lines omitted' in q:
        return False, 'quote is this script\'s own elision marker, not log content'
    if q not in flatten(body):
        return False, 'quote is NOT a substring of the log excerpt'
    return True, 'verbatim substring of the excerpt'


ENDPOINT_RETRIES = [0]
_retry_lock = threading.Lock()

# --------------------------------------------------------------------- context budgeting
#
# Ollama's /api/generate does NOT error on an over-length prompt. It cuts it and answers
# from what is left, and the response looks exactly like a good one. That is the worst
# possible failure here, because the GROUNDING CHECK CANNOT SEE IT: the model quotes a line
# that really is in the part it was shown, the substring test passes, and the row is
# published as evidence-backed while the model never saw the half of the log that mattered.
#
# Measured 2026-09-04 on this box: the two endpoints do not have the same window.
#     11434  qwen3:4b   context_length 8192
#     11435  qwen3:0.6b context_length 4096
# and a 160-line excerpt builds a prompt of ~3,800 tokens median, 4,100 at the top of the
# range - which fits the dGPU and silently overflows the iGPU. The excerpt size that is
# right for one card is a truncation bug on the other.
#
# So the window is read from the server, per device, and the excerpt is fitted to it BEFORE
# the request goes out. Nothing is sent that does not fit. num_ctx is deliberately not
# overridden per request: localai.py records that doing so forces a full model reload and
# evicts the resident weights other lanes are using, so the excerpt bends and the server
# does not.

CHARS_PER_TOKEN = 2.9   # measured below the true ratio on purpose: it must never over-fit.
CTX_RESERVE = 192       # room for the system prompt and the chat scaffold Ollama adds.
_CTX = {}
_ctx_lock = threading.Lock()


def device_context(device):
    """The context window of the model actually loaded on that endpoint, from /api/ps.

    Not a constant in this file: the two servers are configured separately and one of them
    is restarted by other lanes. A hard-coded 8192 here would be a guess about somebody
    else's process."""
    with _ctx_lock:
        if device in _CTX:
            return _CTX[device]
    want = L.DEVICES[device]['model']
    for attempt in (0, 1):
        d = L._get(device, '/api/ps')
        for m in d.get('models') or []:
            if m.get('name') == want and m.get('context_length'):
                with _ctx_lock:
                    _CTX[device] = int(m['context_length'])
                return _CTX[device]
        if attempt == 0:
            # Not resident yet. Load it with the smallest possible request, then re-read.
            L.generate(device, 'hi', num_predict=1)
    raise L.LocalAIError(
        'device %r will not report a context window for %s via /api/ps. Refusing to send a '
        'prompt whose length cannot be checked - an over-length prompt is truncated silently '
        'by /api/generate and the answer would look exactly like a good one.' % (device, want))


def fit_excerpt(log, device, keep_lines, num_predict):
    """Shrink the excerpt until the prompt provably fits the device's window.

    Returns (body, lines_used, est_tokens, budget). Halving rather than trimming a line at a
    time because the excerpt is built around error clusters and losing whole clusters is more
    honest than losing the end of one. If even the smallest excerpt will not fit, this raises:
    a prompt that does not fit is a missing input, and a missing input must FAIL."""
    budget = device_context(device) - num_predict - CTX_RESERVE
    keep = keep_lines
    while True:
        body, _ = excerpt(log, keep)
        est = len(body) / CHARS_PER_TOKEN
        # The excerpt is the only part that varies; the scaffold is ~700 chars.
        if est + 260 <= budget or keep <= 10:
            break
        keep = max(10, keep // 2)
    if est + 260 > budget:
        raise L.LocalAIError(
            'even a %d-line excerpt estimates %d tokens against a %d-token budget on device '
            '%r (context %d). Not sending it: /api/generate would truncate it silently.'
            % (keep, est, budget, device, device_context(device)))
    return body, keep, int(est), budget


def generate_retrying(device, prompt, tries=4, backoff=2.0, **kw):
    """Ollama gets restarted under this process. Measured 2026-09-03 23:51: the server on
    11434 changed pid mid-sweep and three requests came back WinError 10061 - connection
    refused, not a dead endpoint. A sweep that loses a row to a two-second restart is a
    worse instrument than one that waits.

    This retries the SAME device only. It is not a fallback: a request is never quietly
    answered by a different model than the one it was routed to, because that would make
    the per-device precision numbers meaningless. Every retry is counted and reported."""
    last = None
    for i in range(tries):
        try:
            return L.generate(device, prompt, **kw)
        except (L.LocalAIError, OSError) as e:
            # WinError 10054 (connection reset) arrives as a bare ConnectionResetError, not a
            # URLError, so localai's transport does not wrap it: urlopen returns and the SOCKET
            # dies while the response body is being read. Measured at concurrency 6 on 11434,
            # six of six requests at once, 0.3 s in. It is the same transient class as 10061.
            last = e
            transient = ('endpoint DOWN', 'EMPTY completion', 'out of memory')
            if isinstance(e, L.LocalAIError) and not any(t in str(e) for t in transient):
                raise
            # "CUDA error: out of memory" arrives as an HTTP 500 and IS worth waiting out:
            # this card is shared, and the memory that was missing belongs to a request that
            # is about to finish. Measured at 320-line excerpts, concurrency 2. It is not
            # worth waiting out forever, which is what `tries` is for.
            if 'out of memory' in str(e):
                time.sleep(backoff * 2 * (i + 1))
                continue
            with _retry_lock:
                ENDPOINT_RETRIES[0] += 1
            if i < tries - 1:
                time.sleep(backoff * (i + 1))
    raise last


def classify(row, body, device, strict=False, num_predict=200):
    prompt = build_prompt(row, body, strict=strict)
    ctx = device_context(device)
    est = len(prompt) / CHARS_PER_TOKEN
    if est > ctx - num_predict:
        # Backstop. fit_excerpt should have made this unreachable; if it fires, the estimate
        # is wrong rather than the prompt being acceptable, so it fails rather than sends.
        raise L.LocalAIError('prompt estimates %d tokens against a %d-token window on %r; '
                             'refusing to let the transport truncate it' % (est, ctx, device))
    r = generate_retrying(device, prompt, system=SYSTEM, num_predict=num_predict,
                          stop=['\n\n', '--- LOG', '--- END'])
    # Post-flight, against the server's OWN count of what it evaluated. The estimate above is
    # a guess about tokenisation; this is the measurement. If the server evaluated a prompt
    # that fills the window, the input was cut and the answer is about an unknown fraction of
    # the log - which the grounding check cannot detect, because the quote is real.
    if r['prompt_tokens'] and r['prompt_tokens'] >= ctx - 8:
        raise L.LocalAIError(
            'TRUNCATED: %r evaluated %d prompt tokens into a %d-token window, so the log was '
            'cut before the model read it. The answer is discarded rather than published: a '
            'grounded quote from a truncated prompt is still an answer about half a log.'
            % (device, r['prompt_tokens'], ctx))
    fields = parse_answer(r['text'])
    cls = (fields.get('CLASS') or '').strip().strip('.`').lower()
    coerced = cls not in CLASSES
    ok, why = ground(fields.get('QUOTE'), body)
    return {
        'class': cls if not coerced else 'unknown',
        'class_coerced_from': cls if coerced else None,
        'quote': (fields.get('QUOTE') or '').strip(),
        'cause': (fields.get('CAUSE') or '').strip(),
        'grounded': ok,
        'ground_reason': why,
        'device': device,
        'model': r['model'],
        'tok_s': r['tok_s'],
        'eval_tokens': r['eval_tokens'],
        'prompt_tokens': r['prompt_tokens'],
        'wall_s': r['wall_s'],
        'ctx': ctx,
        'raw': r['text'],
    }


# --------------------------------------------------------------------------- GPU sampling

class Sampler(threading.Thread):
    """nvidia-smi, sampled once a second FOR THE DURATION OF THE RUN. Utilisation read before
    or after a run is a reading of an idle card and says nothing about the work."""

    CMD = ['nvidia-smi', '--query-gpu=utilization.gpu,memory.used',
           '--format=csv,noheader,nounits', '-l', '1']

    def __init__(self):
        threading.Thread.__init__(self, daemon=True)
        self.samples = []
        self.proc = None
        self.error = None

    def run(self):
        try:
            self.proc = subprocess.Popen(self.CMD, stdout=subprocess.PIPE,
                                         stderr=subprocess.DEVNULL, text=True,
                                         stdin=subprocess.DEVNULL)
        except OSError as e:
            self.error = 'nvidia-smi not runnable: %s' % e
            return
        for line in self.proc.stdout:
            parts = [p.strip() for p in line.split(',')]
            if len(parts) == 2 and parts[0].isdigit():
                self.samples.append((int(parts[0]), int(parts[1])))

    def stop(self):
        if self.proc and self.proc.poll() is None:
            try:
                self.proc.terminate()
            except OSError:
                pass
        self.join(timeout=3)

    def report(self):
        if self.error:
            return {'error': self.error, 'n': 0}
        if not self.samples:
            return {'error': 'no samples read from nvidia-smi', 'n': 0}
        util = [s[0] for s in self.samples]
        mem = [s[1] for s in self.samples]
        busy = [u for u in util if u >= 50]
        return {
            'n': len(util),
            'command': ' '.join(self.CMD),
            'util_min': min(util), 'util_med': int(statistics.median(util)),
            'util_max': max(util), 'util_mean': round(statistics.mean(util), 1),
            'pct_samples_over_50': round(100.0 * len(busy) / len(util), 1),
            'mem_min_mib': min(mem), 'mem_max_mib': max(mem),
        }


def vram_free_mib():
    try:
        r = subprocess.run(['nvidia-smi', '--query-gpu=memory.free',
                            '--format=csv,noheader,nounits'],
                           capture_output=True, text=True, timeout=10)
        return int(r.stdout.strip().splitlines()[0])
    except (OSError, ValueError, IndexError, subprocess.SubprocessError):
        return None


# --------------------------------------------------------------------------- the pump

def pump(rows, slots, keep_lines=DEFAULT_LINES, refresh=False, progress=True):
    """Fetch every log, then fan the classifications across the device slots.

    `slots` is a list of device names, one entry per request permitted in flight - so
    ['gpu','gpu','gpu','igpu','igpu'] is three concurrent on the dGPU and two on the Intel
    adapter. The list IS the concurrency; there is no separate knob to disagree with it.

    Fetching is done first and in parallel, because a log fetch is 1.3 s of network on which
    the GPU would otherwise sit idle. Once fetching is done the queue never starves."""
    results = [None] * len(rows)
    logs = [None] * len(rows)
    fetch_errors = 0

    t_fetch = time.time()
    fq = queue.Queue()
    for i, row in enumerate(rows):
        fq.put((i, row))
    lock = threading.Lock()

    def fetcher():
        nonlocal fetch_errors
        while True:
            try:
                i, row = fq.get_nowait()
            except queue.Empty:
                return
            try:
                logs[i] = cached_log(row, refresh=refresh)
            except Exception as e:                      # noqa: BLE001 - recorded, never hidden
                with lock:
                    fetch_errors += 1
                results[i] = _failed_row(row, e)
            finally:
                fq.task_done()

    fetchers = [threading.Thread(target=fetcher, daemon=True) for _ in range(8)]
    for t in fetchers:
        t.start()
    for t in fetchers:
        t.join()
    fetch_s = time.time() - t_fetch

    work = queue.Queue()
    for i, row in enumerate(rows):
        if logs[i] is not None:
            work.put(i)
    todo = work.qsize()
    done = [0]
    t_model = time.time()

    def worker(device):
        while True:
            try:
                i = work.get_nowait()
            except queue.Empty:
                return
            row, log = rows[i], logs[i]
            rec = dict(row)
            rec['log_chars'] = len(log)
            rec['first_error_line'] = first_error_line(log)
            rec['attempts'] = 0
            try:
                # Fitted to THIS device's window, not to a constant. The iGPU's 4096-token
                # window takes a smaller excerpt than the dGPU's 8192, and the row records
                # which it got, so two rows classified by different cards are never compared
                # as though they saw the same evidence.
                body, used_lines, est, budget = fit_excerpt(log, device, keep_lines, 200)
                rec['excerpt_chars'] = len(body)
                rec['excerpt_lines'] = used_lines
                rec['est_prompt_tokens'] = est
                rec['ctx_budget'] = budget
                a = classify(row, body, device)
                rec['attempts'] = 1

                # Two reasons to go again on the dGPU, and they are different failures.
                #
                # UNGROUNDED - the quote was not in the log. Retried with the rejection quoted
                # back and a stricter instruction to copy rather than recall.
                #
                # UNKNOWN FROM THE SMALL MODEL - measured over a full estate sweep on
                # 2026-09-04, ALL EIGHT answers the 0.6B produced were classed `unknown`,
                # while all eight of its quotes were verbatim. The small model can copy the
                # decisive line and cannot say what it means. Publishing its `unknown` would
                # make the board's class distribution a fact about which card happened to
                # pick the row up, not about the estate. So its quote is kept and the reading
                # is escalated. This is not a fallback for a broken endpoint - it is routing
                # a job to the model that was measured able to do it.
                why_again = None
                if not a['grounded']:
                    why_again = 'ungrounded'
                    rec['rejected_first'] = {'device': a['device'], 'quote': a['quote'],
                                             'cause': a['cause'], 'why': a['ground_reason']}
                elif a['class'] == 'unknown' and device != 'gpu':
                    why_again = 'unknown-from-small-model'
                    rec['first_pass'] = {'device': a['device'], 'class': a['class'],
                                         'quote': a['quote'], 'cause': a['cause']}
                if why_again:
                    # Refitted, because the dGPU's window is twice the iGPU's - reusing the
                    # iGPU-sized body would hand the big card half the evidence.
                    body2, used2, est2, _ = fit_excerpt(log, 'gpu', keep_lines, 200)
                    b = classify(row, body2, 'gpu', strict=(why_again == 'ungrounded'))
                    rec['attempts'] = 2
                    rec['escalated'] = why_again
                    better = b['grounded'] and (why_again == 'ungrounded'
                                                or b['class'] != 'unknown')
                    if better:
                        a, body = b, body2
                        rec['excerpt_chars'], rec['excerpt_lines'] = len(body2), used2
                        rec['est_prompt_tokens'] = est2
                rec.update(a)
                rec['state'] = 'ok' if a['grounded'] else 'UNGROUNDED'
            except Exception as e:                      # noqa: BLE001
                rec['state'] = 'MODEL-ERROR'
                rec['class'] = 'unknown'
                rec['grounded'] = False
                rec['cause'] = str(e)[:300]
                rec['device'] = device
            results[i] = rec
            with lock:
                done[0] += 1
                if progress:
                    sys.stderr.write('\r  classified %d/%d' % (done[0], todo))
                    sys.stderr.flush()
            work.task_done()

    threads = [threading.Thread(target=worker, args=(d,), daemon=True) for d in slots]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    if progress and todo:
        sys.stderr.write('\n')
    model_s = time.time() - t_model
    return results, {'fetch_s': round(fetch_s, 1), 'model_s': round(model_s, 1),
                     'fetch_errors': fetch_errors, 'classified': todo}


def _failed_row(row, err):
    rec = dict(row)
    msg = str(err)
    rec['state'] = 'NO-FAILING-JOB' if 'recorded no failing job' in msg else 'FETCH-FAILED'
    rec['class'] = 'unknown'
    rec['grounded'] = False
    rec['cause'] = msg[:300]
    rec['first_error_line'] = None
    return rec


# --------------------------------------------------------------------------- the board

def write_board(rows, meta):
    by_class = {}
    for r in rows:
        key = r.get('class') or 'unknown'
        if r['state'] in ('FETCH-FAILED', 'NO-FAILING-JOB', 'MODEL-ERROR'):
            key = 'no-evidence'
        by_class.setdefault(key, []).append(r)
    order = [c for c in CLASSES if c in by_class] + \
            [c for c in sorted(by_class) if c not in CLASSES]

    g = sum(1 for r in rows if r.get('grounded'))
    u = sum(1 for r in rows if r['state'] == 'UNGROUNDED')
    ne = sum(1 for r in rows if r['state'] in ('FETCH-FAILED', 'NO-FAILING-JOB', 'MODEL-ERROR'))

    out = []
    out.append('# red board')
    out.append('')
    out.append('written %s · %d red jobs across %d repositories · sweep %.0fs'
               % (meta['written'], len(rows), meta['repos_red'], meta['wall_s']))
    out.append('')
    out.append('%d grounded · %d UNGROUNDED (quote not found in the log) · %d no evidence to read'
               % (g, u, ne))
    out.append('')
    out.append('Every cause below quotes a line this script verified is present in that job\'s '
               'log, character for character. A row marked UNGROUNDED shows the model\'s claim '
               'as a claim and the log\'s own first error line beside it. The repo, run id, job '
               'and failing step come from the GitHub API, never from a model.')
    out.append('')
    out.append('**Read the quote, not the heading.** The class is a soft label and it is not '
               'stable: the same 48 jobs classified from a 40-line excerpt and from a 160-line '
               'excerpt disagreed on 13 of them (measured 2026-09-04, both runs fully inside '
               'the context window, neither truncated). The grounded quote is the durable part '
               'of a row - it was checked against the log. The class is only how the rows are '
               'sorted, and a count of a class is not a measurement of the estate.')
    out.append('')
    for cls in order:
        group = sorted(by_class[cls], key=lambda r: r.get('at') or '', reverse=True)
        head = CLASS_HELP.get(cls, 'the log could not be read at all')
        out.append('## %s — %d' % (cls, len(group)))
        out.append('')
        out.append('*%s*' % head)
        out.append('')
        for r in group:
            mark = '' if r.get('grounded') else ' **%s**' % r['state']
            at_head = 'AT HEAD' if r.get('at_head') else 'stale'
            out.append('- **%s** `%s` %s · %s%s'
                       % (r['repo'], r['run_id'], (r.get('at') or '')[:16].replace('T', ' '),
                          at_head, mark))
            out.append('  - step: `%s`' % (r.get('failing_step') or 'not recorded by the API'))
            if r.get('grounded'):
                out.append('  - %s' % r['cause'])
                out.append('  - > `%s`' % _one_line(r['quote']))
            else:
                if r.get('cause'):
                    out.append('  - claimed (rejected): %s' % _one_line(r['cause']))
                if r.get('rejected_first', {}).get('quote'):
                    out.append('  - rejected quote: `%s` — %s'
                               % (_one_line(r['rejected_first']['quote']),
                                  r.get('ground_reason') or r['rejected_first']['why']))
                if r.get('first_error_line'):
                    out.append('  - log says (quoted by triage.py, not by a model): `%s`'
                               % _one_line(r['first_error_line']))
        out.append('')

    out.append('---')
    out.append('')
    out.append('## how this was measured')
    out.append('')
    out.append('| | |')
    out.append('|---|---|')
    out.append('| reds enumerated | `python scripts/audit_estate.py --json` — %d red runs, %d failing jobs |'
               % (meta['red_runs'], len(rows)))
    out.append('| logs | `scripts/gh-api.sh repos/Ventusltd/<repo>/actions/jobs/<job_id>/logs --raw`, %d fetched, %.1fs |'
               % (meta['classified'], meta['fetch_s']))
    out.append('| excerpt | %d lines around the `##[error]` lines, median %d chars fed to the model |'
               % (meta['keep_lines'], meta['excerpt_median_chars']))
    out.append('| slots | %s |' % meta['slots_desc'])
    for dev, s in sorted(meta['per_device'].items()):
        out.append('| %s | %s, %d answers, median %.0f tok/s |'
                   % (dev, s['model'], s['n'], s['median_tok_s']))
    smi = meta['gpu']
    if smi.get('n'):
        out.append('| dGPU during the run | `%s` — %d samples, util min/median/max %d/%d/%d%%, '
                   '%.0f%% of samples over 50%%, VRAM %d–%d MiB |'
                   % (smi['command'], smi['n'], smi['util_min'], smi['util_med'],
                      smi['util_max'], smi['pct_samples_over_50'], smi['mem_min_mib'],
                      smi['mem_max_mib']))
    else:
        out.append('| dGPU during the run | NOT MEASURED: %s |' % smi.get('error'))
    out.append('| model wall | %.1fs for %d classifications, %d needed a second attempt |'
               % (meta['model_s'], meta['classified'], meta['retries']))
    out.append('| grounding | quote must be a whitespace-flattened, case-sensitive substring '
               'of the excerpt, ≥%d chars |' % MIN_QUOTE)
    out.append('| endpoint restarts absorbed | %d requests retried after a connection refusal '
               '(ollama is restarted under this process by other lanes) |'
               % meta.get('endpoint_retries', 0))
    out.extend(board_device_notes(meta))
    out.append('')
    out.append('Regenerate: `python familiars/triage.py`. This file is machine state, rewritten '
               'every sweep, and is not committed.')
    out.append('')
    text = '\n'.join(out)
    os.makedirs(LOGS, exist_ok=True)
    with open(BOARD_MD, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(text)
    with open(BOARD_JSON, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump({'meta': meta, 'rows': rows}, fh, indent=1)
    return text


def _one_line(s):
    return _WS.sub(' ', str(s)).strip().replace('`', "'")[:300]


# --------------------------------------------------------------------------- sweep

def load_estate(reuse=None):
    if reuse:
        with open(reuse, 'r', encoding='utf-8') as fh:
            return json.load(fh), 0.0
    t0 = time.time()
    r = subprocess.run([sys.executable, os.path.join(REPO_ROOT, 'scripts', 'audit_estate.py'),
                        '--json', ESTATE_JSON], cwd=REPO_ROOT, capture_output=True, text=True,
                       timeout=600, stdin=subprocess.DEVNULL)
    if r.returncode != 0 or not os.path.exists(ESTATE_JSON):
        raise L.LocalAIError('audit_estate.py failed (rc=%s): %s'
                             % (r.returncode, (r.stderr or r.stdout)[-400:]))
    with open(ESTATE_JSON, 'r', encoding='utf-8') as fh:
        return json.load(fh), time.time() - t0


def sweep(args):
    t0 = time.time()
    estate, audit_s = load_estate(args.estate)
    rows = reds_from_estate(estate)
    red_runs = sum(len(r.get('reds') or []) for r in estate.get('ci') or [])
    repos_red = sum(1 for r in estate.get('ci') or [] if r.get('reds'))
    if args.limit:
        rows = rows[:args.limit]
    print('%d red runs -> %d failing jobs across %d repositories (audit %.1fs)'
          % (red_runs, len(rows), repos_red, audit_s))

    slots = build_slots(args.gpu, args.igpu)
    # A DEAD ENDPOINT MUST REACH THE EXIT CODE AND THE BOARD. A sibling job was measured
    # returning "endpoint DOWN" for every single file and exiting 0 - an empty board that
    # reads as "nothing is broken". So each configured device is proved up front, a device
    # that is down is dropped from the pool rather than failing every row it touches, and
    # the drop is recorded in the board and forces a non-zero exit at the end.
    down = {}
    for dev in sorted(set(slots)):
        try:
            ctx = device_context(dev)
            # Reading /api/ps is NOT proof the device can do work. Measured 2026-09-04: a
            # governor installed in localai.py by the lane that owns the overnight autopilot
            # refuses the iGPU outright ("governor permits only the discrete-GPU lane") while
            # 11435 still answers /api/ps perfectly. The pre-flight passed, and then all 47
            # rows failed one at a time. So the proof is an actual generation, one token.
            L.generate(dev, 'ok', num_predict=1)
            print('%-5s %-30s context %d tokens, generation proved'
                  % (dev, L.DEVICES[dev]['model'], ctx))
        except Exception as e:                          # noqa: BLE001
            down[dev] = str(e)[:300]
            slots = [s for s in slots if s != dev]
            print('DEVICE DOWN: %s -- %s' % (dev, down[dev]), file=sys.stderr)
    if not slots:
        raise L.LocalAIError('every configured device is down: %s' % down)
    print('slots: %s' % slots_desc(slots))
    sampler = Sampler()
    sampler.start()
    results, timing = pump(rows, slots, keep_lines=args.lines, refresh=args.refresh)
    sampler.stop()

    per_device, retries = {}, 0
    ex_chars = []
    for r in results:
        if r.get('tok_s'):
            d = per_device.setdefault(r['device'], {'tok': [], 'model': r.get('model')})
            d['tok'].append(r['tok_s'])
        if r.get('attempts', 0) > 1:
            retries += 1
        if r.get('excerpt_chars'):
            ex_chars.append(r['excerpt_chars'])
    per_device = {k: {'model': v['model'], 'n': len(v['tok']),
                      'median_tok_s': statistics.median(v['tok'])}
                  for k, v in per_device.items()}

    wall = time.time() - t0
    meta = {
        'written': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'wall_s': round(wall, 1), 'audit_s': round(audit_s, 1),
        'red_runs': red_runs, 'repos_red': repos_red,
        'keep_lines': args.lines,
        'excerpt_median_chars': int(statistics.median(ex_chars)) if ex_chars else 0,
        'slots_desc': slots_desc(slots), 'per_device': per_device,
        'gpu': sampler.report(), 'retries': retries,
        'endpoint_retries': ENDPOINT_RETRIES[0],
        'devices_down': down,
        'contexts': dict(_CTX),
        'model_errors': sum(1 for r in results if r['state'] == 'MODEL-ERROR'),
        'truncated': sum(1 for r in results if 'TRUNCATED' in str(r.get('cause') or '')),
        'grounded': sum(1 for r in results if r.get('grounded')),
        'ungrounded': sum(1 for r in results if r['state'] == 'UNGROUNDED'),
        'no_evidence': sum(1 for r in results
                           if r['state'] in ('FETCH-FAILED', 'NO-FAILING-JOB', 'MODEL-ERROR')),
    }
    meta.update(timing)
    write_board(results, meta)

    print('grounded %d | UNGROUNDED %d | no evidence %d | second attempts %d | endpoint '
          'retries %d' % (meta['grounded'], meta['ungrounded'], meta['no_evidence'], retries,
                          meta['endpoint_retries']))
    smi = meta['gpu']
    if smi.get('n'):
        print('dGPU util min/med/max %d/%d/%d%% over %d samples, %.0f%% of samples over 50%%, '
              'VRAM %d-%d MiB' % (smi['util_min'], smi['util_med'], smi['util_max'], smi['n'],
                                  smi['pct_samples_over_50'], smi['mem_min_mib'],
                                  smi['mem_max_mib']))
    for dev, s in sorted(per_device.items()):
        print('%-5s %-30s %3d answers  median %.0f tok/s' % (dev, s['model'], s['n'],
                                                             s['median_tok_s']))
    print('wrote %s in %.1fs (fetch %.1fs, model %.1fs)'
          % (BOARD_MD, wall, timing['fetch_s'], timing['model_s']))

    # A missing input must FAIL, never skip. A red the audit named and this sweep could not
    # read is a HOLE in the board, and a board with an unannounced hole is worse than no
    # board - it gets quoted. Both halves count: a log that would not fetch, and a log that
    # was fetched and never classified because the endpoint stayed down.
    if down:
        print('FAIL: %d configured device(s) were DOWN and did no work: %s'
              % (len(down), ', '.join(down)), file=sys.stderr)
    bad = [r for r in results if r['state'] in ('FETCH-FAILED', 'MODEL-ERROR')]
    if bad or down:
        print('FAIL: %d of %d reds produced no reading (%d fetch, %d model); the board is '
              'short of the audit by that many'
              % (len(bad), len(results), timing['fetch_errors'], meta['model_errors']),
              file=sys.stderr)
        for r in bad[:5]:
            print('  %s %s run %s: %s' % (r['state'], r['repo'], r['run_id'], r['cause']),
                  file=sys.stderr)
        return 1
    return 0


def board_device_notes(meta):
    """The lines the board carries about the machine, so a reader of red-board.md never has
    to trust that the models were up or that they saw the whole excerpt."""
    out = []
    for dev, ctx in sorted((meta.get('contexts') or {}).items()):
        out.append('| %s context | %d tokens, read from /api/ps; every prompt is fitted under '
                   'it before it is sent |' % (dev, ctx))
    for dev, why in sorted((meta.get('devices_down') or {}).items()):
        out.append('| **%s DOWN** | did no work in this sweep: %s |' % (dev, why))
    if meta.get('truncated'):
        out.append('| **truncated prompts discarded** | %d |' % meta['truncated'])
    return out


def build_slots(n_gpu, n_igpu):
    return ['gpu'] * n_gpu + ['igpu'] * n_igpu


def slots_desc(slots):
    return ', '.join('%d x %s (%s)' % (slots.count(d), d, L.DEVICES[d]['model'])
                     for d in sorted(set(slots), key=slots.index))


# --------------------------------------------------------------------------- calibration

def calibrate_conc(args):
    """Find the concurrency at which this card stops paying, by measurement.

    THE WORKLOAD IS FIXED AND THE POOL VARIES. Every rung runs the SAME number of requests -
    `--work`, at least eight - through a pool of `conc` threads. Two reasons, both learned by
    getting it wrong here first:

      - Aggregate throughput is only comparable between rungs if the numerator is the same
        work. Issuing `conc` requests at rung `conc` compares four requests against sixteen.
      - A median over one sample is not a median. Per-request tok/s on this box swings 40%
        between single requests, and a 20%-degradation rule fired on that noise and chose
        concurrency 1 for a card that batches happily at 16.

    Three stopping conditions, whichever binds first, and the reason is printed:
      - VRAM headroom under --margin. On a shared 8 GB card this is the one that usually bites.
      - per-request tok/s below --per-floor of the single-request baseline: latency protection,
        so one answer does not take a minute just to make the batch look good.
      - aggregate throughput no longer rising by --gain: past that, more requests in flight buy
        nothing and only cost memory."""
    estate, _ = load_estate(args.estate)
    rows = [r for r in reds_from_estate(estate) if r['job_id']][:args.samples]
    bodies = []
    for row in rows:
        bodies.append((row, cached_log(row)))
    if not bodies:
        raise L.LocalAIError('no red jobs to calibrate on')
    work_n = max(8, args.work)
    print('calibrating on %d real job logs, %d lines each, %d requests per rung\n'
          % (len(bodies), args.lines, work_n))
    print('%-6s %-4s %6s %9s %9s %8s %8s' % ('device', 'conc', 'ok', 'agg tok/s',
                                             'per-req', 'wall', 'VRAM free'))
    best = {}
    for device in args.devices.split(','):
        prev_agg, baseline_per = None, None
        for conc in [int(x) for x in args.steps.split(',')]:
            got, tok, gen = [], [], []
            t0 = time.time()
            q = queue.Queue()
            for k in range(work_n):
                q.put(bodies[k % len(bodies)])
            lock = threading.Lock()

            def one():
                while True:
                    try:
                        row, log = q.get_nowait()
                    except queue.Empty:
                        return
                    try:
                        body = fit_excerpt(log, device, args.lines, 200)[0]
                        a = classify(row, body, device)
                        with lock:
                            got.append(a['grounded'])
                            gen.append(a['eval_tokens'])
                            if a['tok_s']:
                                tok.append(a['tok_s'])
                    except Exception as e:              # noqa: BLE001
                        with lock:
                            got.append(False)
                            print('   ! %s' % str(e)[:140])

            ts = [threading.Thread(target=one, daemon=True) for _ in range(conc)]
            for t in ts:
                t.start()
            for t in ts:
                t.join()
            wall = time.time() - t0
            free = vram_free_mib()
            per = statistics.median(tok) if tok else 0.0
            # Aggregate is GENERATED TOKENS OVER WALL CLOCK, and nothing else. The obvious
            # formula - median per-request tok/s times the number of requests - was written
            # here first and overstated throughput FOURFOLD at concurrency 16 (1052 claimed,
            # ~250 real), because each request's tok/s comes from Ollama's own eval_duration,
            # which is that request's generation clock and overlaps every other request's.
            # Multiplying overlapping clocks together counts the same second many times.
            agg = (sum(gen) / wall) if wall > 0 else 0.0
            print('%-6s %-4d %6d %9.0f %9.0f %8.1f %8s'
                  % (device, conc, sum(1 for g in got if g), agg, per, wall,
                     '%d MiB' % free if free is not None else '?'))
            if baseline_per is None:
                baseline_per = per
            why = None
            if free is not None and free < args.margin:
                why = 'VRAM headroom %d MiB is under the %d MiB margin' % (free, args.margin)
            elif baseline_per and per < baseline_per * args.per_floor:
                why = ('per-request tok/s %.0f is under %.0f%% of the single-request baseline '
                       '%.0f' % (per, 100 * args.per_floor, baseline_per))
            elif prev_agg and agg < prev_agg * (1 + args.gain):
                why = ('aggregate %.0f tok/s is not %.0f%% above the previous rung %.0f - more '
                       'requests in flight buy nothing' % (agg, 100 * args.gain, prev_agg))
            if why:
                print('   stop at %d: %s -> use %d' % (conc, why, max(1, best.get(device, 1))))
                break
            prev_agg = agg
            best[device] = conc
    print('\nchosen: %s' % ', '.join('%s=%d' % kv for kv in sorted(best.items())))
    return 0


def calibrate_lines(args):
    """How much log does the model actually need? Grounding rate and class stability against
    excerpt size, on real logs. The answer is not 'all of it': a bigger excerpt costs prefill
    on every request and gives the model more places to find a plausible-looking line."""
    estate, _ = load_estate(args.estate)
    rows = [r for r in reds_from_estate(estate) if r['job_id']][:args.samples]
    logs = [(r, cached_log(r)) for r in rows]
    print('%d logs, median %d chars raw\n' % (len(logs),
                                              statistics.median([len(l) for _, l in logs])))
    print('%-6s %10s %10s %8s %9s  %s' % ('lines', 'med chars', 'med tokens', 'grounded',
                                          'wall', 'classes'))
    for keep in [int(x) for x in args.steps.split(',')]:
        chars, ptoks, ok, classes = [], [], 0, {}
        t0 = time.time()
        q = queue.Queue()
        for row, log in logs:
            q.put((row, log))
        lock = threading.Lock()

        def one(device):
            nonlocal ok
            while True:
                try:
                    row, log = q.get_nowait()
                except queue.Empty:
                    return
                try:
                    body = fit_excerpt(log, device, keep, 200)[0]
                    a = classify(row, body, device)
                    with lock:
                        chars.append(len(body))
                        ptoks.append(a['prompt_tokens'])
                        classes[a['class']] = classes.get(a['class'], 0) + 1
                        if a['grounded']:
                            ok += 1
                except Exception as e:                  # noqa: BLE001
                    with lock:
                        print('   ! %s' % str(e)[:140])

        slots = build_slots(args.gpu, args.igpu)
        ts = [threading.Thread(target=one, args=(d,), daemon=True) for d in slots]
        for t in ts:
            t.start()
        for t in ts:
            t.join()
        print('%-6d %10d %10d %5d/%-3d %8.1fs  %s'
              % (keep, statistics.median(chars) if chars else 0,
                 statistics.median(ptoks) if ptoks else 0, ok, len(logs), time.time() - t0,
                 ' '.join('%s=%d' % kv for kv in sorted(classes.items()))))
    return 0


# --------------------------------------------------------------------------- cli

def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('--gpu', type=int, default=DEFAULT_GPU_SLOTS,
                   help='requests in flight on the dGPU (11434)')
    p.add_argument('--igpu', type=int, default=DEFAULT_IGPU_SLOTS,
                   help='requests in flight on the iGPU (11435); 0 while the governor is '
                        'installed - it refuses the iGPU outright')
    p.add_argument('--lines', type=int, default=DEFAULT_LINES, help='log lines in the excerpt')
    p.add_argument('--limit', type=int, default=0, help='only the newest N failing jobs')
    p.add_argument('--estate', help='reuse an existing audit_estate.py --json file')
    p.add_argument('--refresh', action='store_true', help='refetch cached job logs')
    p.add_argument('--loop', type=int, default=0, help='sweep every N seconds, forever')
    p.add_argument('--calibrate-conc', action='store_true')
    p.add_argument('--calibrate-lines', action='store_true')
    p.add_argument('--samples', type=int, default=6, help='logs used by a calibration')
    p.add_argument('--steps', default='1,2,3,4,6', help='calibration ladder')
    p.add_argument('--devices', default='gpu,igpu', help='devices for --calibrate-conc')
    p.add_argument('--margin', type=int, default=250, help='MiB of VRAM headroom to keep free')
    p.add_argument('--work', type=int, default=12,
                   help='requests per calibration rung; the same at every rung, min 8')
    p.add_argument('--per-floor', type=float, default=0.40, dest='per_floor',
                   help='stop when per-request tok/s falls below this fraction of the '
                        'single-request baseline')
    p.add_argument('--gain', type=float, default=0.10,
                   help='stop when a rung fails to raise aggregate tok/s by this fraction')
    args = p.parse_args()

    if args.calibrate_conc:
        return calibrate_conc(args)
    if args.calibrate_lines:
        return calibrate_lines(args)
    if args.loop:
        while True:
            try:
                sweep(args)
            except Exception as e:                      # noqa: BLE001 - a pump keeps pumping
                print('sweep failed: %s' % str(e)[:400], file=sys.stderr)
            time.sleep(args.loop)
    return sweep(args)


if __name__ == '__main__':
    sys.exit(main())
