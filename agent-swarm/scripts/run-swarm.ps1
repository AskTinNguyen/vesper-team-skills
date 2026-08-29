[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)] [ValidateSet('validate', 'run')] [string] $Action,
    [Parameter(Mandatory = $true)] [string] $Manifest,
    [string] $OutputDir,
    [switch] $DryRun,
    [switch] $AllowUnapproved
)

$ErrorActionPreference = 'Stop'
$scriptPath = Join-Path $PSScriptRoot 'swarm.py'
$arguments = @($scriptPath, $Action, '--manifest', $Manifest)
if ($OutputDir) { $arguments += @('--output-dir', $OutputDir) }
if ($DryRun) { $arguments += '--dry-run' }
if ($AllowUnapproved) { $arguments += '--allow-unapproved' }
& python @arguments
exit $LASTEXITCODE
