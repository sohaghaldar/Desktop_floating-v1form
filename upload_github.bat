@echo off
setlocal
title GitHub One-Click Push (Desktop_floating-v1form)
cls
echo ============================================================
echo     Pushing Desktop Floating to GitHub (sohaghaldar)
echo ============================================================
echo.
echo Target Repository: https://github.com/sohaghaldar/Desktop_floating-v1form
echo.
echo NOTE: Make sure you created the empty repository "Desktop_floating-v1form"
echo on https://github.com/new first!
echo.

git branch -M main
git push -u origin main
if %errorlevel% equ 0 (
    echo.
    echo [✓] Pushed main branch successfully!
    echo [>] Pushing version tag v2.6.0...
    git push origin v2.6.0
    echo [✓] All done! Your code and release pipeline are live on GitHub!
) else (
    echo.
    echo [!] Push failed or authorization cancelled.
    echo Please make sure the repo "Desktop_floating-v1form" exists at https://github.com/new.
)

echo.
pause
