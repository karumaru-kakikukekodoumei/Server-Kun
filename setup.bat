@echo off
setlocal

:: --- Configuration ---
set "ENV_NAME=ai_kun"
set "PYTHON_VERSION=3.9"
set "REQUIREMENTS_FILE=requirements.txt"
set "ENV_FILE=.env"

echo Starting AI-KUN environment setup for Conda...
echo This script will set up the Conda environment and install dependencies.
echo --------------------------------------------------
echo.

:: 1. Check for Conda
echo [Step 1/5] Checking for Conda...
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Conda is not installed or not found in your PATH.
    echo Please install Miniconda or Anaconda and ensure it's added to your PATH.
    echo Installation guide: https://docs.conda.io/projects/conda/en/latest/user-guide/install/
    goto :eof
)
echo -- Conda found.
echo.

:: 2. Check for Juman++ (Recommended)
echo [Step 2/5] Checking for Juman++ (Recommended)...
where jumanpp >nul 2>nul
if %errorlevel% neq 0 (
    echo WARNING: Juman++ is not found in your PATH.
    echo Juman++ is recommended for better Japanese morphological analysis, which improves AI accuracy.
    echo The bot will work without it, but with potentially lower accuracy.
    echo Installation guide: https://github.com/ku-nlp/jumanpp
) else (
    echo -- Juman++ found.
)
echo.

:: 3. Create Conda Environment
echo [Step 3/5] Setting up Conda environment '%ENV_NAME%'...
conda env list | findstr /C:"%ENV_NAME% " >nul
if %errorlevel% equ 0 (
    echo -- Conda environment '%ENV_NAME%' already exists. Skipping creation.
) else (
    echo -- Conda environment '%ENV_NAME%' not found. Creating...
    conda create --name %ENV_NAME% python=%PYTHON_VERSION% -y
    if %errorlevel% neq 0 (
        echo Error: Failed to create Conda environment '%ENV_NAME%'.
        goto :eof
    )
    echo -- Conda environment created successfully.
)
echo.

:: 4. Install Dependencies
echo [Step 4/5] Installing Python dependencies from %REQUIREMENTS_FILE%...
echo This may take a few minutes...
call conda run -n %ENV_NAME% pip install -r %REQUIREMENTS_FILE%
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies.
    echo Please check the output above for errors, or try running this command manually:
    echo   conda run -n %ENV_NAME% pip install -r %REQUIREMENTS_FILE%
    goto :eof
)
echo -- Dependencies installed successfully.
echo.

:: 5. Create .env file
echo [Step 5/5] Setting up %ENV_FILE% file...
if exist "%ENV_FILE%" (
    echo -- %ENV_FILE% file already exists. Skipping creation.
) else (
    echo Please enter your Discord Bot Token and press Enter:
    set /p DISCORD_TOKEN=
    if not defined DISCORD_TOKEN (
        echo Error: Token cannot be empty.
        echo Please run the script again and provide a valid token.
        goto :eof
    )
    echo DISCORD_BOT_TOKEN="%DISCORD_TOKEN%"> %ENV_FILE%
    echo -- %ENV_FILE% file created successfully.
)
echo.

echo --------------------------------------------------
echo AI-KUN setup is complete!
echo --------------------------------------------------
echo.
echo You can now use the new .bat scripts to run the bot.
echo.
echo   To start the bot:
echo   run.bat
echo.
echo   To gather conversation data:
echo   research.bat
echo.
echo   To train the AI model:
echo   learning.bat
echo.
echo For more details, please refer to README.md.
echo.

:eof
endlocal
pause