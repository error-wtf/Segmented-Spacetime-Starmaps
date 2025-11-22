@echo off
echo ================================================================================
echo SSZ EXPLORER - COMPLETE EDITION
echo ================================================================================
echo Starting on PORT 9401...
echo.
echo FEATURES:
echo  - 50,000 Star Database (GAIA DR3)
echo  - CSV Download
echo  - SSZ Physics Tab (5 Sub-Tabs)
echo  - Interactive Navigation
echo  - All Catalogs Working
echo.
echo Opening browser at: http://localhost:9401
echo ================================================================================
echo.

cd /d "%~dp0"
start http://localhost:9401
python ssz_explorer\gradio_app_extended.py --server-port 9401

pause
