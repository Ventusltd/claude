$ErrorActionPreference = 'SilentlyContinue'
$ProgressPreference = 'SilentlyContinue'

$counterPaths = @(
  '\Processor(_Total)\% Processor Time',
  '\System\Processor Queue Length',
  '\Memory\Available MBytes',
  '\Memory\Committed Bytes',
  '\Memory\Commit Limit',
  '\Memory\Pages/sec',
  '\Paging File(_Total)\% Usage',
  '\PhysicalDisk(_Total)\Current Disk Queue Length',
  '\PhysicalDisk(_Total)\Avg. Disk sec/Read',
  '\PhysicalDisk(_Total)\Avg. Disk sec/Write',
  '\GPU Engine(*)\Utilization Percentage',
  '\GPU Process Memory(*)\Dedicated Usage',
  '\GPU Process Memory(*)\Shared Usage'
)

$sets = @(Get-Counter -Counter $counterPaths -SampleInterval 1 -MaxSamples 2)
$sample = if ($sets.Count) { $sets[-1] } else { $null }
$values = [ordered]@{}
$gpuByPid = @{}

if ($sample) {
  foreach ($counter in $sample.CounterSamples) {
    $path = $counter.Path.ToLowerInvariant()
    $value = [double]$counter.CookedValue
    if ($path -match '\\processor\(_total\)\\% processor time$') { $values.cpu_percent = $value }
    elseif ($path -match '\\system\\processor queue length$') { $values.cpu_queue = $value }
    elseif ($path -match '\\memory\\available mbytes$') { $values.ram_available_mb = $value }
    elseif ($path -match '\\memory\\committed bytes$') { $values.commit_bytes = $value }
    elseif ($path -match '\\memory\\commit limit$') { $values.commit_limit_bytes = $value }
    elseif ($path -match '\\memory\\pages/sec$') { $values.pages_per_sec = $value }
    elseif ($path -match '\\paging file\(_total\)\\% usage$') { $values.pagefile_percent = $value }
    elseif ($path -match '\\physicaldisk\(_total\)\\current disk queue length$') { $values.disk_queue = $value }
    elseif ($path -match '\\physicaldisk\(_total\)\\avg\. disk sec/read$') { $values.disk_read_ms = 1000 * $value }
    elseif ($path -match '\\physicaldisk\(_total\)\\avg\. disk sec/write$') { $values.disk_write_ms = 1000 * $value }
    elseif ($counter.InstanceName -match '^pid_(\d+)_') {
      $pidValue = [int]$matches[1]
      if (-not $gpuByPid.ContainsKey($pidValue)) {
        $gpuByPid[$pidValue] = [ordered]@{engine_percent=0.0; dedicated_bytes=0.0; shared_bytes=0.0}
      }
      if ($path -match '\\gpu engine') { $gpuByPid[$pidValue].engine_percent += $value }
      elseif ($path -match '\\dedicated usage$') { $gpuByPid[$pidValue].dedicated_bytes += $value }
      elseif ($path -match '\\shared usage$') { $gpuByPid[$pidValue].shared_bytes += $value }
    }
  }
}

$parentByPid = @{}
$processCounters = Get-Counter '\Process(*)\ID Process','\Process(*)\Creating Process ID' -MaxSamples 1
$processRows = @{}
foreach ($counter in $processCounters.CounterSamples) {
  $instance = $counter.Path -replace '^.*\\process\(([^)]*)\).*$','$1'
  if (-not $processRows.ContainsKey($instance)) {
    $processRows[$instance] = [ordered]@{pid=$null; ppid=$null}
  }
  if ($counter.Path -match '\\creating process id$') { $processRows[$instance].ppid = [int]$counter.CookedValue }
  elseif ($counter.Path -match '\\id process$') { $processRows[$instance].pid = [int]$counter.CookedValue }
}
foreach ($row in $processRows.Values) {
  if ($row.pid) { $parentByPid[$row.pid] = $row.ppid }
}

$wanted = '^(llama-server|ollama|python|claude|codex|codex-code-mode-host|chrome)$'
$processes = @()
foreach ($process in Get-Process) {
  if ($process.Name -notmatch $wanted) { continue }
  $started = $null
  $cpuSeconds = $null
  $workingSet = $null
  $privateBytes = $null
  try { $started = $process.StartTime.ToUniversalTime().ToString('o') } catch {}
  try { $cpuSeconds = [double]$process.CPU } catch {}
  try { $workingSet = [double]$process.WorkingSet64 } catch {}
  try { $privateBytes = [double]$process.PrivateMemorySize64 } catch {}
  $ppid = if ($parentByPid.ContainsKey($process.Id)) { $parentByPid[$process.Id] } else { $null }
  $parentAlive = if ($ppid) { [bool](Get-Process -Id $ppid -ErrorAction SilentlyContinue) } else { $false }
  $gpu = if ($gpuByPid.ContainsKey($process.Id)) { $gpuByPid[$process.Id] } else { $null }
  $processes += [ordered]@{
    name = $process.Name
    pid = $process.Id
    ppid = $ppid
    parent_alive = $parentAlive
    started_utc = $started
    cpu_seconds = $cpuSeconds
    working_set_bytes = $workingSet
    private_bytes = $privateBytes
    gpu_engine_percent = if ($gpu) { $gpu.engine_percent } else { 0.0 }
    gpu_dedicated_bytes = if ($gpu) { $gpu.dedicated_bytes } else { 0.0 }
    gpu_shared_bytes = if ($gpu) { $gpu.shared_bytes } else { 0.0 }
  }
}

$drive = [System.IO.DriveInfo]::new('C')
[ordered]@{
  sampled_utc = [DateTimeOffset]::UtcNow.ToString('o')
  logical_processors = [Environment]::ProcessorCount
  counters = $values
  disk = [ordered]@{total_bytes=$drive.TotalSize; free_bytes=$drive.AvailableFreeSpace}
  processes = $processes
} | ConvertTo-Json -Depth 7 -Compress
