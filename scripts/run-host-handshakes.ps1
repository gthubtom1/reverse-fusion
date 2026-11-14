param(
    [string]$Output = (Join-Path $PSScriptRoot '..\state\host-handshakes.json')
)

$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$outputPath = [IO.Path]::GetFullPath($Output)
New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($outputPath)) -Force | Out-Null

function Find-Executable([string[]]$Names) {
    foreach ($name in $Names) {
        $command = Get-Command $name -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($command) { return $command }
    }
    return $null
}

function Invoke-HostProbe([string]$Id, [string[]]$Names, [string[]]$Arguments, [string]$Sentinel) {
    $command = Find-Executable $Names
    if (-not $command) {
        return [ordered]@{
            id = $Id; status = 'unavailable'; executable = $null; version = $null
            exit_code = $null; sentinel = $Sentinel; observed = $false
            reason = 'executable not found'; config_mutation = $false
        }
    }
    $versionText = (& $command.Source --version 2>&1 | Out-String).Trim()
    $outputText = (& $command.Source @Arguments 2>&1 | Out-String).Trim()
    $exitCode = $LASTEXITCODE
    $observed = $outputText.Contains($Sentinel, [StringComparison]::Ordinal)
    $status = if ($observed -and $exitCode -eq 0) { 'pass' }
        elseif ($Id -eq 'claude' -and $outputText -match 'Not logged in|Please run /login') { 'blocked' }
        elseif ($exitCode -eq 0) { 'unknown' }
        else { 'failed' }
    $reason = if ($status -eq 'blocked') { 'Claude CLI started but has no active login or API credential on this host' }
        elseif ($status -eq 'pass') { 'non-interactive sentinel response observed' }
        else { 'sentinel response was not observed' }
    return [ordered]@{
        id = $Id; status = $status; executable = $command.Source; version = $versionText
        exit_code = $exitCode; sentinel = $Sentinel; observed = $observed; reason = $reason
        config_mutation = $false
        output_excerpt = if ($outputText.Length -gt 2000) { $outputText.Substring($outputText.Length - 2000) } else { $outputText }
    }
}

$probes = @(
    (Invoke-HostProbe 'codex' @('codex', 'codex.exe') @(
        'exec', '--ephemeral', '--sandbox', 'read-only', '--ignore-user-config', '--json',
        '--skip-git-repo-check', 'Reply with exactly RF_HOST_HANDSHAKE_CODEX and nothing else. Do not call tools or modify files.'
    ) 'RF_HOST_HANDSHAKE_CODEX'),
    (Invoke-HostProbe 'pi' @('pi', 'pi.cmd', 'pi.ps1') @(
        '--print', '--mode', 'json', '--no-session', '--no-tools', '--no-mcp',
        'Reply with exactly RF_HOST_HANDSHAKE_PI and nothing else. Do not call tools or modify files.'
    ) 'RF_HOST_HANDSHAKE_PI'),
    (Invoke-HostProbe 'claude' @('claude', 'claude.cmd', 'claude.ps1') @(
        '-p', 'Reply with exactly RF_HOST_HANDSHAKE_CLAUDE and nothing else. Do not call tools or modify files.',
        '--bare', '--no-session-persistence', '--tools', '', '--permission-mode', 'plan',
        '--output-format', 'json', '--max-budget-usd', '0.05'
    ) 'RF_HOST_HANDSHAKE_CLAUDE')
)

$result = [ordered]@{
    schema_version = 1
    operation = 'host-handshakes'
    generated_at = (Get-Date).ToUniversalTime().ToString('o')
    working_directory = $repo
    config_mutation = $false
    probes = @($probes)
}
$result | ConvertTo-Json -Depth 10 | Out-File -LiteralPath $outputPath -Encoding utf8
Write-Output ($result | ConvertTo-Json -Depth 10 -Compress)
