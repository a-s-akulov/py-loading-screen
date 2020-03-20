@echo off

python setup.py sdist bdist_wheel
twine upload dist/*

echo.
echo.
pause