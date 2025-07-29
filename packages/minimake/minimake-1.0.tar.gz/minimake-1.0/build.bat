@echo off

REM ============================================
REM Script for building the Python module file
REM and copy it to multiple output directories
REM Usage : build.bat Path\To\Directory1 Path\To\Directory2 ...
REM ============================================

mkdir build
cd build

pip install ../
REM Debug version
REM pip install . -v

REM Check if user passed at least one destination directory
if "%~1"=="" (
    echo No destination directories specified, skipping copy.
    goto end
)

REM Search the first .pyd file inside current folder and subfolders
set "pydfile="
for /r %%f in (*.pyd) do (
    set "pydfile=%%f"
    goto found_pyd
)

echo No .pyd files found inside %CD%
goto end

:found_pyd
echo Found : %pydfile%

REM Iterate over all arguments (all destination folders)
:copy_loop
if "%~1"=="" goto end

set "DESTDIR=%~1"
echo Copying to "%DESTDIR%"
xcopy /Y /D "%pydfile%" "%DESTDIR%\"

shift
goto copy_loop

:end
echo Done.
pause