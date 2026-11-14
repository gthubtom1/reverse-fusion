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

function Get-ConfigSnapshot([string]$Id) {
    $userHome = [Environment]::GetFolderPath('UserProfile')
    $paths = @()
    if ($Id -eq 'codex') {
        $root = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $userHome '.codex' }
        $paths = @((Join-Path $root 'config.toml'), (Join-Path $root 'AGENTS.md'))
    } elseif ($Id -eq 'pi') {
        $root = if ($env:PI_CODING_AGENT_DIR) { $env:PI_CODING_AGENT_DIR } else { Join-Path $userHome '.pi\agent' }
        $paths = @((Join-Path $root 'settings.json'), (Join-Path $root 'mcp.json'), (Join-Path $root 'AGENTS.md'))
    } elseif ($Id -eq 'claude') {
        $root = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $userHome '.claude' }
        $paths = @((Join-Path $root 'settings.json'), (Join-Path $root 'config.json'), (Join-Path $userHome '.claude.json'))
    }
    $files = [ordered]@{}
    foreach ($path in $paths) {
        if (Test-Path -LiteralPath $path -PathType Leaf) {
            $files[$path] = (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToLowerInvariant()
        }
    }
    return [ordered]@{ status = 'observed'; known_paths = $paths; files = $files }
}

function Invoke-HostProbe([string]$Id, [string[]]$Names, [string[]]$Arguments, [string]$Sentinel) {
    $before = Get-ConfigSnapshot $Id
    $command = Find-Executable $Names
    if (-not $command) {
        $after = Get-ConfigSnapshot $Id
        return [ordered]@{
            id = $Id; status = 'unavailable'; executable = $null; version = $null
            exit_code = $null; sentinel = $Sentinel; observed = $false
            reason = 'executable not found'; config_mutation = ($before.files | ConvertTo-Json -Compress) -ne ($after.files | ConvertTo-Json -Compress)
            config_snapshot = [ordered]@{ before = $before; after = $after; status = 'observed' }
        }
    }
    $previousErrorAction = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        [string]$versionText = (& $command.Source --version 2>&1 | Out-String).Trim()
        [string]$outputText = (& $command.Source @Arguments 2>&1 | Out-String).Trim()
    } finally {
        $ErrorActionPreference = $previousErrorAction
    }
    $exitCode = $LASTEXITCODE
    $after = Get-ConfigSnapshot $Id
    $configChanged = ($before.files | ConvertTo-Json -Compress) -ne ($after.files | ConvertTo-Json -Compress)
    $observed = $outputText.IndexOf($Sentinel, [StringComparison]::Ordinal) -ge 0
    $status = if ($configChanged) { 'blocked' }
        elseif ($observed -and $exitCode -eq 0) { 'pass' }
        elseif ($Id -eq 'claude' -and $outputText -match 'Not logged in|Please run /login') { 'blocked' }
        elseif ($exitCode -eq 0) { 'unknown' }
        else { 'failed' }
    $reason = if ($configChanged) { 'known host configuration changed during probe' }
        elseif ($status -eq 'blocked') { 'Claude CLI started but has no active login or API credential on this host' }
        elseif ($status -eq 'pass') { 'non-interactive sentinel response observed' }
        else { 'sentinel response was not observed' }
    return [ordered]@{
        id = $Id; status = $status; executable = $command.Source; version = $versionText
        exit_code = $exitCode; sentinel = $Sentinel; observed = $observed; reason = $reason
        config_mutation = $configChanged
        config_snapshot = [ordered]@{ before = $before; after = $after; status = 'observed' }
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
    config_mutation = @($probes | Where-Object { $_.config_mutation -eq $true }).Count -gt 0
    probes = @($probes)
}
$result | ConvertTo-Json -Depth 10 | Out-File -LiteralPath $outputPath -Encoding utf8
Write-Output ($result | ConvertTo-Json -Depth 10 -Compress)
