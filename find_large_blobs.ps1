$bigObjects = git rev-list --objects --all | ForEach-Object {
    $parts = $_.Split(' ', 2)
    $hash = $parts[0]
    $path = if ($parts.Length -gt 1) { $parts[1] } else { "no-path" }
    
    # Check size only if we have a path (optimizing)
    if ($path -ne "no-path") {
        $size = git cat-file -s $hash
        if ($size -gt 50MB) {
            [PSCustomObject]@{ Hash = $hash; Path = $path; SizeMB = "{0:N2}" -f ([long]$size / 1MB) }
        }
    }
} 

$bigObjects | Sort-Object { [double]$_.SizeMB } -Descending | Select-Object -First 20 | Format-Table -AutoSize
