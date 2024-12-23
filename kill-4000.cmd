@echo off
echo Finding processes using port 4000...

:: Get the list of PIDs using port 4000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :4000') do (
    echo Killing process with PID %%a...
    taskkill /PID %%a /F >nul 2>&1
)

echo All processes using port 4000 have been terminated.