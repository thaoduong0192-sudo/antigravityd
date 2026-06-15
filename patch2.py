import os
import re

files = {
    r"D:\Antigravity\ecopets_seo\fully_auto_system.py": {
        "interval": 86400, # 1 per day
        "has_orders": "False"
    },
    r"D:\Antigravity\helloconsen_seo\fully_auto_consen.py": {
        "interval": 8640, # 10 per day (2.4 hours)
        "has_orders": "True"
    },
    r"D:\Antigravity\hoiky_seo\fully_auto_hoiky.py": {
        "interval": 4320, # 20 per day (1.2 hours)
        "has_orders": "True"
    },
    r"D:\Antigravity\giaiphapqrcode_seo\fully_auto_giaiphapqrcode.py": {
        "interval": 8640, # 10 per day
        "has_orders": "False"
    }
}

for filepath, config in files.items():
    if not os.path.exists(filepath):
        continue
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    new_loop = f"""import time
from datetime import datetime

if __name__ == "__main__":
    print("=============================================================")
    print("     HE THONG VAN HANH SEO TU DONG (ROBUST SCHEDULER)")
    print("=============================================================")
    print(f"Kich hoat he thong tu dong dang bai! (Moi {{ {config['interval']} }} giay 1 bai)")

    last_daily_run = 0
    last_order_check = time.time()
    last_weekly_report = None

    while True:
        now_ts = time.time()
        now_dt = datetime.now()

        # Check orders every 5 minutes (300 seconds)
        if {config['has_orders']}:
            if now_ts - last_order_check >= 300:
                run_safe(check_new_orders) if "run_safe" in globals() else check_new_orders()
                last_order_check = now_ts

        # Run daily job
        if now_ts - last_daily_run >= {config['interval']}:
            print(f"\\n[+] Dang chay tien trinh dang bai luc: {{now_dt.strftime('%H:%M:%S')}}")
            try:
                run_safe(run_daily_job) if "run_safe" in globals() else run_daily_job()
            except Exception as e:
                try:
                    run_daily_job()
                except Exception as ex:
                    print(f"Loi: {{ex}}")
            last_daily_run = now_ts

        # Check weekly report (Sunday after 10:00)
        if now_dt.weekday() == 6 and now_dt.hour >= 10 and (last_weekly_report is None or last_weekly_report.date() != now_dt.date()):
            try:
                run_safe(run_weekly_job) if "run_safe" in globals() else run_weekly_job()
            except Exception as e:
                try:
                    run_weekly_job()
                except Exception as ex:
                    print(f"Loi: {{ex}}")
            last_weekly_report = now_dt

        time.sleep(60)
"""

    # Because we already replaced it earlier, we can just replace from `if __name__ == "__main__":` to the end.
    # But wait! I replaced `if __name__ == "__main__":` with `import time\nfrom datetime import datetime\n\nif __name__ == "__main__":`
    # Let's replace from `import time\nfrom datetime import datetime` to the end!
    if "import time\nfrom datetime import datetime" in content:
        content = content[:content.find("import time\nfrom datetime import datetime")] + new_loop
    else:
        # Fallback if somehow it wasn't replaced yet
        if "def start_daemon():" in content:
            content = re.sub(r'def start_daemon\(\):.*', new_loop, content, flags=re.DOTALL)
        else:
            content = re.sub(r'if __name__ == "__main__":.*', new_loop, content, flags=re.DOTALL)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print("Patched completely and syntax fixed")
