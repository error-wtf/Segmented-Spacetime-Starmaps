# Simple Stellaris Cleanup
Write-Host "Stellaris Cleanup Starting..."

$files = Get-ChildItem -Recurse -Include *.md,*.py,*.txt -File | Where-Object { $_.FullName -notmatch '\\\.git\\' -and $_.FullName -notmatch '\\\.venv\\' }

$changed = 0
foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
    if ($content) {
        $new = $content
        $new = $new -replace 'Stellaris', 'Interactive3D'
        $new = $new -replace 'stellaris', 'interactive3d'
        $new = $new -replace 'STELLARIS', 'INTERACTIVE3D'
        
        if ($new -ne $content) {
            $new | Set-Content $file.FullName -Encoding UTF8 -NoNewline
            $changed++
            Write-Host "Updated: $($file.Name)"
        }
    }
}

Write-Host "Done! Files changed: $changed"
