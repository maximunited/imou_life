@echo off
echo 🐳 Running Imou Life tests in Docker...
echo.

REM Create directories for test results
if not exist "coverage" mkdir coverage
if not exist "test-results" mkdir test-results

REM Build and run tests
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

echo.
echo ✅ Docker tests completed!
echo 📊 Check the coverage/ and test-results/ folders for results
pause
