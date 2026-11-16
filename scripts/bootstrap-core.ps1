param([string]$NodePath = $env:REVERSE_FUSION_NODE)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'lib/ScriptSupport.ps1')
$repo = Get-CanonicalPath (Join-Path $PSScriptRoot '..')
$selectedNode = Resolve-ReaNodePath $repo $NodePath
if (-not $NodePath) {
    $nodeSupported = $false
    try {
        $text = (& $selectedNode --version | Out-String).Trim()
        if ($LASTEXITCODE -eq 0 -and $text -match '^v(\d+)\.(\d+)\.(\d+)$') {
            $v = [version]($text.Substring(1))
            $nodeSupported = ($v.Major -eq 22 -and $v -ge [version]'22.23.4') -or ($v.Major -eq 24 -and $v -ge [version]'24.22.1') -or $v -ge [version]'26.12.1'
        }
    } catch { }
    if (-not $nodeSupported) {
        $nodeRuntime = & powershell -NoProfile -File (Join-Path $PSScriptRoot 'bootstrap-node.ps1') | ConvertFrom-Json
        Assert-NativeExit $LASTEXITCODE 'Repository-local compatible Node'
        $selectedNode = $nodeRuntime.node
    }
}
# Core components are required at deployment. Target-specific IDA/JADX/Frida/
# device and model/account setup are separate and are never inferred here.
& powershell -NoProfile -File (Join-Path $PSScriptRoot 'bootstrap-rea.ps1') -NodePath $selectedNode
Assert-NativeExit $LASTEXITCODE 'Required REA installation'
& powershell -NoProfile -File (Join-Path $PSScriptRoot 'bootstrap-spec.ps1')
Assert-NativeExit $LASTEXITCODE 'Required Spec installation'
& powershell -NoProfile -File (Join-Path $PSScriptRoot 'bootstrap-craft.ps1')
Assert-NativeExit $LASTEXITCODE 'Required native Craft installation'
& powershell -NoProfile -File (Join-Path $PSScriptRoot 'bootstrap-craft-mcp.ps1')
Assert-NativeExit $LASTEXITCODE 'Required full Craft MCP installation'
& powershell -NoProfile -File (Join-Path $PSScriptRoot 'run-rea-doctor.ps1')
Assert-NativeExit $LASTEXITCODE 'Required REA live diagnosis'
& (Join-Path $repo '.venv/Scripts/python.exe') -m reverse_fusion native-craft capabilities --format json
Assert-NativeExit $LASTEXITCODE 'Required Craft live identity'
Write-Output '{"core_deployment":"installed","business_acceptance":"not-performed"}'
