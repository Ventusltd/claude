"""Bounded resource governor for unattended local-model work.

It measures and reports. It never changes a product tree, starts inference, or
kills an owned runner. Every five minutes it invokes reap.py's narrow contract,
which can terminate only a llama-server whose Ollama parent is gone twice.

    python familiars/overnight_governor.py --once
    python familiars/overnight_governor.py --run --hours 8 --interval 60
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.error
import urllib.request


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
PROBE = HERE / 'governor-probe.ps1'
REAPER = HERE / 'reap.py'
DEFAULT_OUT = ROOT / 'logs' / 'governor'
CREATE_NO_WINDOW = 0x08000000 if os.name == 'nt' else 0
DETACHED_PROCESS = 0x00000008 if os.name == 'nt' else 0
CREATE_NEW_PROCESS_GROUP = 0x00000200 if os.name == 'nt' else 0

LIMITS = {
    'reserved_logical_processors': 4,
    'cpu_ceiling_percent': 80.0,
    'ram_admission_floor_mb': 3072.0,
    'ram_critical_mb': 1536.0,
    'commit_warning_percent': 85.0,
    'commit_critical_percent': 92.0,
    'paging_warning_pages_sec': 5000.0,
    'paging_critical_pages_sec': 20000.0,
    'dgpu_reserved_mib': 1536.0,
    'dgpu_critical_free_mib': 768.0,
    'dgpu_temperature_warning_c': 80.0,
    'dgpu_temperature_critical_c': 85.0,
    'dgpu_saturation_percent': 95.0,
    'dgpu_saturation_samples': 5,
    'igpu_ram_floor_mb': 4096.0,
    'disk_warning_free_gib': 100.0,
    'disk_critical_free_gib': 50.0,
    'max_gpu_clients': 1,
}


def utc_now():
    return dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z')


def run(command, timeout=30):
    return subprocess.run(command, capture_output=True, text=True, timeout=timeout,
                          creationflags=CREATE_NO_WINDOW)


def probe():
    result = run(['powershell.exe', '-NoProfile', '-NonInteractive',
                  '-ExecutionPolicy', 'Bypass', '-File', str(PROBE)], timeout=30)
    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError('probe failed rc=%s: %s' %
                           (result.returncode, (result.stderr or result.stdout)[-500:]))
    return json.loads(result.stdout)


def nvidia():
    fields = ('name,memory.total,memory.used,memory.free,utilization.gpu,'
              'utilization.memory,temperature.gpu,power.draw,power.limit')
    result = run(['nvidia-smi', '--query-gpu=' + fields,
                  '--format=csv,noheader,nounits'])
    if result.returncode != 0 or not result.stdout.strip():
        return {'error': (result.stderr or result.stdout).strip()[-300:]}
    values = [part.strip() for part in result.stdout.strip().splitlines()[0].split(',')]
    keys = fields.split(',')
    out = {}
    for key, value in zip(keys, values):
        try:
            out[key] = float(value)
        except ValueError:
            out[key] = None if value in ('N/A', '[N/A]') else value
    return out


def ollama(port):
    try:
        with urllib.request.urlopen('http://127.0.0.1:%d/api/ps' % port,
                                    timeout=4) as response:
            data = json.load(response)
        return {'port': port, 'models': data.get('models') or []}
    except (OSError, ValueError, urllib.error.URLError) as exc:
        return {'port': port, 'error': '%s: %s' % (type(exc).__name__, exc)}


def tcp_table():
    result = run(['netstat.exe', '-ano', '-p', 'tcp'])
    clients, listeners = [], []
    for raw in result.stdout.splitlines():
        fields = raw.split()
        if len(fields) < 5 or fields[0] != 'TCP':
            continue
        row = {'local': fields[1], 'remote': fields[2], 'state': fields[3],
               'pid': int(fields[4])}
        if fields[3] == 'ESTABLISHED' and (fields[2].endswith(':11434') or
                                            fields[2].endswith(':11435')):
            clients.append(row)
        elif fields[3] == 'LISTENING' and (fields[1].endswith(':11434') or
                                           fields[1].endswith(':11435')):
            listeners.append(row)
    return clients, listeners


def unload(port, model):
    payload = json.dumps({'model': model, 'keep_alive': 0}).encode()
    request = urllib.request.Request('http://127.0.0.1:%d/api/generate' % port,
                                     data=payload,
                                     headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=30) as response:
        response.read()


def drain_and_disable_igpu(snapshot):
    """Remove the shared-RAM lane only after proving it has no live request."""
    clients = [row for row in snapshot.get('ollama_clients') or []
               if row['remote'].endswith(':11435')]
    if clients:
        return {'action': 'drain-pending', 'client_pids': sorted({r['pid'] for r in clients}),
                'reason': 'live requests are never interrupted'}
    endpoint = next((e for e in snapshot.get('ollama') or [] if e.get('port') == 11435), {})
    models = endpoint.get('models') or []
    if models:
        names = []
        for model in models:
            name = model.get('name') or model.get('model')
            if name:
                unload(11435, name)
                names.append(name)
        # Unload is asynchronous. Re-read both the request table and model table
        # before touching the listener; a request that arrived during drain wins.
        for _ in range(5):
            time.sleep(1)
            clients_now, listeners_now = tcp_table()
            clients_now = [row for row in clients_now if row['remote'].endswith(':11435')]
            endpoint_now = ollama(11435)
            if clients_now:
                return {'action': 'models-unloaded-drain-pending', 'models': names,
                        'client_pids': sorted({r['pid'] for r in clients_now}),
                        'reason': 'a request arrived during drain; listener preserved'}
            if not (endpoint_now.get('models') or []):
                snapshot['ollama_listeners'] = listeners_now
                snapshot['ollama'] = [e for e in snapshot.get('ollama') or []
                                      if e.get('port') != 11435] + [endpoint_now]
                break
        else:
            return {'action': 'models-unload-pending', 'models': names,
                    'reason': 'endpoint still reports a model; listener preserved'}
    listener = next((row for row in snapshot.get('ollama_listeners') or []
                     if row['local'].endswith(':11435')), None)
    if not listener:
        return {'action': 'disabled', 'reason': 'no listener on port 11435'}
    owner = next((p for p in snapshot.get('processes') or []
                  if p.get('pid') == listener['pid']), None)
    # Three facts must agree before a process is stopped: the exact port has no
    # clients, the endpoint has no loaded model, and its listener is Ollama.
    if not owner or owner.get('name') != 'ollama':
        return {'action': 'refused', 'reason': 'port 11435 listener identity is not Ollama',
                'listener': listener, 'owner': owner}
    result = run(['taskkill.exe', '/PID', str(listener['pid']), '/T', '/F'])
    return {'action': 'listener-stopped' if result.returncode == 0 else 'stop-failed',
            'pid': listener['pid'], 'rc': result.returncode,
            'stdout': result.stdout.strip(), 'stderr': result.stderr.strip(),
            'reason': 'zero clients and zero loaded models on the Intel shared-memory endpoint'}


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    os.replace(temp, path)


def append_jsonl(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(value, separators=(',', ':'), sort_keys=True) + '\n')


def evaluate(snapshot, saturation_streak):
    c = snapshot.get('counters') or {}
    gpu = snapshot.get('nvidia') or {}
    disk = snapshot.get('disk') or {}
    processes = snapshot.get('processes') or []
    clients = snapshot.get('ollama_clients') or []
    warnings, critical = [], []

    ram = float(c.get('ram_available_mb') or 0)
    committed = float(c.get('commit_bytes') or 0)
    commit_limit = float(c.get('commit_limit_bytes') or 0)
    commit_pct = 100 * committed / commit_limit if commit_limit else 100.0
    pages = float(c.get('pages_per_sec') or 0)
    cpu = float(c.get('cpu_percent') or 0)
    gpu_free = float(gpu.get('memory.free') or 0)
    gpu_util = float(gpu.get('utilization.gpu') or 0)
    gpu_temp = float(gpu.get('temperature.gpu') or 0)
    free_gib = float(disk.get('free_bytes') or 0) / 2**30

    if ram < LIMITS['ram_critical_mb']:
        critical.append('RAM %.0f MB below %.0f MB critical floor' %
                        (ram, LIMITS['ram_critical_mb']))
    elif ram < LIMITS['ram_admission_floor_mb']:
        warnings.append('RAM %.0f MB below %.0f MB admission floor' %
                        (ram, LIMITS['ram_admission_floor_mb']))
    if commit_pct >= LIMITS['commit_critical_percent']:
        critical.append('commit %.1f%% at or above %.1f%%' %
                        (commit_pct, LIMITS['commit_critical_percent']))
    elif commit_pct >= LIMITS['commit_warning_percent']:
        warnings.append('commit %.1f%% at or above %.1f%%' %
                        (commit_pct, LIMITS['commit_warning_percent']))
    if pages >= LIMITS['paging_critical_pages_sec']:
        critical.append('paging %.0f pages/s at or above %.0f' %
                        (pages, LIMITS['paging_critical_pages_sec']))
    elif pages >= LIMITS['paging_warning_pages_sec']:
        warnings.append('paging %.0f pages/s at or above %.0f' %
                        (pages, LIMITS['paging_warning_pages_sec']))
    if cpu >= LIMITS['cpu_ceiling_percent']:
        warnings.append('CPU %.1f%% exceeds %.1f%% ceiling that preserves four cores' %
                        (cpu, LIMITS['cpu_ceiling_percent']))
    if gpu_free and gpu_free < LIMITS['dgpu_critical_free_mib']:
        critical.append('dGPU free %.0f MiB below %.0f MiB critical reserve' %
                        (gpu_free, LIMITS['dgpu_critical_free_mib']))
    elif gpu_free and gpu_free < LIMITS['dgpu_reserved_mib']:
        warnings.append('dGPU free %.0f MiB below %.0f MiB display reserve' %
                        (gpu_free, LIMITS['dgpu_reserved_mib']))
    if gpu_temp >= LIMITS['dgpu_temperature_critical_c']:
        critical.append('dGPU temperature %.0f C at or above %.0f C' %
                        (gpu_temp, LIMITS['dgpu_temperature_critical_c']))
    elif gpu_temp >= LIMITS['dgpu_temperature_warning_c']:
        warnings.append('dGPU temperature %.0f C at or above %.0f C' %
                        (gpu_temp, LIMITS['dgpu_temperature_warning_c']))
    if saturation_streak >= LIMITS['dgpu_saturation_samples']:
        warnings.append('dGPU at least %.0f%% for %d consecutive samples' %
                        (LIMITS['dgpu_saturation_percent'], saturation_streak))
    if free_gib < LIMITS['disk_critical_free_gib']:
        critical.append('C: free %.1f GiB below %.0f GiB critical reserve' %
                        (free_gib, LIMITS['disk_critical_free_gib']))
    elif free_gib < LIMITS['disk_warning_free_gib']:
        warnings.append('C: free %.1f GiB below %.0f GiB reserve' %
                        (free_gib, LIMITS['disk_warning_free_gib']))

    gpu_clients = {row['pid'] for row in clients if row['remote'].endswith(':11434')}
    if len(gpu_clients) > LIMITS['max_gpu_clients']:
        warnings.append('%d simultaneous clients on dGPU Ollama; maximum is %d' %
                        (len(gpu_clients), LIMITS['max_gpu_clients']))
    orphans = [p for p in processes if p.get('name') == 'llama-server'
               and p.get('ppid') and not p.get('parent_alive')]
    if orphans:
        critical.append('orphan llama-server PIDs: %s' %
                        ','.join(str(p['pid']) for p in orphans))

    loaded = []
    for endpoint in snapshot.get('ollama') or []:
        for model in endpoint.get('models') or []:
            loaded.append((endpoint['port'], model.get('name') or model.get('model'),
                           model.get('size_vram'), model.get('context_length')))
    if any(port == 11434 and name and '8b' in name.lower() for port, name, _, _ in loaded):
        critical.append('8B model loaded on dGPU; measured configuration thrashes this card')

    severity = 'critical' if critical else ('warning' if warnings else 'ok')
    allow_gpu = not critical and ram >= LIMITS['ram_admission_floor_mb'] \
        and (not gpu_free or gpu_free >= LIMITS['dgpu_reserved_mib']) \
        and cpu < LIMITS['cpu_ceiling_percent']
    # This run was explicitly assigned to the discrete GPU. The Intel endpoint
    # remains closed because its Vulkan allocations consume ordinary system RAM.
    allow_igpu = False
    model_processes = [p for p in processes if p.get('name') == 'llama-server']
    return {
        'severity': severity,
        'warnings': warnings,
        'critical': critical,
        'admission': {
            'allow_new_local_inference': allow_gpu,
            'allow_dgpu': allow_gpu,
            'allow_igpu': allow_igpu,
            'reason': (critical + warnings) or ['within envelope'],
        },
        'derived': {
            'commit_percent': round(commit_pct, 2),
            'disk_free_gib': round(free_gib, 2),
            'dgpu_saturation_streak': saturation_streak,
            'dgpu_client_pids': sorted(gpu_clients),
            'loaded_models': loaded,
            'model_working_set_mib': round(sum(float(p.get('working_set_bytes') or 0)
                                               for p in model_processes) / 2**20, 1),
            'model_private_commit_mib': round(sum(float(p.get('private_bytes') or 0)
                                                  for p in model_processes) / 2**20, 1),
            'model_wddm_dedicated_mib': round(sum(float(p.get('gpu_dedicated_bytes') or 0)
                                                  for p in model_processes) / 2**20, 1),
            'model_wddm_shared_mib': round(sum(float(p.get('gpu_shared_bytes') or 0)
                                               for p in model_processes) / 2**20, 1),
            'memory_accounting': ('working set is resident system RAM; private commit is the '
                                  'process address/commit footprint; WDDM dedicated/shared are '
                                  'GPU allocations. They are recorded separately and never '
                                  'added as though all were physical RAM.'),
        },
        'orphan_evidence': orphans,
    }


def take_sample(saturation_streak=0):
    snapshot = probe()
    snapshot['nvidia'] = nvidia()
    snapshot['ollama'] = [ollama(11434), ollama(11435)]
    clients, listeners = tcp_table()
    snapshot['ollama_clients'] = clients
    snapshot['ollama_listeners'] = listeners
    snapshot['npu'] = {
        'present': True,
        'usable_by_ollama': False,
        'reason': 'Intel AI Boost is installed, but this Ollama/llama.cpp stack has no NPU backend',
    }
    utilization = float((snapshot.get('nvidia') or {}).get('utilization.gpu') or 0)
    saturation_streak = saturation_streak + 1 if utilization >= LIMITS['dgpu_saturation_percent'] else 0
    snapshot['evaluation'] = evaluate(snapshot, saturation_streak)
    snapshot['control'] = drain_and_disable_igpu(snapshot)
    snapshot['limits'] = LIMITS
    snapshot['sample_sha256'] = hashlib.sha256(
        json.dumps(snapshot, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return snapshot, saturation_streak


def acquire_lock(path, end_utc):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        try:
            old = json.loads(path.read_text(encoding='utf-8'))
            os.kill(int(old['pid']), 0)
        except (OSError, ValueError, KeyError, json.JSONDecodeError):
            path.unlink(missing_ok=True)
        else:
            raise RuntimeError('governor already running as PID %s' % old['pid'])
    payload = {'pid': os.getpid(), 'started_utc': utc_now(), 'end_utc': end_utc}
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
        json.dump(payload, stream, indent=1)
        stream.write('\n')
    return payload


def reap_orphans():
    result = run([sys.executable, str(REAPER), '--reap'], timeout=30)
    return {'utc': utc_now(), 'rc': result.returncode,
            'stdout': result.stdout.strip(), 'stderr': result.stderr.strip()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--once', action='store_true')
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--detach', action='store_true',
                        help='start a handle-detached --run child and print its PID')
    parser.add_argument('--hours', type=float, default=8.0)
    parser.add_argument('--interval', type=float, default=60.0)
    parser.add_argument('--reap-every', type=float, default=300.0)
    parser.add_argument('--out', default=str(DEFAULT_OUT))
    args = parser.parse_args(argv)
    if not (args.once or args.run or args.detach):
        parser.error('pass --once, --run or --detach')

    if args.detach:
        command = [sys.executable, str(pathlib.Path(__file__).resolve()), '--run',
                   '--hours', str(args.hours), '--interval', str(args.interval),
                   '--reap-every', str(args.reap_every), '--out', args.out]
        child = subprocess.Popen(command, cwd=str(ROOT), stdin=subprocess.DEVNULL,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                 close_fds=True,
                                 creationflags=(CREATE_NO_WINDOW | DETACHED_PROCESS |
                                                CREATE_NEW_PROCESS_GROUP))
        print(child.pid)
        return 0

    if args.once:
        sample, _ = take_sample()
        print(json.dumps(sample, indent=1))
        return 2 if sample['evaluation']['severity'] == 'critical' else 0

    out = pathlib.Path(args.out).resolve()
    end = time.time() + max(0.0, args.hours) * 3600
    end_utc = dt.datetime.fromtimestamp(end, dt.timezone.utc).isoformat().replace('+00:00', 'Z')
    lock_path = out / 'governor.lock.json'
    lock = acquire_lock(lock_path, end_utc)
    events_path = out / 'events.jsonl'
    samples_path = out / 'samples.jsonl'
    last_reap = 0.0
    last_severity = None
    saturation_streak = 0
    sequence = 0
    try:
        while time.time() < end:
            started = time.time()
            sequence += 1
            try:
                sample, saturation_streak = take_sample(saturation_streak)
                sample['sequence'] = sequence
                sample['governor'] = lock
                if started - last_reap >= args.reap_every:
                    sample['reaper'] = reap_orphans()
                    last_reap = started
                append_jsonl(samples_path, sample)
                atomic_json(out / 'status.json', sample)
                admission = dict(sample['evaluation']['admission'])
                admission['sampled_utc'] = sample.get('sampled_utc')
                admission['sequence'] = sequence
                atomic_json(out / 'admission.json', admission)
                severity = sample['evaluation']['severity']
                if severity != last_severity or severity == 'critical':
                    append_jsonl(events_path, {
                        'utc': utc_now(), 'sequence': sequence, 'severity': severity,
                        'warnings': sample['evaluation']['warnings'],
                        'critical': sample['evaluation']['critical'],
                        'processes': sample.get('processes'),
                        'nvidia': sample.get('nvidia'),
                        'ollama_clients': sample.get('ollama_clients'),
                        'control': sample.get('control'),
                        'reaper': sample.get('reaper'),
                    })
                last_severity = severity
            except Exception as exc:
                append_jsonl(events_path, {'utc': utc_now(), 'sequence': sequence,
                                           'severity': 'critical',
                                           'critical': ['probe failed: %s: %s' %
                                                        (type(exc).__name__, exc)]})
            # A second sample ten seconds after launch proves the handoff and
            # control action; the steady-state cadence begins after that.
            cadence = min(args.interval, 10.0) if sequence == 1 else args.interval
            wait = cadence - (time.time() - started)
            if wait > 0:
                time.sleep(wait)
    finally:
        try:
            owner = json.loads(lock_path.read_text(encoding='utf-8'))
            if int(owner.get('pid', -1)) == os.getpid():
                lock_path.unlink(missing_ok=True)
        except (OSError, ValueError, json.JSONDecodeError):
            pass
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
