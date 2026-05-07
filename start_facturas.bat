@echo off
cd /d "%~dp0"
start "Facturas Local Server" /min node server.js
timeout /t 2 /nobreak >nul
start http://localhost:8765/
