
<#
.SYNOPSIS
    Update version badges in documentation files
.DESCRIPTION
    This script automatically updates version badges in README.md and other documentation
    files based on the current version in manifest.json.
#>

param(
    [Parameter(Position=0)]
    [string]$Version = ""
)

# Function to get current version from manifest.json
function Get-CurrentVersion {
    $manifestPath = "custom_components/imou_life/manifest.json"
    if (Test-Path $manifestPath) {
        $manifest = Get-Content $manifestPath | ConvertFrom-Json
        return $manifest.version
    }
    return $null
}

# Function to update version badges in a file
function Update-VersionBadges {
    param(
        [string]$FilePath,
        [string]$CurrentVersion
    )

    if (-not (Test-Path $FilePath)) {
        Write-Host "File not found: $FilePath" -ForegroundColor Yellow
        return
    }

    $content = Get-Content $FilePath -Raw

    # Update release badge
    $content = $content -replace 'badge/release-\d+\.\d+\.\d+', "badge/release-$CurrentVersion"

    # Update pre-release badge (same version for now)
    $content = $content -replace 'badge/pre--release-\d+\.\d+\.\d+', "badge/pre--release-$CurrentVersion"

    # Write back to file
    Set-Content $FilePath $content -NoNewline
    Write-Host "✅ Updated version badges in $FilePath" -ForegroundColor Green
}

# Main execution
$currentVersion = if ($Version) { $Version } else { Get-CurrentVersion }

if (-not $currentVersion) {
    Write-Host "❌ Could not determine current version" -ForegroundColor Red
    exit 1
}

Write-Host "🔄 Updating version badges to $currentVersion" -ForegroundColor Cyan

# Update badges in main documentation files
Update-VersionBadges "README.md" $currentVersion

Write-Host "🎉 Version badges updated successfully!" -ForegroundColor Green
Write-Host "Current version: $currentVersion" -ForegroundColor White
