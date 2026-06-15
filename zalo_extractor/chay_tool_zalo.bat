@echo off
chcp 65001 > nul
echo ===================================================
echo   TOOL TU DONG LAY LICH SU TIN NHAN ZALO PC
echo ===================================================
echo.
echo VUI LONG:
echo 1. Mo san Zalo PC va dang nhap
echo 2. De yen chuot va ban phim khi tool dang chay
echo.
echo Bat dau ngay bay gio...
echo.
cd /d d:\Antigravity\zalo_extractor
python zalo_scraper.py
echo.
echo ===================================================
echo Dang bat dau dung AI de phan tich Khach hang truc tiep...
python ai_analyzer.py
echo ===================================================
echo Da hoan thanh tat ca! Nhan phim bat ky de thoat...
pause > nul
