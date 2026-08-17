param(
    [Parameter(Mandatory = $true)][string]$Url,
    [string]$OutFile = ""
)

# Fetch article HTML via the escalated network channel and extract <p> text.
# Usage:
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File fetch_article.ps1 "<article-url>"
$ErrorActionPreference = "Stop"

if (-not $OutFile) {
    $OutFile = Join-Path $env:TEMP ("article_" + [guid]::NewGuid().ToString("N") + ".html")
}

curl.exe -sk -L -o $OutFile --max-time 90 $Url
if ($LASTEXITCODE -ne 0 -or -not (Test-Path $OutFile)) {
    Write-Error "FETCH_FAILED url=$Url"
    exit 1
}

$raw = Get-Content $OutFile -Raw -Encoding UTF8

$title = ""
$m = [regex]::Match($raw, '<title[^>]*>(.*?)</title>', 'Singleline')
if ($m.Success) {
    $title = ($m.Groups[1].Value -replace '\s+', ' ').Trim()
}

# Prefer paragraphs inside <article>; fall back to all <p> tags.
$body = $raw
$am = [regex]::Match($raw, '<article[^>]*>(.*?)</article>', 'Singleline')
if ($am.Success) {
    $body = $am.Groups[1].Value
}

$paras = [regex]::Matches($body, '<p[^>]*>(.*?)</p>', 'Singleline') | ForEach-Object {
    ($_.Groups[1].Value -replace '<[^>]+>', ' ' -replace '&[a-z]+;', ' ' -replace '&#\d+;', ' ' -replace '\s+', ' ').Trim()
} | Where-Object { $_.Length -gt 40 }

$text = $paras -join "`n"
$words = @($text -split '\s+' | Where-Object { $_ }).Count

Write-Output ("TITLE: " + $title)
Write-Output ("URL: " + $Url)
Write-Output ("SAVED: " + $OutFile)
Write-Output ("PARA_COUNT: " + $paras.Count)
Write-Output ("WORDS: " + $words)
Write-Output "---TEXT_START---"
Write-Output $text
Write-Output "---TEXT_END---"
