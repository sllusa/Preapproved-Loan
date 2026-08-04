@echo off
echo Stopping services...

if exist pids.txt (
    for /f %%p in (pids.txt) do (
        taskkill /PID %%p /F >nul 2>&1
        echo   OK Stopped PID %%p
    )
    del pids.txt
    echo.
    echo OK All services stopped
) else (
    echo Warning: No pids.txt found -- services may not be running
)
