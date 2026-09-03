"""reap.py - kill local-AI runners that hold memory with no task behind them.

WHY THIS EXISTS

Measured on 2026-09-03: the RTX 5070 reported 904 MiB free of 8151, and system RAM
reported 0.7 GB free of 15.5. The obvious reading was "this machine is maxed out".
It was not. Two llama-server.exe processes were holding 3.4 GB of VRAM and 3.2 GB of
RAM between them, and BOTH had a dead parent. The `ollama serve` that spawned each one
had exited without taking its runner with it. Nothing listened on 11434, so no request
could ever reach either runner again - but they still answered 200 on their own private
ports, so every liveness check that pinged the runner directly said "healthy".

That is the trap. A leaked runner looks alive from the outside. It holds a model in VRAM,
it responds to /health, and it will sit there until reboot. The only thing that
distinguishes it from a working runner is that its parent process is gone.

Reaping both took VRAM free from 904 MiB to 6762 MiB, and RAM free from 0.7 GB to 5.0 GB.
No task lost anything, because no task could reach them.

WHAT IT DOES NOT DO

It never kills a runner whose parent is alive - that one is serving somebody, possibly
another agent lane mid-call. Parentage is the whole test. --dry-run is the default;
you must pass --reap to actually kill anything.

Usage:
    python familiars/reap.py              # report only
    python familiars/reap.py --reap       # report, then kill the orphans
"""
import subprocess, sys, json

PS = ["powershell.exe", "-NoProfile", "-Command"]

def ps(cmd):
    r = subprocess.run(PS + [cmd], capture_output=True, text=True)
    return r.stdout.strip()

def gpu():
    r = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.used,memory.free", "--format=csv,noheader,nounits"],
        capture_output=True, text=True)
    if r.returncode != 0:
        return None
    used, free = [int(x) for x in r.stdout.strip().split(",")]
    return used, free

def ram_free_gb():
    out = ps("(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory")
    return int(out) / 1048576 if out.isdigit() else None

def runners():
    """Every llama-server, with its parent and whether that parent still exists."""
    out = ps(
        "Get-CimInstance Win32_Process -Filter \"Name='llama-server.exe'\" | "
        "ForEach-Object { $p=$_; $alive = [bool](Get-CimInstance Win32_Process "
        "-Filter (\"ProcessId=\"+$p.ParentProcessId) -ErrorAction SilentlyContinue); "
        "[pscustomobject]@{pid=$p.ProcessId; ppid=$p.ParentProcessId; "
        "mb=[int]($p.WorkingSetSize/1MB); alive=$alive} } | ConvertTo-Json -Compress"
    )
    if not out:
        return []
    d = json.loads(out)
    return d if isinstance(d, list) else [d]

def main():
    do_reap = "--reap" in sys.argv
    g0, r0 = gpu(), ram_free_gb()

    rs = runners()
    if not rs:
        print("no llama-server processes running")
        return 0

    orphans = [r for r in rs if not r["alive"]]
    for r in rs:
        tag = "ORPHAN - no parent, unreachable" if not r["alive"] else "in use - parent alive"
        print(f"  pid {r['pid']:<7} ppid {r['ppid']:<7} {r['mb']:>5} MB   {tag}")

    if not orphans:
        print("\nnothing to reap; every runner has a live parent")
        return 0

    print(f"\n{len(orphans)} orphan(s) holding memory with no task behind them")
    if not do_reap:
        print("dry run - pass --reap to release them")
        return 0

    for r in orphans:
        ps(f"Stop-Process -Id {r['pid']} -Force -ErrorAction SilentlyContinue")
        print(f"  reaped pid {r['pid']}")

    g1, r1 = gpu(), ram_free_gb()
    if g0 and g1:
        print(f"\nVRAM free  {g0[1]} -> {g1[1]} MiB  (+{g1[1]-g0[1]})")
    if r0 and r1:
        print(f"RAM  free  {r0:.1f} -> {r1:.1f} GB  (+{r1-r0:.1f})")
    return 0

if __name__ == "__main__":
    sys.exit(main())
