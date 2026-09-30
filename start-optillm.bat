@echo off
rem Start the OptiLLM proxy and its chat GUI against the local Ollama server.
rem Extra arguments are passed through, e.g. start-optillm.bat --approach moa --model gemma4:26b
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\optillm.exe" (
    echo Creating virtual environment...
    python -m venv .venv || goto :error
    ".venv\Scripts\python" -m pip install --upgrade pip || goto :error
    ".venv\Scripts\python" -m pip install -e . || goto :error
)

curl -s -o nul http://localhost:11434/api/tags
if errorlevel 1 (
    echo Ollama is not reachable on http://localhost:11434. Start Ollama first.
    goto :error
)

rem Open the chat GUI in the browser once the server has had time to start
start "" /b cmd /c "timeout /t 10 /nobreak >nul & start http://127.0.0.1:7860"

echo API: http://127.0.0.1:8000/v1   Chat GUI: http://127.0.0.1:7860
".venv\Scripts\optillm.exe" --launch-gui %*
goto :eof

:error
pause
exit /b 1
