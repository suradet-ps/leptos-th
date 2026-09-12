param(
    [string]$Orig = '',
    [string]$Trans = (Join-Path $PSScriptRoot '..\src')
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$trans = [System.IO.Path]::GetFullPath($Trans)

if ([string]::IsNullOrWhiteSpace($Orig)) {
    $candidates = @(
        (Join-Path $PSScriptRoot '..\..\book\src'),
        (Join-Path $PSScriptRoot '..\upstream\src'),
        (Join-Path (Get-Location) 'upstream\src')
    )
    foreach ($cand in $candidates) {
        if (Test-Path -LiteralPath $cand) {
            $Orig = $cand
            break
        }
    }
}

if ([string]::IsNullOrWhiteSpace($Orig) -or (-not (Test-Path -LiteralPath $Orig))) {
    Write-Error "Cannot find upstream leptos-rs/book src directory.`nPlease provide the path using: ./scripts/verify-translation.ps1 -Orig <path-to-book/src>"
    exit 1
}

$orig = [System.IO.Path]::GetFullPath($Orig)
Write-Output "Comparing translation against upstream:"
Write-Output "  Upstream:    $orig"
Write-Output "  Translation: $trans"

function Read-Normalized($path) {
    return ([System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)).Replace("`r`n", "`n")
}

# Parses fenced blocks. Admonish containers hold translated prose, so only the
# directive kind is compared for them; fenced code nested inside them is still
# compared byte-exact.
function Parse-Blocks($content, $codeBlocks, $admonishKinds) {
    $lines = $content -split "`n"
    $i = 0
    while ($i -lt $lines.Count) {
        $line = $lines[$i]
        if ($line -match '^\s{0,3}(`{3,})(.*)$') {
            $fenceLen = $Matches[1].Length
            $info = $Matches[2].Trim()
            $bodyLines = New-Object System.Collections.Generic.List[string]
            $i++
            while ($i -lt $lines.Count) {
                $l = $lines[$i]
                if ($l -match '^\s{0,3}(`{3,})\s*$' -and $Matches[1].Length -ge $fenceLen) { break }
                $bodyLines.Add($l)
                $i++
            }
            $body = ($bodyLines -join "`n")
            $tokens = @($info -split '\s+' | Where-Object { $_ -ne '' })
            $first = if ($tokens.Count -gt 0) { $tokens[0] } else { '' }
            if ($first -eq 'admonish' -or $first -eq 'sandbox') {
                $kind = if ($tokens.Count -gt 1) { "$($tokens[0]) $($tokens[1])" } else { $tokens[0] }
                $admonishKinds.Add($kind)
                Parse-Blocks $body $codeBlocks $admonishKinds
            } else {
                $codeBlocks.Add([PSCustomObject]@{ Info = $info; Body = $body })
            }
        }
        $i++
    }
}

function Get-CodeBlocks($path) {
    $blocks = New-Object System.Collections.Generic.List[object]
    $kinds = New-Object System.Collections.Generic.List[string]
    Parse-Blocks (Read-Normalized $path) $blocks $kinds
    return ,$blocks
}

function Get-AdmonishKinds($path) {
    $blocks = New-Object System.Collections.Generic.List[object]
    $kinds = New-Object System.Collections.Generic.List[string]
    Parse-Blocks (Read-Normalized $path) $blocks $kinds
    return ,$kinds
}

function Get-Headings($path) {
    $content = Read-Normalized $path
    $rx = [regex]'(?m)^#{1,6} .*$'
    return @($rx.Matches($content) | ForEach-Object { $_.Value })
}

function Get-RefLinks($path) {
    $content = Read-Normalized $path
    $rx = [regex]'(?m)^\[[^\]]+\]:\s+\S+.*$'
    return @($rx.Matches($content) | ForEach-Object { $_.Value -replace '\s+$','' })
}

function Get-InlineLinkTargets($path) {
    $content = Read-Normalized $path
    $rx = [regex]'\[[^\]]*\]\(([^)]+)\)'
    return @($rx.Matches($content) | ForEach-Object { $_.Groups[1].Value -replace '\s+$','' })
}

function Normalize-LinkTarget($url) {
    if ([string]::IsNullOrWhiteSpace($url)) {
        return ''
    }
    $trimmed = $url.Trim()
    # In-page anchor link (anchors are translated to Thai slugs and checked by check-links.ps1)
    if ($trimmed.StartsWith('#')) {
        return '#anchor'
    }
    # File link with in-page anchor (e.g. usage.md#regression-check vs usage.md#การตรวจสอบรีเกรสชัน)
    if ($trimmed -match '^([^#]+)#(.+)$') {
        return $Matches[1]
    }
    return $trimmed
}

$origFiles = Get-ChildItem -Recurse -File $orig -Filter *.md
$fail = 0
$total = 0

foreach ($f in $origFiles) {
    $rel = $f.FullName.Substring($orig.Length + 1)
    $tPath = Join-Path $trans $rel
    $total++
    if (-not (Test-Path -LiteralPath $tPath)) {
        Write-Output "[FAIL] $rel : missing translated file"
        $fail++
        continue
    }

    $oc = Get-CodeBlocks $f.FullName
    $tc = Get-CodeBlocks $tPath
    if ($oc.Count -ne $tc.Count) {
        Write-Output "[FAIL] $rel : code block count differs (orig=$($oc.Count) trans=$($tc.Count))"
        $fail++
    } else {
        for ($i = 0; $i -lt $oc.Count; $i++) {
            if ($oc[$i].Info -cne $tc[$i].Info) {
                Write-Output "[FAIL] $rel : code block #$($i+1) info differs (orig='$($oc[$i].Info)' trans='$($tc[$i].Info)')"
                $fail++
            } elseif ($oc[$i].Body -cne $tc[$i].Body) {
                Write-Output "[FAIL] $rel : code block #$($i+1) differs"
                $fail++
            }
        }
    }

    $ok = Get-AdmonishKinds $f.FullName
    $tk = Get-AdmonishKinds $tPath
    if ($ok.Count -ne $tk.Count) {
        Write-Output "[FAIL] $rel : admonish block count differs (orig=$($ok.Count) trans=$($tk.Count))"
        $fail++
    } else {
        for ($i = 0; $i -lt $ok.Count; $i++) {
            if ($ok[$i] -cne $tk[$i]) {
                Write-Output "[FAIL] $rel : admonish block #$($i+1) kind differs (orig='$($ok[$i])' trans='$($tk[$i])')"
                $fail++
            }
        }
    }

    $oh = Get-Headings $f.FullName
    $th = Get-Headings $tPath
    if ($oh.Count -ne $th.Count) {
        Write-Output "[FAIL] $rel : heading count differs (orig=$($oh.Count) trans=$($th.Count))"
        $fail++
    } else {
        for ($i = 0; $i -lt $oh.Count; $i++) {
            $ol = ($oh[$i] -split ' ')[0]
            $tl = ($th[$i] -split ' ')[0]
            if ($ol -cne $tl) {
                Write-Output "[FAIL] $rel : heading #$($i+1) level differs (orig='$($oh[$i])' trans='$($th[$i])')"
                $fail++
            }
        }
    }

    $or = Get-RefLinks $f.FullName
    $tr = Get-RefLinks $tPath
    if ($or.Count -ne $tr.Count) {
        Write-Output "[FAIL] $rel : ref-link count differs (orig=$($or.Count) trans=$($tr.Count))"
        $fail++
    } else {
        for ($i = 0; $i -lt $or.Count; $i++) {
            $ourl = Normalize-LinkTarget (($or[$i] -split ':\s*',2)[1])
            $turl = Normalize-LinkTarget (($tr[$i] -split ':\s*',2)[1])
            if ($ourl -cne $turl) {
                Write-Output "[FAIL] $rel : ref-link #$($i+1) url differs (orig='$ourl' trans='$turl')"
                $fail++
            }
        }
    }

    $oi = @(Get-InlineLinkTargets $f.FullName | ForEach-Object { Normalize-LinkTarget $_ })
    $ti = @(Get-InlineLinkTargets $tPath | ForEach-Object { Normalize-LinkTarget $_ })
    $os = $oi | Sort-Object -Unique
    $ts = $ti | Sort-Object -Unique
    $missing = @($os | Where-Object { $_ -notin $ts })
    $extra = @($ts | Where-Object { $_ -notin $os })
    if ($missing.Count -gt 0 -or $extra.Count -gt 0) {
        Write-Output "[FAIL] $rel : inline link targets differ (missing=[$($missing -join ', ')] extra=[$($extra -join ', ')])"
        $fail++
    }
}

Write-Output "---"
Write-Output "Checked $total files, $fail problem(s)"
if ($fail -eq 0) { Write-Output "ALL OK: code blocks, admonish blocks, headings, links match 100%" }
exit ($fail -gt 0)
