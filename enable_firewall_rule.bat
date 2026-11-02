@echo off
:: Batch script to permit Smart Blind Stick telemetry on Port 8000 and 8001
echo ========================================================
echo  Configuring Windows Network & Firewall for Blind Stick
echo ========================================================
echo.
echo 1. Adding Inbound Firewall Rules for Port 8000 and 8001...
netsh advfirewall firewall add rule name="Smart Blind Stick Ports" dir=in action=allow protocol=TCP localport=8000,8001 profile=any
echo.
echo 2. Setting Wi-Fi Connection to Private Network...
powershell -NoProfile -Command "Get-NetConnectionProfile -InterfaceAlias 'Wi-Fi' | Set-NetConnectionProfile -NetworkCategory Private"
echo.
echo 3. Adding WSL2 Portproxy from 10.30.115.161:8000 to 127.0.0.1:8000...
netsh interface portproxy add v4tov4 listenport=8000 listenaddress=10.30.115.161 connectport=8000 connectaddress=127.0.0.1
echo.
echo ========================================================
echo  SUCCESS! Inbound ports and portproxy configured.
echo ========================================================
pause
