@echo off
set "CURRENT_DIR=%~dp0..\..\"
echo ***** Current directory: %CURRENT_DIR% *****

git -C "%CURRENT_DIR%" pull --ff-only
if errorlevel 1 (
  echo ##### Update failed #####
  pause
  exit /b 1
)

if exist "%CURRENT_DIR%apps\money-printer-turbo\requirements.txt" (
  "%CURRENT_DIR%lib\python\Scripts\pip.exe" install -r "%CURRENT_DIR%apps\money-printer-turbo\requirements.txt"
)

echo ##### Update completed #####
pause
