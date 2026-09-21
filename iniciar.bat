@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    py -3 -m venv .venv
    if errorlevel 1 goto :error
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :error
".venv\Scripts\python.exe" -m streamlit run app.py --server.address localhost
if errorlevel 1 goto :error
exit /b 0
:error
echo.
echo Nao foi possivel iniciar. Confira o erro acima e a instalacao do Python 3.11 ou superior.
pause
exit /b 1
