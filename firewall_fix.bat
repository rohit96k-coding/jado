@echo off
echo ===================================================
echo   FIXING FIREWALL FOR SAMI VOICE ASSISTANT
echo ===================================================
echo.
echo Attempting to allow incoming connections on Port 5000...
echo.

netsh advfirewall firewall add rule name="SAMi Brain (TCP-In)" dir=in action=allow protocol=TCP localport=5000
netsh advfirewall firewall add rule name="SAMi Brain (UDP-In)" dir=in action=allow protocol=UDP localport=5000

echo.
echo ===================================================
echo IF YOU SAW "Ok." ABOVE:
echo Success! Your phone should now connect.
echo.
echo IF YOU SAW "The requested operation requires elevation":
echo FAILED. You must Right-Click this file and choose "Run as Administrator".
echo ===================================================
pause
