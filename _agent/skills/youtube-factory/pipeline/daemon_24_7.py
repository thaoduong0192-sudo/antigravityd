#!/usr/bin/env python3
"""24/7 Daemon Worker — Chạy tự động không cần Antigravity IDE
Cấu hình: Windows Task Scheduler chạy mỗi 15 phút
Chức năng: Quét email + gửi Ebook tự động cho các kênh đang ở Bước 5
"""
import os, sys, yaml, subprocess, datetime, time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REGISTRY_PATH = os.path.join(BASE_DIR, "channels_registry.yaml")
LOG_PATH = os.path.join(BASE_DIR, "output_factory", "daemon_log.txt")

def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def main():
    log("=== DAEMON 24/7 BẮT ĐẦU CHU KỲ QUÉT ===")
    
    if not os.path.exists(REGISTRY_PATH):
        log("[!] Không tìm thấy channels_registry.yaml. Thoát.")
        return
    
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = yaml.safe_load(f)
    
    channels = registry.get("channels", [])
    run_count = 0
    
    for channel in channels:
        if run_count >= 3:
            log("[!] Đã đạt giới hạn 3 kênh/lần chạy. Dừng.")
            break
        
        for topic in channel.get("topics", []):
            if topic.get("current_step") == 5:
                ch_idx = f"{channel['index']:02d}"
                ch_id = channel['id']
                t_idx = f"{topic['index']:02d}"
                t_id = topic['id']
                topic_dir = os.path.join(BASE_DIR, "output_factory", f"channel_{ch_idx}_{ch_id}", f"topic_{t_idx}_{t_id}")
                
                if not os.path.exists(topic_dir):
                    log(f"  [!] Thư mục không tồn tại: {topic_dir}")
                    continue
                
                log(f"  ✉️ Chạy Auto-Mailer cho kênh {ch_id} / chủ đề {t_id}...")
                cmd = [sys.executable, "module_5_auto_mailer.py", "--topic-dir", topic_dir]
                try:
                    proc = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True, encoding="utf-8", timeout=300)
                    if proc.stdout:
                        for line in proc.stdout.strip().split("\n"):
                            log(f"    {line}")
                except Exception as e:
                    log(f"  [!] Lỗi: {e}")
                
                time.sleep(120)  # Stagger 2 phút giữa các kênh
                run_count += 1
    
    log("=== DAEMON 24/7 KẾT THÚC CHU KỲ ===")

if __name__ == "__main__":
    main()
