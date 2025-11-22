# Cleanup Script: Remove all "Stellaris" references
# © 2025 Carmen Wrede, Lino Casu

Write-Host "🔧 Stellaris Cleanup Script" -ForegroundColor Cyan
Write-Host "=" * 60

$replacements = @{
    'Stellaris'                 = 'Interactive3D'
    'stellaris'                 = 'interactive3d'
    'STELLARIS'                 = 'INTERACTIVE3D'
    'Stellaris-style'           = 'Interactive 3D style'
    'stellaris-style'           = 'interactive 3D style'
    'SSZ Stellaris Viewer'      = 'SSZ Explorer'
    'SSZ Stellaris'             = 'SSZ Interactive3D'
    'Stellaris Viewer'          = 'Interactive3D Viewer'
    'Stellaris Sky Map'         = 'Interactive Sky Map'
    'Stellaris Edition'         = 'Interactive Edition'
}

# Get all text files (md, py, txt, ps1, sh, json, yaml)
$files = Get-ChildItem -Recurse -Include *.md,*.py,*.txt,*.ps1,*.sh,*.json,*.yaml,*.toml,*.cfg -File |
    Where-Object { $_.FullName -notmatch '\\\.git\\' -and $_.FullName -notmatch '\\\.venv\\' -and $_.FullName -notmatch '__pycache__' }

$count = 0
$filesChanged = 0

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    $originalContent = $content
    $changed = $false
    
    foreach ($key in $replacements.Keys) {
        if ($content -match [regex]::Escape($key)) {
            $content = $content -replace [regex]::Escape($key), $replacements[$key]
            $changed = $true
            $count++
        }
    }
    
    if ($changed) {
        $content | Set-Content -Path $file.FullName -Encoding UTF8 -NoNewline
        $filesChanged++
        Write-Host "Updated: $($file.Name)"
    }
}

Write-Host ""
Write-Host "=" * 60
Write-Host "✅ Cleanup Complete!" -ForegroundColor Green
Write-Host "   Files changed: $filesChanged" -ForegroundColor Yellow
Write-Host "   Replacements made: $count" -ForegroundColor Yellow
Write-Host "=" * 60
