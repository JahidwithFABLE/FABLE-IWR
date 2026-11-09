# Collect approved historical FABLE-C source data without modifying original files.
param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$SpamWork = 'C:\FABLE_JAHID\Python Scripts\FINAL SPAM SCRIPt\data\work\SPAMFABLE',
    [string]$IwrSource = 'C:\FABLE_JAHID\WORK\Data\Water requirement data\FABLE final irrigation water requirement rebuild\FINAL_RELEASE_POST_SPAM_FIX\FABLE_crop_irrigation_water_requirement_2000_2020_FINAL_REPAIRED.csv',
    [string]$TechnologyFolder = 'C:\FABLE_JAHID\WORK\Data\Water requirement data\FABLE crop water requirement outputs\final_release',
    [string]$OriginalGlobalExport = 'C:\FABLE_JAHID\WORK\Data\FABLE3_GLOBAL_export'
)
$ErrorActionPreference = 'Stop'
$files = @(
    @('05 SPAM country master', (Join-Path $SpamWork '05_final_release\country\05_FABLE_SPAM_country_product_2000_2020.csv.gz'), 'data\spam\fablec\05_FABLE_SPAM_country_product_2000_2020.csv.gz'),
    @('06 harmonized SPAM', (Join-Path $SpamWork '06_harmonized_irrigation\06_FABLE_C_SPAM_historical_input_2000_2020_HARMONIZED.csv.gz'), 'data\spam\fablec\06_FABLE_C_SPAM_historical_input_2000_2020_HARMONIZED.csv.gz'),
    @('Repaired historical net IWR', $IwrSource, 'data\crop\fablec\FABLE_crop_irrigation_water_requirement_2000_2020_FINAL_REPAIRED.csv'),
    @('Approved irrigation shares', (Join-Path $TechnologyFolder '12_FABLE_irrigation_technology_shares_2000_2020_FINAL.csv'), 'data\technology\12_FABLE_irrigation_technology_shares_2000_2020_FINAL.csv'),
    @('Approved efficiencies', (Join-Path $TechnologyFolder '13_FABLE_irrigation_efficiency_parameters_FINAL.csv'), 'data\technology\13_FABLE_irrigation_efficiency_parameters_FINAL.csv'),
    @('Original IWR regression reference (optional)', (Join-Path $OriginalGlobalExport 'FABLE3_GLOBAL_IWR_2000_2020_FINAL.csv'), 'data\reference\fablec\FABLE3_GLOBAL_IWR_2000_2020_FINAL.csv'),
    @('Original SPAM regression reference (optional)', (Join-Path $OriginalGlobalExport 'FABLE3_GLOBAL_SPAM_2000_2020_FINAL.csv'), 'data\reference\fablec\FABLE3_GLOBAL_SPAM_2000_2020_FINAL.csv')
)
foreach ($item in $files) {
    $label = $item[0]
    $source = $item[1]
    $destination = Join-Path $RepoRoot $item[2]
    if (Test-Path -LiteralPath $destination -PathType Leaf) {
        Write-Host "EXISTS (not overwritten): $label => $destination"
    } elseif (Test-Path -LiteralPath $source -PathType Leaf) {
        $folder = Split-Path -Parent $destination
        New-Item -ItemType Directory -Force -Path $folder | Out-Null
        Copy-Item -LiteralPath $source -Destination $destination
        Write-Host "COPIED: $label => $destination"
    } else {
        Write-Warning "MISSING: $label; expected at $source"
    }
}
Write-Host 'All data is copied only into data/ (ignored by Git). Please run the Python input check next.'
