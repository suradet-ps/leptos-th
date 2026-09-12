param(
    [string]$BookDir = (Join-Path $PSScriptRoot '..\book')
)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$book = [System.IO.Path]::GetFullPath($BookDir)

$files = Get-ChildItem -Recurse -File $book -Filter *.html
$broken = @()
$total = 0

foreach ($f in $files) {
    $content = [System.IO.File]::ReadAllText($f.FullName)
    $ids = @{}
    foreach ($m in [regex]::Matches($content, 'id="([^"]+)"')) { $ids[$m.Groups[1].Value] = $true }

    $rel = $f.FullName.Substring($book.Length + 1).Replace('\','/')
    foreach ($m in [regex]::Matches($content, 'href="([^"]*)"')) {
        $href = $m.Groups[1].Value
        if ($href -like 'http*' -or $href -like 'javascript*' -or $href -eq '') { continue }
        if ($href.StartsWith('#')) {
            $total++
            $target = [System.Uri]::UnescapeDataString($href.Substring(1))
            if (-not $ids.ContainsKey($target)) {
                $broken += "$rel -> #$target (id not found)"
            }
        } elseif ($href -like '*.html*' -or $href -like '*print.html*') {
            $page = ($href -split '[?#]')[0]
            $resolvedPath = Split-Path $f.FullName -Parent
            foreach ($segment in ($page -split '/')) {
                $resolvedPath = Join-Path $resolvedPath $segment
            }
            $resolved = [System.IO.Path]::GetFullPath($resolvedPath)
            if (-not (Test-Path -LiteralPath $resolved)) {
                $broken += "$rel -> $href (file missing)"
                continue
            }
            if ($href -match '#(.+)$') {
                $total++
                $target = [System.Uri]::UnescapeDataString($Matches[1])
                $pContent = [System.IO.File]::ReadAllText($resolved)
                if ($pContent -notmatch 'id="' + [regex]::Escape($target) + '"') {
                    $broken += "$rel -> $href (anchor not found in target)"
                }
            }
        }
    }
}

Write-Output "Checked $total anchor links"
if ($broken.Count -eq 0) { Write-Output "ALL ANCHOR LINKS OK" }
else { $broken | ForEach-Object { Write-Output "[BROKEN] $_" } }
