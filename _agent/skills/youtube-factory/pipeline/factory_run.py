import subprocess
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def run_script(script_name, args=[]):
    print(f"\n[{script_name}] BẮT ĐẦU CHẠY...")
    cmd = ["python", script_name] + args
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print(f"[{script_name}] Đã xảy ra lỗi, Dừng luồng Factory.")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Sử dụng: python factory_run.py \"Tên khóa học\"")
        sys.exit(1)
        
    topic = sys.argv[1]
    
    # 1. Sinh nội dung AI & cấu trúc file Text
    run_script("module_1_content_gen.py", [topic])
    
    # 2. Render Video
    run_script("module_2_3_video_factory.py")
    
    # 3. Lịch đăng báo tự động
    run_script("module_4_youtube_bot.py")
    
    print("\n[+] TOÀN BỘ CHUỖI NHÀ MÁY ĐÃ HOÀN TẤT VÀ TỰ ĐỘNG NGỦ!")

if __name__ == "__main__":
    main()
