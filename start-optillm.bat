@echo off
rem Start the OptiLLM proxy against the local Ollama server.
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

".venv\Scripts\optillm.exe" %*
goto :eof

:error
pause
exit /b 1
