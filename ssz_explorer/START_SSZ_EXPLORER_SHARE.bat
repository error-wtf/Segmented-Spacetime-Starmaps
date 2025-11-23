@echo off
REM Start SSZ Explorer with Share Link (for Colab/Online)
echo.
echo ================================================================================
echo SSZ EXPLORER - LAUNCHING WITH SHARE LINK
echo ================================================================================
echo.

cd /d "%~dp0"

REM Activate venv if exists
if exist "..\venv\Scripts\activate.bat" (
    call ..\venv\Scripts\activate.bat
) else if exist "..\venv_clean\Scripts\activate.bat" (
    call ..\venv_clean\Scripts\activate.bat
)

REM Launch with share flag
python gradio_app_complete.py --share --port 7860

pause
