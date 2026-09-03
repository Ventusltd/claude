# Local AI on this machine

Measured 2026-09-03, 22:00–23:00 UTC, on the laptop that carries the GlobalGrid2050 estate.
Every number below was read from the named command on that date. Nothing here is a
manufacturer figure and nothing is an estimate.

## The hardware, as measured

| what | reading | read from |
|---|---|---|
| CPU | Intel Core Ultra 7 255HX, **20 cores / 20 threads** | `Get-CimInstance Win32_Processor` |
| RAM | **15.46 GB** total; free ranged **0.46 → 6.07 GB** during the session | `Win32_OperatingSystem` |
| commit | **35.32 GB committed of a 38.97 GB limit** at the tightest point | `\Memory\Committed Bytes` |
| disk C: | **340.9 GB free** of 926.2 GB | `Win32_LogicalDisk` |
| discrete GPU | **NVIDIA GeForce RTX 5070 Laptop GPU, 8151 MiB**, driver 592.02, CUDA 13.1, compute **12.0** (Blackwell sm_120) | `nvidia-smi`, Ollama `inference compute` |
| integrated GPU | **Intel(R) Graphics**, driver 32.0.101.8724, Vulkan, 8.8 GiB *shared* system memory | `Win32_VideoController`, Ollama device log |
| NPU | **Intel(R) AI Boost** present, `PCI\VEN_8086&DEV_AD1D`, status OK, driver 32.0.100.4778 | `Win32_PnPEntity`, `Win32_PnPSignedDriver` |

Nothing was installed before this session: `where ollama`, `where nvcc` and
`import torch` all came back empty.

## Is the NPU reachable? No — and that is a plain no.

The Intel AI Boost NPU **is physically present and its driver is healthy** (`npu.inf` in the
DriverStore, dated 28/04/2026). It is **not reachable from this toolchain**, and no amount of
Ollama configuration will change that:

- llama.cpp — which is what Ollama runs — has **no NPU backend**. Its backends here are CUDA
  and Vulkan. Neither targets AI Boost.
- Reaching the NPU needs a different stack: OpenVINO GenAI, or ONNX Runtime with the Intel NPU
  execution provider. Measured on this machine: `openvino`, `onnxruntime` and `torch` are all
  **not installed**, and there is no OpenVINO runtime under `System32` or `Program Files\Intel`.
- The model formats do not transfer either. GGUF is not an NPU format; using the NPU would mean
  converting to OpenVINO IR or ONNX and maintaining a **second, parallel model store**.

So: the NPU is real, it is idle, and it stayed idle. Claiming otherwise would be inventing a
measurement. If it is ever wanted, the work is an OpenVINO GenAI install plus a model
conversion — not a setting.

## What was installed

```
winget install --id Ollama.Ollama -e --accept-source-agreements --accept-package-agreements
# -> Ollama 0.33.3

ollama pull qwen3:4b-instruct-2507-q4_K_M     # 2.5 GB  - the working model
ollama pull qwen3:0.6b                        # 522 MB  - the iGPU's classifier
ollama pull qwen3:8b                          # 5.2 GB  - measured, then REJECTED, see below
```

Server settings, set once at User scope so a normal Ollama start inherits them:

```
OLLAMA_FLASH_ATTENTION = 1
OLLAMA_KV_CACHE_TYPE   = q8_0      # halves the KV cache; this card has no spare MiB
OLLAMA_NUM_PARALLEL    = 2
OLLAMA_CONTEXT_LENGTH  = 8192
OLLAMA_KEEP_ALIVE      = 30m
OLLAMA_MAX_LOADED_MODELS = 2
```

The second server, pinned to the Intel adapter, is started by
`python familiars/localai.py --serve-igpu`, which sets:

```
OLLAMA_HOST=127.0.0.1:11435   CUDA_VISIBLE_DEVICES=-1
GGML_VK_VISIBLE_DEVICES=1     OLLAMA_IGPU_ENABLE=1
```

## Throughput, and the proof the GPU did the work

`ollama ps` reporting `100% GPU` is **not** proof, as the 8B below shows. Three things together
are: layers offloaded in the llama.cpp log, `size_vram == size` in `/api/ps`, and GPU
utilisation moving under load.

