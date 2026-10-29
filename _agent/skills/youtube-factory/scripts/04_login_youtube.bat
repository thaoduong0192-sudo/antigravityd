@echo off
echo === DANG NHAP YOUTUBE STUDIO ===
echo Mo Chrome voi profile rieng. Hay dang nhap tai khoan YouTube.
echo Sau khi dang nhap xong, dong Chrome lai.
echo.
"C:\Program Files\Google\Chrome\Application\chrome.exe" --user-data-dir="%~dp0..\pipeline\chrome_profile_bot" "https://studio.youtube.com"
