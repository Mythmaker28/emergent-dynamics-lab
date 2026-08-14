# Reassemble the ORR01 self-contained repository from its parts and verify it (Windows).
#   powershell -ExecutionPolicy Bypass -File reassemble_and_verify.ps1 [-Out <dir>]
param([string]$Out = "$PWD\csc01_offline")
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
New-Item -ItemType Directory -Force -Path $Out | Out-Null
$parts = Get-ChildItem "$here\CSC01_OFFLINE_REPO.tar.gz.part*" | Sort-Object Name
Write-Host "== reassembling from $($parts.Count) parts"
$dst = Join-Path $Out "CSC01_OFFLINE_REPO.tar.gz"
if (Test-Path $dst) { Remove-Item $dst }
$fs = [System.IO.File]::Create($dst)
foreach ($p in $parts) { $b = [System.IO.File]::ReadAllBytes($p.FullName); $fs.Write($b, 0, $b.Length) }
$fs.Close()
$expected = (Select-String -Path "$here\CSC01_OFFLINE_REPO.SHA256SUMS" -Pattern 'reassembled whole').Line.Split(' ')[0]
$got = (Get-FileHash $dst -Algorithm SHA256).Hash.ToLower()
if ($got -eq $expected) { Write-Host "   OK  $got" } else { Write-Host "   MISMATCH expected $expected got $got"; exit 1 }
Write-Host "== extracting"
tar xzf $dst -C $Out
Write-Host "bare repository at $Out\bare4"
Write-Host "Then, with git available:  git -c protocol.file.allow=always clone $Out\bare4 $Out\wc ; git -C $Out\wc checkout d89c2217697c33cfb66a6878b885442f13b19c57"
