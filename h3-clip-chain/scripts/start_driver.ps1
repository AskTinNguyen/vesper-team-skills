param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Forward)
$py = "C:\ComfyUI-H3\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }
$script = Join-Path $PSScriptRoot "chain_driver.py"
$work = Get-Location
$log = Join-Path $work "driver.out.log"
$err = Join-Path $work "driver.err.log"
$argList = @($script) + $Forward
Start-Process -FilePath $py -ArgumentList $argList -WorkingDirectory $work -WindowStyle Hidden -RedirectStandardOutput $log -RedirectStandardError $err
Write-Output "chain driver started (hidden). logs: $log"