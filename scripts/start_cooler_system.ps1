$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$frontendRoot = Join-Path $projectRoot "frontend"
$backendPort = 8010
$frontendPort = 5173
$powershellExe = (Get-Command powershell.exe -ErrorAction Stop).Source

function Resolve-PythonCommand {
    $venvCandidates = @(
        (Join-Path $projectRoot ".venv\Scripts\python.exe"),
        (Join-Path $projectRoot "venv\Scripts\python.exe"),
        (Join-Path $projectRoot "env\Scripts\python.exe")
    )

    foreach ($candidate in $venvCandidates) {
        if (Test-Path $candidate) {
            return @{
                Executable = $candidate
                PrefixArgs = @()
            }
        }
    }

    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) {
        return @{
            Executable = $pythonCommand.Source
            PrefixArgs = @()
        }
    }

    $pyCommand = Get-Command py -ErrorAction SilentlyContinue
    if ($pyCommand) {
        return @{
            Executable = $pyCommand.Source
            PrefixArgs = @("-3")
        }
    }

    throw "Python 3.11+ was not found."
}

function Resolve-NpmExe {
    $npmCmd = Get-Command npm.cmd -ErrorAction SilentlyContinue
    if ($npmCmd) {
        return $npmCmd.Source
    }

    $npm = Get-Command npm -ErrorAction SilentlyContinue
    if ($npm) {
        return $npm.Source
    }

    throw "npm was not found. Please install Node.js 18+."
}

$pythonCommand = Resolve-PythonCommand
$npmExe = Resolve-NpmExe

if (-not (Test-Path $frontendRoot)) {
    throw "Frontend directory was not found: $frontendRoot"
}

if ($pythonCommand.PrefixArgs.Count -gt 0) {
    $pythonInvocation = "& '$($pythonCommand.Executable)' $($pythonCommand.PrefixArgs -join ' ')"
} else {
    $pythonInvocation = "& '$($pythonCommand.Executable)'"
}

$backendCommand = @"
`$Host.UI.RawUI.WindowTitle = 'Cooler System - Backend'
Set-Location -LiteralPath '$projectRoot'
$pythonInvocation -m uvicorn backend.app:app --host 127.0.0.1 --port $backendPort
"@

$frontendCommand = @"
`$Host.UI.RawUI.WindowTitle = 'Cooler System - Frontend'
Set-Location -LiteralPath '$frontendRoot'
& '$npmExe' run dev
"@

Start-Process -FilePath $powershellExe -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy",
    "Bypass",
    "-Command",
    $backendCommand
)

Start-Sleep -Seconds 2

Start-Process -FilePath $powershellExe -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy",
    "Bypass",
    "-Command",
    $frontendCommand
)

Start-Sleep -Seconds 4
Start-Process "http://127.0.0.1:$frontendPort"
