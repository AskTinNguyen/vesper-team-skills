param([string]$RunDir = "h3chain_run", [int]$Port = 8321, [int]$Total = 40)
$py = "C:\ComfyUI-H3\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }
$script = Join-Path $PSScriptRoot "tracker_server.py"
Start-Process -FilePath $py -ArgumentList @($script, "--run-dir", $RunDir, "--port", "$Port", "--total", "$Total") -WorkingDirectory (Get-Location) -WindowStyle Hidden
Write-Output "tracker starting on http://127.0.0.1:$Port (run-dir $RunDir)"