@echo off
echo Iniciando servidores do CapBot...
echo.

echo [1/2] Iniciando API Backend (porta 8000)...
start "CapBot API" cmd /k "python main.py"

echo [2/2] Iniciando Frontend (porta 3000)...
cd frontend
start "CapBot Frontend" cmd /k "python -m http.server 3000"

echo.
echo ✅ Servidores iniciados!
echo 🌐 Frontend: http://localhost:3000
echo 🔧 API: http://localhost:8000
echo.
echo Pressione qualquer tecla para sair...
pause > nul
