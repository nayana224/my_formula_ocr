@echo off
setlocal
cd /d "%~dp0\.."
if not exist .venv\Scripts\python.exe (
  echo [ERROR] .venv is missing. Create the environment and install the project first.
  exit /b 1
)
.venv\Scripts\python.exe -m formula_ocr
