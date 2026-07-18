[CmdletBinding(DefaultParameterSetName = 'Detached')]
param(
    [Parameter(Mandatory = $true)]
    [string]$Path,

    [Parameter(Mandatory = $true)]
    [string]$Commitish,

    [string]$Repository = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path,

    [Parameter(ParameterSetName = 'Branch')]
    [ValidateNotNullOrEmpty()]
    [string]$Branch
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)]
        [string]$WorkingDirectory,

        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    $savedErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $output = @(& git -C $WorkingDirectory @Arguments 2>&1)
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $savedErrorActionPreference
    }
    if ($exitCode -ne 0) {
        $detail = $output -join [Environment]::NewLine
        throw "git $($Arguments -join ' ') failed in $WorkingDirectory with exit code $exitCode.$([Environment]::NewLine)$detail"
    }
    return @($output | ForEach-Object { $_.ToString() })
}

function Test-WindowsInvalidGitPath {
    param([Parameter(Mandatory = $true)][string]$GitPath)

    foreach ($segment in $GitPath.Split('/')) {
        if ($segment.Length -eq 0 -or $segment -eq '.' -or $segment -eq '..') {
            return $true
        }
        if ($segment -match '[<>:"\\|?*\x00-\x1f]') {
            return $true
        }
        if ($segment.EndsWith(' ') -or $segment.EndsWith('.')) {
            return $true
        }

        $stem = $segment.Split('.')[0].ToUpperInvariant()
        if ($stem -match '^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$') {
            return $true
        }
    }
    return $false
}

function ConvertTo-SparseLiteral {
    param([Parameter(Mandatory = $true)][string]$GitPath)

    $escaped = $GitPath.Replace('\\', '\\\\')
    $escaped = $escaped.Replace('*', '\\*')
    $escaped = $escaped.Replace('?', '\\?')
    $escaped = $escaped.Replace('[', '\\[')
    return $escaped
}

$repositoryPath = (Resolve-Path -LiteralPath $Repository).Path
$targetPath = [IO.Path]::GetFullPath($Path)

if (Test-Path -LiteralPath $targetPath) {
    throw "Refusing to overwrite existing path: $targetPath"
}

$registeredPaths = @(
    Invoke-Git -WorkingDirectory $repositoryPath -Arguments @('worktree', 'list', '--porcelain') |
        Where-Object { $_.StartsWith('worktree ') } |
        ForEach-Object { [IO.Path]::GetFullPath($_.Substring(9)) }
)
if ($registeredPaths.Where({ $_.Equals($targetPath, [StringComparison]::OrdinalIgnoreCase) }).Count -gt 0) {
    throw "Refusing registered worktree path even though its directory is absent: $targetPath"
}

$resolvedCommit = (@(Invoke-Git -WorkingDirectory $repositoryPath -Arguments @('rev-parse', '--verify', "$Commitish^{commit}")))[-1].Trim()
$expectedTree = (@(Invoke-Git -WorkingDirectory $repositoryPath -Arguments @('rev-parse', "$resolvedCommit^{tree}")))[-1].Trim()
$treePaths = @(Invoke-Git -WorkingDirectory $repositoryPath -Arguments @('-c', 'core.quotepath=false', 'ls-tree', '-r', '--name-only', $resolvedCommit))
$invalidPaths = @($treePaths | Where-Object { Test-WindowsInvalidGitPath -GitPath $_ } | Sort-Object -Unique)
$outsideDocumentedCache = @($invalidPaths | Where-Object { -not $_.StartsWith('results/_tomo_cache/', [StringComparison]::Ordinal) })

if ($outsideDocumentedCache.Count -gt 0) {
    throw "Refusing commit with undocumented Windows-invalid paths outside results/_tomo_cache/: $($outsideDocumentedCache -join ', ')"
}

if ($PSCmdlet.ParameterSetName -eq 'Branch') {
    [void](Invoke-Git -WorkingDirectory $repositoryPath -Arguments @('check-ref-format', '--branch', $Branch))
    $branchProbe = @(& git -C $repositoryPath show-ref --verify --quiet "refs/heads/$Branch" 2>&1)
    if ($LASTEXITCODE -eq 0) {
        throw "Refusing to overwrite existing branch: $Branch"
    }
    if ($LASTEXITCODE -ne 1) {
        throw "Unable to verify whether branch already exists: $Branch. $($branchProbe -join ' ')"
    }
    [void](Invoke-Git -WorkingDirectory $repositoryPath -Arguments @('worktree', 'add', '--no-checkout', '-b', $Branch, $targetPath, $resolvedCommit))
} else {
    [void](Invoke-Git -WorkingDirectory $repositoryPath -Arguments @('worktree', 'add', '--no-checkout', '--detach', $targetPath, $resolvedCommit))
}

try {
    [void](Invoke-Git -WorkingDirectory $targetPath -Arguments @('sparse-checkout', 'init', '--no-cone'))
    $patterns = @('/*') + @($invalidPaths | ForEach-Object { '!/' + (ConvertTo-SparseLiteral -GitPath $_) })
    $patternOutput = @($patterns | & git -C $targetPath sparse-checkout set --no-cone --stdin 2>&1)
    if ($LASTEXITCODE -ne 0) {
        throw "git sparse-checkout set failed with exit code $LASTEXITCODE.$([Environment]::NewLine)$($patternOutput -join [Environment]::NewLine)"
    }

    [void](Invoke-Git -WorkingDirectory $targetPath -Arguments @('-c', 'core.protectNTFS=false', 'checkout', '--quiet'))

    $actualHead = (@(Invoke-Git -WorkingDirectory $targetPath -Arguments @('rev-parse', 'HEAD')))[-1].Trim()
    if ($actualHead -ne $resolvedCommit) {
        throw "HEAD mismatch: expected $resolvedCommit, got $actualHead"
    }

    $actualTree = (@(Invoke-Git -WorkingDirectory $targetPath -Arguments @('write-tree')))[-1].Trim()
    if ($actualTree -ne $expectedTree) {
        throw "Index tree mismatch: expected $expectedTree, got $actualTree"
    }

    $skippedPaths = @(
        Invoke-Git -WorkingDirectory $targetPath -Arguments @('-c', 'core.quotepath=false', 'ls-files', '-v') |
            Where-Object { $_.StartsWith('S ') } |
            ForEach-Object { $_.Substring(2) } |
            Sort-Object -Unique
    )
    if (($skippedPaths -join [char]0) -ne ($invalidPaths -join [char]0)) {
        throw "Sparse exclusion mismatch. Expected [$($invalidPaths -join ', ')], got [$($skippedPaths -join ', ')]"
    }

    $status = @(Invoke-Git -WorkingDirectory $targetPath -Arguments @('status', '--porcelain=v1', '--untracked-files=all'))
    if ($status.Count -ne 0) {
        throw "New worktree is not clean: $($status -join '; ')"
    }
} catch {
    Write-Error "Worktree construction failed after registration. It was left in place for diagnosis: $targetPath. $($_.Exception.Message)"
    throw
}

Write-Output "CREATED_WINDOWS_SAFE_WORKTREE"
Write-Output "path=$targetPath"
Write-Output "commit=$resolvedCommit"
Write-Output "tree=$expectedTree"
Write-Output "excluded_invalid_paths=$($invalidPaths.Count)"
