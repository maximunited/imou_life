#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Git alias script for automatic version bumping and tagging
.DESCRIPTION
    This script is designed to be used as a Git alias: git bump [version]
    It automatically updates manifest.json, commits, creates tags, and pushes everything.
    If no version is supplied, it auto-increments the patch version.
#>

param(
    [Parameter(Position=0)]
    [string]$Version = "",
    
    [Parameter(Position=1)]
    [string]$Message = ""
)

# Function to parse and validate version
function Parse-Version {
    param([string]$VersionString)
    
    # Remove 'v' prefix if present
    $cleanVersion = $VersionString -replace '^v', ''
    
    # Check if it's a valid version format
    if ($cleanVersion -match '^(\d+)\.(\d+)(?:\.(\d+))?$') {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        $patch = if ($matches[3]) { [int]$matches[3] } else { 0 }
        
        return @{
            Major = $major
            Minor = $minor
            Patch = $patch
            Full = "$major.$minor.$patch"
            IsValid = $true
        }
    }
    
    return @{ IsValid = $false }
}

# Function to auto-increment version
function Get-NextVersion {
    param([string]$CurrentVersion)
    
    $parsed = Parse-Version $CurrentVersion
    if (-not $parsed.IsValid) {
        Write-Host "Error: Current version '$CurrentVersion' is not in valid format" -ForegroundColor Red
        exit 1
    }
    
    return "$($parsed.Major).$($parsed.Minor).$($parsed.Patch + 1)"
}

Write-Host "🚀 Git Bump - Automatic Version Management" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Check if we're in a git repository
if (-not (Test-Path ".git")) {
    Write-Host "Error: Not in a git repository!" -ForegroundColor Red
    exit 1
}

# Read current manifest
$manifestPath = "custom_components/imou_life/manifest.json"
if (-not (Test-Path $manifestPath)) {
    Write-Host "Error: manifest.json not found!" -ForegroundColor Red
    exit 1
}

try {
    $manifest = Get-Content $manifestPath | ConvertFrom-Json
    $oldVersion = $manifest.version
    Write-Host "Current version: $oldVersion" -ForegroundColor Yellow
} catch {
    Write-Host "Error reading version from manifest.json: $_" -ForegroundColor Red
    exit 1
}

# Determine new version
if ([string]::IsNullOrWhiteSpace($Version)) {
    # Auto-increment patch version
    $newVersion = Get-NextVersion $oldVersion
    Write-Host "Auto-incrementing to: $newVersion" -ForegroundColor Green
} else {
    # Parse user-provided version
    $parsed = Parse-Version $Version
    if (-not $parsed.IsValid) {
        Write-Host "Error: Version must be in format X.Y.Z or X.Y (e.g., 1.0.24, v1.0.24, 1.0)" -ForegroundColor Red
        exit 1
    }
    
    $newVersion = $parsed.Full
    Write-Host "New version: $newVersion" -ForegroundColor Green
}

# Check if version is actually changing
if ($oldVersion -eq $newVersion) {
    Write-Host "Warning: Version is already $newVersion" -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        Write-Host "Aborting version bump." -ForegroundColor Red
        exit 1
    }
}

# Check git status
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "Warning: You have uncommitted changes!" -ForegroundColor Yellow
    Write-Host "Uncommitted changes:" -ForegroundColor Yellow
    Write-Host $gitStatus
    Write-Host ""
    
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        Write-Host "Aborting version bump." -ForegroundColor Red
        exit 1
    }
}

# Update manifest.json
Write-Host "Updating manifest.json..." -ForegroundColor Green
$manifest.version = $newVersion
$manifest | ConvertTo-Json -Depth 10 | Set-Content $manifestPath

# Stage the change
Write-Host "Staging changes..." -ForegroundColor Green
git add $manifestPath

# Commit
$commitMessage = if ($Message) { "Bump version to $newVersion - $Message" } else { "Bump version to $newVersion" }
Write-Host "Committing changes: $commitMessage" -ForegroundColor Green
git commit -m $commitMessage

# Create and push tag
$tagName = "v$newVersion"
Write-Host "Creating tag: $tagName" -ForegroundColor Green

# Check if tag already exists locally
$localTag = git tag --list $tagName
if ($localTag) {
    Write-Host "Tag $tagName already exists locally, deleting..." -ForegroundColor Yellow
    git tag -d $tagName
}

# Check if tag exists on remote
$remoteTag = git ls-remote --tags origin $tagName
if ($remoteTag) {
    Write-Host "Tag $tagName already exists on remote, deleting..." -ForegroundColor Yellow
    git push origin ":refs/tags/$tagName"
}

# Create the tag
git tag $tagName

# Push changes and tag
Write-Host "Pushing changes and tag..." -ForegroundColor Green
git push origin master
git push origin $tagName

Write-Host ""
Write-Host "🎉 Version bump completed successfully!" -ForegroundColor Green
Write-Host "✅ Version updated to $newVersion" -ForegroundColor Green
Write-Host "✅ Changes committed and pushed" -ForegroundColor Green
Write-Host "✅ Tag $tagName created and pushed" -ForegroundColor Green
Write-Host "✅ GitHub Actions workflow triggered" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Check the Actions tab in your GitHub repository" -ForegroundColor White
Write-Host "2. Wait for the Release Management workflow to complete" -ForegroundColor White
Write-Host "3. Check the Releases section for your new pre-release" -ForegroundColor White
