#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Project information and navigation helper
.DESCRIPTION
    This script provides information about the project structure and helps developers navigate the restructured project.
#>

Write-Host "🏗️ Imou Life - Project Structure" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📁 Directory Structure:" -ForegroundColor Yellow
Write-Host "├── custom_components/imou_life/    # Home Assistant integration" -ForegroundColor White
Write-Host "├── tools/                          # Development and utility tools" -ForegroundColor White
Write-Host "│   ├── scripts/                    # PowerShell/Batch scripts" -ForegroundColor White
Write-Host "│   ├── docker/                     # Docker testing files" -ForegroundColor White
Write-Host "│   └── validation/                 # Setup validation tools" -ForegroundColor White
Write-Host "├── tests/                          # Test suite" -ForegroundColor White
Write-Host "│   ├── unit/                       # Unit tests" -ForegroundColor White
Write-Host "│   ├── integration/                # Integration tests" -ForegroundColor White
Write-Host "│   └── fixtures/                   # Test data and fixtures" -ForegroundColor White
Write-Host "├── docs/                           # Documentation" -ForegroundColor White
Write-Host "├── scripts/                        # Build and deployment scripts" -ForegroundColor White
Write-Host "└── config/                         # Configuration files" -ForegroundColor White
Write-Host ""

Write-Host "🚀 Quick Commands:" -ForegroundColor Yellow
Write-Host "• Activate environment: .\tools\scripts\activate_venv.ps1" -ForegroundColor White
Write-Host "• Run tests: python -m pytest tests/" -ForegroundColor White
Write-Host "• Version bump: .\tools\scripts\git-bump.ps1" -ForegroundColor White
Write-Host "• Docker tests: .\tools\scripts\run_docker_tests.ps1" -ForegroundColor White
Write-Host ""

Write-Host "📚 Documentation:" -ForegroundColor Yellow
Write-Host "• Main docs: docs/README.md" -ForegroundColor White
Write-Host "• Quick start: docs/QUICK_START.md" -ForegroundColor White
Write-Host "• Testing: docs/TESTING.md" -ForegroundColor White
Write-Host "• Configuration: docs/CONFIGURATION.md" -ForegroundColor White
Write-Host "• FAQ: docs/FAQ.md" -ForegroundColor White
Write-Host ""

Write-Host "🔧 Configuration:" -ForegroundColor Yellow
Write-Host "• Dependencies: config/requirements*.txt" -ForegroundColor White
Write-Host "• Test config: config/.coveragerc, config/setup.cfg" -ForegroundColor White
Write-Host "• Pre-commit: .pre-commit-config.yaml" -ForegroundColor White
Write-Host ""

Write-Host "📊 Test Results:" -ForegroundColor Yellow
Write-Host "• Coverage HTML: tools/htmlcov/index.html" -ForegroundColor White
Write-Host "• Coverage XML: tools/coverage.xml" -ForegroundColor White
Write-Host "• Test results: tools/test-results/" -ForegroundColor White
Write-Host ""

Write-Host "💡 Tips:" -ForegroundColor Green
Write-Host "• Use 'git bump' for automated version management" -ForegroundColor White
Write-Host "• Check docs/QUICK_START.md for 5-minute setup" -ForegroundColor White
Write-Host "• Run tests before committing changes" -ForegroundColor White
Write-Host "• Use Docker for consistent testing environments" -ForegroundColor White