Sampling `nvidia-smi` every 700 ms across one generation — utilisation went **3–6 % idle →
95–97 % during generation → back to 4 %**, with VRAM flat. The card, not the CPU, did it.

| configuration | footprint | tokens/s | note |
|---|---|---|---|
| qwen3:4b q4_K_M, ctx 8192, 1 request | 3.9 GB, 100 % GPU | **108.5 – 118.9** | the working configuration |
| qwen3:4b q4_K_M, ctx 8192, 2 concurrent | 3.9 GB, 100 % GPU | **92.2 + 92.2 = 184.4** | best throughput on this card |
| qwen3:0.6b on **Intel iGPU**, Vulkan | 930 MB shared, 29/29 layers | **47–69** | a genuine second engine |
| both adapters at once, 2 requests each | — | **184.4 + 94.5 = 278.9** | RTX 92.2×2, Intel 47.6/46.9 |
| **qwen3:8b q4_K_M** | 6.3 GB, "100 % GPU" | **7.4** | **rejected — see below** |
| qwen3:4b, NUM_PARALLEL=4, ctx 8192 | peak 7522 MiB | 10.3 each, 37 aggregate | **rejected** |

The iGPU offload is not inferred. The Vulkan server's own log:

```
llama_prepare_model_devices: using device Vulkan0 (Intel(R) Graphics) - 8313 MiB free
load_tensors: offloaded 29/29 layers to GPU
load_tensors:      Vulkan0 model buffer size =   409.29 MiB
llama_kv_cache:    Vulkan0 KV buffer size =   448.00 MiB
```

## The finding that governs everything else

**On this 8 GB laptop card, throughput is set by VRAM headroom, not by model size or slot
count — and every failure mode still reports `100% GPU`.**

Three configurations hit the same wall at ~7.5 GB of the 8151 MiB card:

| what was tried | VRAM at peak | result |
|---|---|---|
| qwen3:8b q4 | 7532 MiB used, 360 free | 7.4 tok/s — **15× slower** than the 4B |
| qwen3:4b, 4 parallel slots | 7522 MiB used | 10.3 tok/s per request |
| qwen3:4b while an orphan held 4.9 GB | 7552 MiB used | 25–28 tok/s, GPU util **5–27 %** |

Low utilisation with low throughput is the signature. It is not compute starvation — it is
Windows WDDM silently paging VRAM into system RAM, which the driver permits and which
`nvidia-smi` and `ollama ps` both report as a healthy fully-offloaded model. In the worst case
Ollama did eventually admit it (`79%/21% CPU/GPU`), but only after the damage was visible.

**The detector is tokens/s, never the offload percentage.** A 4B at 108 tok/s and an 8B at
7.4 tok/s both say "100% GPU".

Consequences, in order of usefulness:

1. **Do not run an 8B on this card.** It fits and it is unusable. The 4B is 15× faster.
2. **Do not raise `OLLAMA_NUM_PARALLEL` past 2.** Slots × context is a VRAM budget: 2 slots ×
   8192 costs 2448 MiB of KV cache at q8_0. Four slots cost the card its headroom and lose
   more to paging than they gain in concurrency.
3. **The desktop is a real tenant.** This card drives a 3840- and a 2560-wide display; the
   Windows desktop alone held between 1.5 and 4.8 GB across the session. Budget for it.
4. **Reap before concluding the card is full.** `python familiars/reap.py` — an orphaned
   `llama-server` was holding **4953 MB of VRAM**; reaping three of them moved free VRAM
   **371 → 5454 MiB**. Note that reap.py reports a runner's *system RAM* working set, so the
   worst offender looked like 65 MB while holding 4.9 GB of VRAM. Trust the GPU counter:
   `Get-Counter '\GPU Process Memory(*)\Dedicated Usage'`.

## The integrated GPU is worth using, and it is switched on

Ollama drops iGPUs by default and says so: `dropping integrated GPU; to enable, set
OLLAMA_IGPU_ENABLE=1`. Enabled and pinned, the Intel adapter runs qwen3:0.6b at **47–69 tok/s
with 29/29 layers offloaded**, in shared system memory, taking **nothing** from the RTX's
8151 MiB. Under simultaneous load the discrete card lost only 92.2 → 92.2 tok/s (nothing
measurable) while the Intel adapter added 94.5 tok/s.

