# PowerShell script to run Imou Life Integration Tests
Write-Host "Running Imou Life Integration Tests..." -ForegroundColor Green
Write-Host ""

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

# Run simple tests
python run_simple_tests.py

# Keep window open
Read-Host "Press Enter to continue..."
