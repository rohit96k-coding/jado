echo ===================================================
echo     STARTING SAMi (Smart Artificial Mind)
echo ===================================================
cd /d "%~dp0"
echo.

echo [1/2] Checking Configuration...
python setup_spotify.py

echo [2/2] Launching Core Systems...
python main.py

pause
