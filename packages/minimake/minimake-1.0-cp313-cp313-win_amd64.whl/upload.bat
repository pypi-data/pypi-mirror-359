REM Build the module to the "minimake" folder
python -m build

REM Upload the module to PyPI
twine upload dist/*

pause