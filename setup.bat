@echo off
setlocal

:: AI-KUN Environment Setup Script for Windows (.bat)

:: --- Configuration ---
set "PYTHON_MAJOR_VERSION=3"
set "PYTHON_MINOR_VERSION=8"
set "VENV_DIR=.venv"

:: --- Helper Functions for Colored Text ---
:: (This is a bit tricky in batch, we'll use it sparingly)
:: For this, we'll just use ECHO with clear section headers.

echo.
echo ==================================================
echo      Starting AI-KUN Environment Setup
echo ==================================================
echo.
echo This script will guide you through the setup process.
echo.

:: 1. Check for Python
echo [Step 1/5] Checking for Python...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not found in your PATH.
    echo Please install Python %PYTHON_MAJOR_VERSION%.%PYTHON_MINOR_VERSION% or higher from https://www.python.org/
    echo and ensure it's added to your PATH.
    goto :eof
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do (
    for /f "tokens=1,2 delims=." %%a in ("%%v") do (
        set "PY_MAJOR=%%a"
        set "PY_MINOR=%%b"
    )
)

if %PY_MAJOR% LSS %PYTHON_MAJOR_VERSION% (
    echo ERROR: Your Python version is %PY_MAJOR%.%PY_MINOR%. AI-KUN requires Python %PYTHON_MAJOR_VERSION%.%PYTHON_MINOR_VERSION% or higher.
    echo Please upgrade your Python installation.
    goto :eof
)
if %PY_MAJOR% EQU %PYTHON_MAJOR_VERSION% (
    if %PY_MINOR% LSS %PYTHON_MINOR_VERSION% (
        echo ERROR: Your Python version is %PY_MAJOR%.%PY_MINOR%. AI-KUN requires Python %PYTHON_MAJOR_VERSION%.%PYTHON_MINOR_VERSION% or higher.
        echo Please upgrade your Python installation.
        goto :eof
    )
)

echo  - Python %PY_MAJOR%.%PY_MINOR% found.
echo.

:: 2. Check for Juman++ (Recommended)
echo [Step 2/5] Checking for Juman++ (Recommended)...
where jumanpp >nul 2>nul
if %errorlevel% neq 0 (
    echo  - WARNING: Juman++ is not found in your PATH.
    echo    Juman++ is recommended for better Japanese morphological analysis.
    echo    The bot will work without it, but with potentially lower accuracy.
    echo    Installation guide: https://github.com/ku-nlp/jumanpp
) else (
    echo  - Juman++ found.
)
echo.

:: 3. Create Virtual Environment
echo [Step 3/5] Creating Python virtual environment...
if exist "%VENV_DIR%" (
    echo  - Virtual environment '%VENV_DIR%' already exists. Skipping creation.
) else (
    python -m venv %VENV_DIR%
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment.
        goto :eof
    )
    echo  - Virtual environment created successfully.
)
echo.

:: 4. Install Python Dependencies
echo [Step 4/5] Installing Python dependencies from requirements.txt...
echo This may take a few minutes...
call "%VENV_DIR%\Scripts\pip.exe" install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies. Please check the output above.
    echo You can try running this command manually:
    echo %VENV_DIR%\Scripts\pip.exe install -r requirements.txt
    goto :eof
)
echo  - Dependencies installed successfully.
echo.

:: 5. Create .env file
echo [Step 5/5] Setting up .env file...
if exist ".env" (
    echo  - .env file already exists. Skipping creation.
) else (
    set "BOT_TOKEN="
    set /p "BOT_TOKEN=Please enter your Discord Bot Token and press Enter: "
    if not defined BOT_TOKEN (
        echo ERROR: Token cannot be empty.
        echo Please run the script again and provide a valid token.
        goto :eof
    )
    echo DISCORD_BOT_TOKEN="%BOT_TOKEN%">.env
    echo  - .env file created successfully.
)
echo.

echo ==================================================
echo      AI-KUN Setup is Complete!
echo ==================================================
echo.
echo Next Steps:
echo.
echo 1. Activate the virtual environment by running this command:
echo    call .\.venv\Scripts\activate.bat
echo.
echo 2. Follow the usage instructions in README.md to start using AI-KUN.
echo    Recommended commands:
echo.
echo    rem To gather conversation data from your server
echo    python src/main.py research
echo.
echo    rem To train the AI model (fine-tuning)
echo    python src/main.py learning
echo.
echo    rem To run the bot
echo    python src/main.py run
echo.
echo For more details, please refer to README.md.
echo.