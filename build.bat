@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" python -m venv .venv
if errorlevel 1 (echo Python/venv creation failed. Make sure Python is installed and available as "python". & pause & exit /b 1)
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
python -m PyInstaller --noconfirm --clean InfiniteImage.spec
if errorlevel 1 (echo BUILD FAILED & pause & exit /b 1)
echo.
echo Build successful: dist\InfiniteImage.exe
echo.
pause
