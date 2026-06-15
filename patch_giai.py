import os
import re

filepath = r"D:\Antigravity\giaiphapqrcode_seo\fully_auto_giaiphapqrcode.py"
interval = 8640 # 10 per day (2.4 hours)
has_orders = False

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

new_loop = f"""import time
from datetime import datetime

if __name__ == "__main__":
    print("=============================================================")
    print("     HỆ THỐNG VẬN HÀNH SEO TỰ ĐỘNG (ROBUST SCHEDULER)")
    print("=============================================================")
    print(f"✅ Đã kích hoạt hệ thống tự động đăng bài! (Mỗi {{ {interval} }} giây 1 bài)")

    last_daily_run = 0  # Chạy ngay lập tức lần đầu
    last_order_check = time.time()
    last_weekly_report = None

    while True:
        now_ts = time.time()
        now_dt = datetime.now()

        # Check orders every 5 minutes (300 seconds)
        {"if now_ts - last_order_check >= 300:" if has_orders else "if False:"}
            {"run_safe(check_new_orders)" if has_orders else "pass"}
            {"last_order_check = now_ts" if has_orders else ""}

        # Run daily job
        if now_ts - last_daily_run >= {interval}:
            print(f"\\n[+] Đang chạy tiến trình đăng bài lúc: {{now_dt.strftime('%H:%M:%S')}}")
            try:
                run_safe(run_daily_job) if "run_safe" in globals() else run_daily_job()
            except Exception as e:
                try:
                    run_daily_job()
                except Exception as ex:
                    print(f"Lỗi: {{ex}}")
            last_daily_run = now_ts

        # Check weekly report (Sunday after 10:00)
        if now_dt.weekday() == 6 and now_dt.hour >= 10 and (last_weekly_report is None or last_weekly_report.date() != now_dt.date()):
            try:
                run_safe(run_weekly_job) if "run_safe" in globals() else run_weekly_job()
            except Exception as e:
                try:
                    run_weekly_job()
                except Exception as ex:
                    print(f"Lỗi: {{ex}}")
            last_weekly_report = now_dt

        time.sleep(60)
"""

content = re.sub(r'if __name__ == "__main__":.*', new_loop, content, flags=re.DOTALL)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched giaiphapqrcode successfully")
