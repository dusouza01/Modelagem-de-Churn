@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    py -3.13 -m venv .venv
    if errorlevel 1 goto :error
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :error
".venv\Scripts\python.exe" train.py
if errorlevel 1 goto :error
echo Treinamento concluido. Agora execute iniciar.bat.
pause
exit /b 0
:error
echo Nao foi possivel treinar. Confira o erro acima.
pause
exit /b 1
