@echo off
echo Running Imou Life Integration Tests...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run simple tests
python run_simple_tests.py

REM Pause to see results
pause
