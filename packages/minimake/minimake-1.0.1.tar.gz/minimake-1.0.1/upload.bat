@echo off

REM Check if there is at least one argument
if "%~1"=="" (
	echo You must give a PyPI token to run this command
	pause
	exit /b 1
)

REM Set the TOKEN property to the given argument
set TOKEN=%~1

REM Build the module to the "minimake" folder
python -m build

REM Upload the module to PyPI
twine upload -u __token__ -p %TOKEN% dist/*
REM twine upload dist/*

pause