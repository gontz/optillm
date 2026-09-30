@echo off
rem Train SPL strategies. Starts the optillm server in its own window if it is not running.
rem   train-spl.bat                                  creative set, 2 passes
rem   train-spl.bat prompts\my_prompts.jsonl --passes 3
rem   train-spl.bat --summary                        show what has been learned so far
rem   train-spl.bat --reset                          back up and empty the learned strategies
setlocal
cd /d "%~dp0.."

if not exist ".venv\Scripts\python.exe" (
    echo Run start-optillm.bat once first to create the virtual environment.
    goto :error
)

if /i "%~1"=="--summary" goto :run
if /i "%~1"=="--reset" goto :run

curl -s -o nul http://127.0.0.1:8000/health
if not errorlevel 1 goto :run

echo Starting optillm server in a new window...
start "optillm" ".venv\Scripts\optillm.exe"
for /l %%i in (1,1,60) do (
    timeout /t 2 /nobreak >nul
    curl -s -o nul http://127.0.0.1:8000/health && goto :run
)
echo The server did not start. Check the optillm window.
goto :error

:run
".venv\Scripts\python.exe" spl_training\train_spl.py %*
pause
goto :eof

:error
pause
exit /b 1
