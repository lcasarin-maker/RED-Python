@echo off
rem Run full test suite for Cerberus project safely

rem Change to project root
cd /d "D:\GoogleDrive\AI\Cerberus"

rem Ensure Python uses UTF-8 output (helps on Windows)
set PYTHONUTF8=1

rem Disable pytest's internal capture to avoid 'underlying buffer has been detached' error
set PYTEST_ADDOPTS=-s

rem Run pytest with quiet output, showing only failures/passes
python -m pytest -q tests

rem Keep the console window open to review results
pause