That is the argument for it: when the discrete card is contended by another lane, the iGPU is
a **second engine rather than a competitor for the same memory**.

Its limit is quality, not speed, and the limit is the 0.6B model rather than the adapter. On
cvaa's untracked files the 0.6B called a markdown note on CRLF-versus-LF hashing
*"a deterministic, non-viable repository"* — fluent and wrong — where the 4B on the RTX read it
correctly as *"a technical analysis of a file system and Git line-ending inconsistency issue"*.
So `triage-untracked` accepts `--device gpu` when the answer has to be right, and defaults to
the iGPU for bulk work that the discrete card should not be interrupted for.

## What it does for the estate

```
python familiars/localai.py --health          # exits 2 if any endpoint is down
python familiars/localai.py --bench           # saturates both adapters
python familiars/localai.py --serve-igpu      # start the Intel-pinned server

python familiars/localai.py --job classify-ci-failure --input Ventusltd/cvaa#33712716373
python familiars/localai.py --job summarise-commit    --input <sha> --repo gridatlas
python familiars/localai.py --job triage-untracked    --input cvaa [--device gpu]
```

Real output, 2026-09-03:

```
STEP: Run node /home/runner/work/cvaa/cvaa/inoculate.mjs /tmp/cvaa-clean-e7PKRH --no-lock --no-write --json
CAUSE: JSON contract failed with "2 antibody problem(s)", indicating the script did not pass its validation.
[cross-check, GitHub jobs API] failing job 'selftest', failing step(s): 'Antibodies fire on disease and stay silent on health'
```

`classify-ci-failure` prints the GitHub jobs API's own record of the failing job and step
beside the model's answer. The model is not trusted; it is **cross-checked in the same breath**,
so a confident wrong answer is visible rather than believed.

## Four traps this cost, worth not paying twice

1. **`bash` on this machine's PATH is the WSL Store stub**, `WindowsApps\bash.exe` — the same
   trap as the `python3` stub CLAUDE.md records, but worse, because it does not error, it
   **hangs**. `gh-api.sh` through it timed out at 180 s and again at 25 s with
   `stdin=DEVNULL`; the identical command in Git Bash returned 30,442 bytes in **1.345 s**.
   A hang reads as a slow network. `localai.py` resolves `C:\Program Files\Git\bin\bash.exe`
   explicitly and refuses the stub by name.

2. **`/api/generate` silently truncates an over-long prompt; `/api/chat` returns HTTP 400.**
   The context was 4096 while the CI-log prompts were 5,268–7,548 tokens, so the classifier had
   been reading a *cut* log and describing the passing tests at the top of it. It looked like a
   weak model. It was a truncated prompt, and only the endpoint that failed loudly revealed it.

3. **`qwen3:0.6b` is a thinking model, and thinking silently ate the whole answer.** With a
   90-token budget it produced `response=""`, `done_reason="length"` and 392 characters of
   `thinking`. `generate()` now raises on an empty completion rather than letting it print as
   `None` in a results table, which is how it first appeared.

4. **Instructions do not constrain output shape; examples do.** "Reply in exactly two lines, no
   markdown" was ignored three times running — the 4B answered with headings, bold and an
   emoji. Putting the example in as a real **assistant turn** via `/api/chat` fixed it first
   time.

And one that is the estate's own rule, caught here again: with the iGPU server stopped, every
untracked file came back "endpoint DOWN" and `triage-untracked` still **exited 0** — a listing
that described nothing, presented as a completed triage. Per-file errors are now counted and
carried out to the exit code.

## Where the environment variables live

Set at **User** scope, so the tray app inherits them on a normal start. Note that
`[Environment]::SetEnvironmentVariable(...,'User')` does **not** reach an already-running
PowerShell's child processes — the first restart silently kept `OLLAMA_FLASH_ATTENTION:false`
and `NUM_PARALLEL:1`, which the server's own `server config` log line exposed. Always read that
line back after a restart rather than trusting the variable was set.
