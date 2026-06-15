@echo off
echo Dang tao tac vu Windows Task Scheduler de chay Bao Cao SEO vao 9:00 AM Thu 2 hang tuan...
schtasks /create /tn "Antigravity_SEO_Reporter" /tr "D:\Antigravity\seo_reporter\run_reporter.bat" /sc weekly /d MON /st 09:00 /f
echo Da hoan thanh!
pause
