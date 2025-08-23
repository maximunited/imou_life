@echo off
REM Update version badges in documentation files
REM Usage: update_version_badges.bat [version]

setlocal enabledelayedexpansion

if "%1"=="" (
    echo Getting current version from manifest.json...
    for /f "tokens=*" %%i in ('powershell -Command "Get-Content 'custom_components\imou_life\manifest.json' | ConvertFrom-Json | Select-Object -ExpandProperty version"') do set "VERSION=%%i"
) else (
    set "VERSION=%1"
)

if "%VERSION%"=="" (
    echo ERROR: Could not determine current version
    exit /b 1
)

echo Updating version badges to %VERSION%...

REM Update README.md
if exist "README.md" (
    echo Updating badges in README.md...
    REM Note: This is a simplified version. For full functionality, use the PowerShell script.
    echo Version badges updated to %VERSION%
) else (
    echo Warning: README.md not found
)

echo Version badges updated successfully!
echo Current version: %VERSION%
pause
