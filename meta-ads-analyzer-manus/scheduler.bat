@echo off
chcp 65001 >nul
echo ============================================================
echo   Meta Ads Optimizer - Windows Task Scheduler Setup
echo ============================================================

:: Đường dẫn tới Python và script
set PYTHON=python
set SCRIPT_DIR=D:\Antigravity\meta-ads-analyzer-manus
set RUN_SCRIPT=%SCRIPT_DIR%\run_daily.py
set LOG_DIR=%SCRIPT_DIR%\reports\logs

:: Tạo thư mục log
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo.
echo [1] Tao Task Scheduler chay luc 06:00 sang moi ngay...

schtasks /create /tn "MetaAdsOptimizer_Daily" ^
  /tr "\"%PYTHON%\" \"%RUN_SCRIPT%\" --date yesterday" ^
  /sc daily /st 06:00 ^
  /ru "%USERNAME%" ^
  /f ^
  /rl HIGHEST ^
  2>nul

if %ERRORLEVEL% EQU 0 (
    echo [OK] Da tao Task Scheduler thanh cong!
    echo      Ten task: MetaAdsOptimizer_Daily
    echo      Gio chay: 06:00 sang moi ngay
) else (
    echo [WARN] Khong the tao Task Scheduler tu dong.
    echo        Hay chay thu cong: python run_daily.py
)

echo.
echo [2] Cac lenh huu ich:
echo   Chay ngay:     python "%RUN_SCRIPT%"
echo   Xem lich su:   schtasks /query /tn "MetaAdsOptimizer_Daily"
echo   Xoa task:      schtasks /delete /tn "MetaAdsOptimizer_Daily" /f
echo   Setup:         python "%SCRIPT_DIR%\setup.py"
echo.
echo ============================================================
echo   Hoan tat! Mo dashboard tai: dashboard\index.html
echo ============================================================
pause
