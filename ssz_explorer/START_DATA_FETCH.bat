@echo off
echo ================================================================================
echo SSZ DATA FETCH SUITE
echo ================================================================================
echo.
echo Starting data enrichment interface...
echo This will run on http://localhost:7861
echo.

cd /d "%~dp0"

REM Try venvs
if exist "..\venv_clean\Scripts\activate.bat" (
    call ..\venv_clean\Scripts\activate.bat
) else if exist "..\venv\Scripts\activate.bat" (
    call ..\venv\Scripts\activate.bat
)

python data_fetch_app.py

pause
