Write-Host "🐳 Running Imou Life tests in Docker..." -ForegroundColor Green
Write-Host ""

# Create directories for test results
if (!(Test-Path "coverage")) { New-Item -ItemType Directory -Name "coverage" }
if (!(Test-Path "test-results")) { New-Item -ItemType Directory -Name "test-results" }

# Build and run tests
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

Write-Host ""
Write-Host "✅ Docker tests completed!" -ForegroundColor Green
Write-Host "📊 Check the coverage/ and test-results/ folders for results" -ForegroundColor Cyan
Read-Host "Press Enter to continue"
