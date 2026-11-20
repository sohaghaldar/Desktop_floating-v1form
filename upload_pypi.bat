@echo off
setlocal
title PyPI One-Click Publish (desktop-floating)
cls
echo ============================================================
echo         Publish desktop-floating v1.0.0 to PyPI
echo ============================================================
echo.
echo Package Name : desktop-floating
echo Version      : 1.0.0
echo Files        : dist\desktop_floating-1.0.0-py3-none-any.whl
echo                dist\desktop_floating-1.0.0.tar.gz
echo.
echo Instructions:
echo 1. When asked for username, enter: __token__
echo 2. When asked for password, paste your PyPI API token (starts with pypi-...)
echo.
python -m twine upload dist/desktop_floating*
echo.
pause
