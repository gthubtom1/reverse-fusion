if (-not ('ReverseFusionPath.Native' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.ComponentModel;
using System.Runtime.InteropServices;
using System.Text;
using Microsoft.Win32.SafeHandles;

namespace ReverseFusionPath {
    public static class Native {
        [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
        private static extern SafeFileHandle CreateFile(
            string name, uint access, uint share, IntPtr security,
            uint creation, uint flags, IntPtr template);

        [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
        private static extern uint GetFinalPathNameByHandle(
            SafeFileHandle handle, StringBuilder path, uint length, uint flags);

        public static string FinalPath(string path) {
            const uint ShareAll = 1u | 2u | 4u;
            const uint OpenExisting = 3u;
            const uint BackupSemantics = 0x02000000u;
            using (SafeFileHandle handle = CreateFile(path, 0, ShareAll, IntPtr.Zero,
                                                       OpenExisting, BackupSemantics, IntPtr.Zero)) {
                if (handle.IsInvalid) throw new Win32Exception(Marshal.GetLastWin32Error());
                StringBuilder buffer = new StringBuilder(32768);
                uint size = GetFinalPathNameByHandle(handle, buffer, (uint)buffer.Capacity, 0);
                if (size == 0 || size >= buffer.Capacity) {
                    throw new Win32Exception(Marshal.GetLastWin32Error());
                }
                string value = buffer.ToString();
                if (value.StartsWith(@"\\?\UNC\", StringComparison.OrdinalIgnoreCase)) {
                    return @"\\" + value.Substring(8);
                }
                if (value.StartsWith(@"\\?\", StringComparison.OrdinalIgnoreCase)) {
                    return value.Substring(4);
                }
                return value;
            }
        }
    }
}
'@
}

function Get-CanonicalPath([string]$Path) {
    $absolute = [IO.Path]::GetFullPath($Path)
    $probe = $absolute
    $suffix = New-Object 'System.Collections.Generic.List[string]'
    while (-not (Test-Path -LiteralPath $probe)) {
        $leaf = Split-Path -Leaf $probe
        if (-not $leaf) { throw "No existing ancestor for path: $absolute" }
        $suffix.Insert(0, $leaf)
        $parent = Split-Path -Parent $probe
        if ($parent -eq $probe) { throw "No existing ancestor for path: $absolute" }
        $probe = $parent
    }
    if ($env:OS -eq 'Windows_NT') {
        $resolved = [ReverseFusionPath.Native]::FinalPath($probe)
    } else {
        $resolved = (Resolve-Path -LiteralPath $probe).Path
    }
    foreach ($part in $suffix) { $resolved = Join-Path $resolved $part }
    return [IO.Path]::GetFullPath($resolved)
}

function Assert-RepositoryWritePath([string]$RepositoryRoot, [string]$Path) {
    $root = Get-CanonicalPath $RepositoryRoot
    $candidate = Get-CanonicalPath $Path
    $prefix = $root.TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
    if (-not $candidate.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Write path escapes the repository: $Path"
    }
    return $candidate
}

function Reset-OutputFile([string]$RepositoryRoot, [string]$Path) {
    $safe = Assert-RepositoryWritePath $RepositoryRoot $Path
    if (Test-Path -LiteralPath $safe) {
        if (-not (Test-Path -LiteralPath $safe -PathType Leaf)) { throw "Expected a file path: $safe" }
        Remove-Item -LiteralPath $safe -Force
    }
    return [DateTime]::UtcNow
}

function Assert-NativeExit([int]$ExitCode, [string]$Operation, [int[]]$Expected = @(0)) {
    if ($Expected -notcontains $ExitCode) {
        throw "$Operation returned exit code $ExitCode; expected $($Expected -join ',')"
    }
}

function Resolve-ReaNodePath([string]$RepositoryRoot, [string]$ExplicitPath) {
    if ($ExplicitPath) { return $ExplicitPath }
    $receiptPath = Join-Path $RepositoryRoot 'state/rea-runtime.json'
    if (Test-Path -LiteralPath $receiptPath -PathType Leaf) {
        try {
            $receipt = Get-Content -Raw -LiteralPath $receiptPath | ConvertFrom-Json
            if ($receipt.schema_version -eq 1 -and
                [IO.Path]::IsPathRooted($receipt.repository_root) -and
                (Get-CanonicalPath $receipt.repository_root) -eq (Get-CanonicalPath $RepositoryRoot) -and
                [IO.Path]::IsPathRooted($receipt.node) -and
                (Test-Path -LiteralPath $receipt.node -PathType Leaf)) {
                return [string]$receipt.node
            }
        } catch { }
    }
    return 'node'
}

function Read-FreshJson([string]$RepositoryRoot, [string]$Path, [DateTime]$StartedAt) {
    $safe = Assert-RepositoryWritePath $RepositoryRoot $Path
    if (-not (Test-Path -LiteralPath $safe -PathType Leaf)) { throw "Expected output was not created: $safe" }
    $item = Get-Item -LiteralPath $safe
    if ($item.Length -eq 0 -or $item.LastWriteTimeUtc -lt $StartedAt.AddSeconds(-2)) {
        throw "Expected output is empty or stale: $safe"
    }
    try { return Get-Content -Raw -LiteralPath $safe | ConvertFrom-Json }
    catch { throw "Expected output is not valid JSON: $safe ($($_.Exception.Message))" }
}

function Assert-ResultStatus($Value, [string[]]$Expected, [string]$Operation) {
    $status = if ($Value -and $Value.PSObject.Properties['status']) { [string]$Value.status } else { '' }
    if ($Expected -notcontains $status) {
        throw "$Operation returned status '$status'; expected $($Expected -join ',')"
    }
}
