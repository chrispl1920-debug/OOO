param(
    [Parameter(Mandatory = $true)][string]$GhidraHome,
    [string]$Image
)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$version = '0.36.5552'
if (-not $Image) { $Image = Join-Path $repoRoot "build/$version/OutOfOre.analysis.exe" }
$imageFile = (Resolve-Path -LiteralPath $Image).Path
$projectDir = Join-Path $repoRoot "build/$version/ghidra"
$outputDir = Join-Path $repoRoot "build/$version/decompiled"
New-Item -ItemType Directory -Force -Path $projectDir, $outputDir | Out-Null
$imageHash = (Get-FileHash -LiteralPath $imageFile -Algorithm SHA256).Hash.Substring(0, 12)
$projectName = "OOO_0_36_5552_$imageHash"
$headless = Join-Path $GhidraHome 'support/analyzeHeadless.bat'
if (-not (Test-Path -LiteralPath $headless)) { throw 'Ghidra analyzeHeadless.bat was not found' }
$manifest = Get-Content -Raw -LiteralPath (Join-Path $repoRoot "config/$version.json") | ConvertFrom-Json
$selections = @($manifest.analysis_functions | ForEach-Object { "$($_.name):$($_.rva):$($_.size)" })
$ghidraArgs = @($projectDir, $projectName)
if (Test-Path -LiteralPath (Join-Path $projectDir "$projectName.gpr")) {
    $ghidraArgs += @('-process', (Split-Path -Leaf $imageFile))
} else {
    $ghidraArgs += @('-import', $imageFile, '-loader-loadLibraries', 'false', '-loader-linkExistingProjectLibraries', 'false')
}
$ghidraArgs += @('-noanalysis', '-scriptPath', (Join-Path $PSScriptRoot 'ghidra'), '-postScript', 'ExportSelected.java', $outputDir)
$ghidraArgs += $selections
# Fresh output is required because headless can return success after a script error.
foreach ($selection in $manifest.analysis_functions) {
    if ($selection.name -notmatch '^[A-Za-z_][A-Za-z0-9_]*$') { throw 'Invalid function name' }
    foreach ($extension in @('c', 'asm')) {
        $generatedFile = Join-Path $outputDir "$($selection.name).$extension"
        if (Test-Path -LiteralPath $generatedFile) { Remove-Item -LiteralPath $generatedFile }
    }
}
& $headless @ghidraArgs
if ($LASTEXITCODE -ne 0) { throw 'Ghidra failed; inspect its log' }
foreach ($selection in $manifest.analysis_functions) {
    if (-not (Test-Path -LiteralPath (Join-Path $outputDir "$($selection.name).c"))) {
        throw "Ghidra did not export $($selection.name)"
    }
}
Write-Output "Analysis drafts: $outputDir"
