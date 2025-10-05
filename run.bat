@echo off
REM This script runs the AI-KUN bot.
REM It ensures that the correct Conda environment ('ai_kun') is activated and used.

REM Get the directory of the batch script. This makes sure the script can be run from anywhere.
set "SCRIPT_DIR=%~dp0"

REM Use 'conda run' to execute the python script within the specified conda environment.
REM This is the recommended way to run scripts in a conda environment without manual activation.
call conda run -n ai_kun python "%SCRIPT_DIR%src\main.py" run

pause