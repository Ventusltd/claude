# live-log.ps1 - append-only plain-text record of what is actually happening.
#
# Written 2026-09-05 after a session in which context was lost twice: once to a
# usage limit, once to a log that existed only in a hidden path. This writes a
# simple .txt that any human, or ChatGPT, Gemini or Claude, can read cold.
#
# It records FACTS, not narrative: commit heads, dirty files, live HTTP codes,
# and long-lived processes. It never guesses and it never grades.
#
#   powershell -ExecutionPolicy Bypass -File logs\live-log.ps1
#
# Ctrl-C stops it. It appends, so stopping and restarting loses nothing.

$ErrorActionPreference = 'SilentlyContinue'
$LogPath = Join-Path $PSScriptRoot 'SESSION-LIVE-LOG.txt'
$GitHub  = 'C:\Users\vikra\OneDrive\Documents\GitHub'

$Repos = @(
  'globalgrid2050','gridatlas','gridatlas-main-202609050200',
  'pipelinenews','ventus-grid-engine','testcode','spiders','claude'
)

$Urls = @(
  'https://globalgrid2050.com/',
  'https://globalgrid2050.com/status.html',
  'https://globalgrid2050.com/uk_renewables_pipeline/v9.7/',
  'https://ventusltd.github.io/gridatlas/atlas/',
  'https://ventusltd.github.io/gridatlas/atlas/current.json',
  'https://ventusltd.github.io/ventus-grid-engine/'
)

function Write-Log([string]$Text) { Add-Content -Path $LogPath -Value $Text -Encoding utf8 }

if (-not (Test-Path $LogPath)) {
  Write-Log "GLOBALGRID2050 LIVE LOG"
  Write-Log "Plain text on purpose. Append-only. All times UTC; the architect's clock is BST, UTC+1."
  Write-Log "Started $((Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ'))"
  Write-Log ("=" * 78)
}

while ($true) {
  $stamp = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
  Write-Log ""
  Write-Log ("-" * 78)
  Write-Log "TICK $stamp"

  Write-Log "REPOS  (branch | head | subject | dirty files)"
  foreach ($r in $Repos) {
    $p = Join-Path $GitHub $r
    if (-not (Test-Path $p)) { Write-Log ("  {0,-32} ABSENT" -f $r); continue }
    Push-Location $p
    $branch  = (git branch --show-current) 2>$null
    $head    = (git log -1 --format='%h %s') 2>$null
    $dirty   = @(git status --porcelain) 2>$null
    Pop-Location
    if ($head.Length -gt 62) { $head = $head.Substring(0,62) }
    Write-Log ("  {0,-32} {1,-28} {2}" -f $r, $branch, $head)
    if ($dirty.Count -gt 0) {
      Write-Log ("  {0,-32} DIRTY: {1} file(s)" -f '', $dirty.Count)
      foreach ($d in ($dirty | Select-Object -First 8)) { Write-Log ("  {0,-32}   {1}" -f '', $d) }
    }
  }

  Write-Log "LIVE  (http status | bytes | url)"
  foreach ($u in $Urls) {
    try {
      $sw = [Diagnostics.Stopwatch]::StartNew()
      $resp = Invoke-WebRequest -Uri $u -Method Get -TimeoutSec 20 -UseBasicParsing
      $sw.Stop()
      Write-Log ("  {0,-5} {1,9} bytes {2,6} ms  {3}" -f $resp.StatusCode, $resp.RawContentLength, $sw.ElapsedMilliseconds, $u)
    } catch {
      Write-Log ("  ERR   {0}  {1}" -f $u, $_.Exception.Message)
    }
  }

  # Long-lived processes matter: ten orphaned servers were found running for
  # eight hours on this machine, which is why this section exists at all.
  $procs = Get-CimInstance Win32_Process -Filter "Name='node.exe' or Name='python.exe'" |
    Where-Object { $_.CommandLine -match 'serve|http.server|proof|emulator|adb' }
  if ($procs) {
    Write-Log "PROCESSES  (pid | minutes | command)"
    foreach ($pr in $procs) {
      $mins = [math]::Round(((Get-Date) - $pr.CreationDate).TotalMinutes, 1)
      $cmd  = $pr.CommandLine
      if ($cmd.Length -gt 90) { $cmd = $cmd.Substring(0,90) }
      Write-Log ("  {0,-7} {1,7} min  {2}" -f $pr.ProcessId, $mins, $cmd)
    }
  } else {
    Write-Log "PROCESSES  none of interest"
  }

  Start-Sleep -Seconds 120
}
