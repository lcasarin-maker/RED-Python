Get-ChildItem -Path 'D:/GoogleDrive/AI/Cerberus' -Recurse -Include *.md,*.txt,*.py,*.yml,*.json -File |
    ForEach-Object {
        $content = Get-Content $_.FullName -Raw
        $new = $content -replace '(?i)VibeCoderProof','CoderCerberus' \
                     -replace '(?i)v5\.7','v0.02' \
                     -replace '(?i)v5\.0','v0.02' \
                     -replace '(?i)\b5\.0\b','v0.02' \
                     -replace '(?i)\.vibecoderproof','deprecated/.vibecoderproof'
        if ($new -ne $content) {
            Set-Content -Path $_.FullName -Value $new -Force
        }
    }
