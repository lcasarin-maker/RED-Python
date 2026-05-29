## rename-project.ps1
# -------------------------------------------------
# Bulk‑replace legacy project name and version strings
# -------------------------------------------------
# Set $DryRun = $true for a preview (no files will be written).
$DryRun = $false

# Define the replacement pairs
$replacements = @(
    @{ Pattern = '(?i)VibeCoderProof';    Replacement = 'CoderCerberus' }
    @{ Pattern = '(?i)\bv5\.7\b';      Replacement = 'v0.02' }
    @{ Pattern = '(?i)\bv5\.0\b';      Replacement = 'v0.02' }
    @{ Pattern = '(?i)\b5\.0\b';       Replacement = 'v0.02' }
    @{ Pattern = '(?i)\.vibecoderproof'; Replacement = 'deprecated/.vibecoderproof' }
)

# Walk through all relevant text files in the repository
Get-ChildItem -Path $PSScriptRoot -Recurse -Include *.md,*.txt,*.py,*.yml,*.json -File |
    ForEach-Object {
        $path = $_.FullName
        $original = Get-Content $path -Raw
        $modified = $original
        foreach ($rep in $replacements) {
            $modified = $modified -replace $rep.Pattern, $rep.Replacement
        }
        if ($modified -ne $original) {
            if ($DryRun) {
                Write-Host "[DRY-RUN] WOULD MODIFY: $path"
            } else {
                Write-Host "[UPDATE] $path"
                Set-Content -Path $path -Value $modified -Force
            }
        }
    }

if ($DryRun) {
    Write-Host "Dry‑run completed – no files were changed."
} else {
    Write-Host "Rename completed."
}
