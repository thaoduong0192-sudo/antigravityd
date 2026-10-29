import sys
import subprocess
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

NOTEBOOK_ID = "5c160b5f-f72c-48cb-8da3-924e8b0eb94f"

def add_sources():
    with open("urls.txt", "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]
    
    print(f"Bắt đầu nạp {len(urls)} video vào NotebookLM (ID: {NOTEBOOK_ID})...")
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Nạp {url}...")
        try:
            # Dùng uv run nlm
            subprocess.run(["uv", "run", "nlm", "source", "add", NOTEBOOK_ID, "--url", url], check=True, capture_output=True)
            print(f"  -> Thành công")
        except subprocess.CalledProcessError as e:
            print(f"  -> Thất bại: {e.stderr.decode('utf-8') if e.stderr else str(e)}")
            
        # Nghỉ 1s tránh rate limit của NotebookLM
        time.sleep(1)
        
    print("Hoàn tất nạp 50 video!")

if __name__ == "__main__":
    add_sources()
