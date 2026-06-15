@echo off
title CHAY AUTO POSTER FACEBOOK (B2B)
color 0a

echo ==================================================
echo HẸ THONG DANG BAI FACEBOOK TU DONG - ECOPETS
echo ==================================================
echo.

:: Kiem tra cai dat Playwright
pip show playwright >nul 2>&1
if %errorlevel% neq 0 (
    echo [1] Phat hien chua co thu vien Playwright. Dang tien hanh cai dat tu dong...
    pip install playwright
    playwright install chromium
) else (
    echo [1] Playwright da san sang.
)

echo [2] Dang goi Tool...
python fb_auto_poster.py

echo.
pause
