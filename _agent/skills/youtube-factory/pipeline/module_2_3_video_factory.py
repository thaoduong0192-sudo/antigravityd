import sys
import json
import time
import subprocess
import os
from factory_state import load_state, save_state

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def run_cmd(cmd, capture=True):
    try:
        res = subprocess.run(cmd, check=True, capture_output=capture, text=True, encoding='utf-8')
        return res.stdout if capture else None
    except subprocess.CalledProcessError as e:
        print(f"[LỖI] Lệnh thất bại: {' '.join(cmd)}")
        if e.stderr:
            print(e.stderr)
        raise e

def render_videos(state, video_type="long_topics", nlm_format="explainer", lang="vi"):
    nb_id = state["notebook_id"]
    topics = state.get(video_type, [])
    
    for item in topics:
        if not item.get("video_id"):
            print(f"[*] Đang ra lệnh render video ({nlm_format}): {item['title']}")
            if nlm_format == "short":
                focus_arg = f"BẮT BUỘC DÙNG FONT CHỮ: Arial, Roboto, hoặc Noto Sans để hiển thị đúng dấu Tiếng Việt. KHÔNG DÙNG FONT NGHỆ THUẬT GÂY LỖI Ô VUÔNG. Hook giật gân, tạo tò mò mạnh. {item['title']}. Tiếng Việt 100%."
            else:
                focus_arg = f"BẮT BUỘC DÙNG FONT CHỮ: Arial, Roboto, hoặc Noto Sans để hiển thị đúng dấu Tiếng Việt. KHÔNG DÙNG FONT NGHỆ THUẬT GÂY LỖI Ô VUÔNG. Khóa học chuyên sâu. {item['title']}. Tiếng Việt 100%."
            
            try:
                out = run_cmd(["uv", "run", "nlm", "video", "create", nb_id, "--format", nlm_format, "--focus", focus_arg, "--language", lang, "--confirm", "--json"])
                v_data = json.loads(out)
                item["video_id"] = v_data.get("artifact_id", "PENDING")
                save_state(state)
            except Exception as e:
                print(f"  -> Lỗi gọi render, bỏ qua: {e}")
            
            time.sleep(3) # Nghỉ xíu tránh spam API
            
    return state

def download_ready_videos(state):
    nb_id = state["notebook_id"]
    print("[*] Đang bắt đầu vòng lặp kiểm tra trạng thái và tải video (Polling)...")
    
    # Gộp tất cả video vào 1 mảng để tiện kiểm tra
    all_videos = []
    for t in state.get("long_topics", []):
        all_videos.append((t, "output_factory/long_videos"))
    for t in state.get("short_topics", []):
        all_videos.append((t, "output_factory/short_videos"))
        
    pending = [v for v, folder in all_videos if v.get("video_id") and not v.get("video_downloaded")]
    
    if not pending:
        print("  -> Không có video nào đang chờ tải!")
        return state
        
    print(f"  -> Có {len(pending)} video đang trong hàng đợi Render của Google.")
    
    # Cấu trúc polling thực tế sẽ lặp liên tục mỗi 60 giây
    while True:
        pending = [v for v, folder in all_videos if v.get("video_id") and not v.get("video_downloaded")]
        if not pending:
            print("\n[+] TẤT CẢ VIDEO ĐÃ TẢI XONG!")
            break
            
        print(f"\n[*] Đang kiểm tra trạng thái {len(pending)} video...")
        try:
            out = run_cmd(["uv", "run", "nlm", "studio", "status", nb_id, "--json"])
            status_data = json.loads(out)
            
            # Đảm bảo status_data là một list
            if isinstance(status_data, dict) and "jobs" in status_data:
                jobs = status_data["jobs"]
            elif isinstance(status_data, list):
                jobs = status_data
            else:
                jobs = []
                
            for item, out_dir in all_videos:
                v_id = item.get("video_id")
                if v_id and not item.get("video_downloaded"):
                    # Tìm trạng thái của v_id trong status_data
                    job_status = next((j.get("status") for j in jobs if j.get("id") == v_id or j.get("artifact_id") == v_id), "PENDING")
                    
                    if job_status == "completed" or job_status == "DONE":
                        print(f"  [+] Video {item['title']} ĐÃ XONG! Đang tải về...")
                        try:
                            # Tự động tạo thư mục nếu chưa có
                            import os
                            os.makedirs(out_dir, exist_ok=True)
                            
                            out_path = f"{out_dir}/{item['id']}.mp4"
                            run_cmd(["uv", "run", "nlm", "download", "video", nb_id, "--id", v_id, "--output", out_path])
                            item["video_downloaded"] = True
                            save_state(state)
                            print(f"  => Tải thành công {out_path}")
                        except Exception as e:
                            print(f"  -> Lỗi tải video {item['id']}: {e}")
                    elif job_status == "failed" or job_status == "ERROR":
                        print(f"  [!] Video {item['title']} bị LỖI RENDER TỪ GOOGLE! Bỏ qua...")
                        item["video_downloaded"] = True # Đánh dấu là đã xử lý để không bị kẹt loop
                        save_state(state)
                    else:
                        pass # Vẫn đang PENDING hoặc processing, im lặng chờ
                        
        except Exception as e:
            print("  -> Lỗi khi kiểm tra status:", e)
            
        print("[-] Đang chờ 60 giây trước khi quét lại...")
        time.sleep(60)
        
    return state

def main():
    state = load_state()
    if not state.get("notebook_id"):
        print("Chưa có Notebook. Vui lòng chạy Module 1 trước.")
        sys.exit(1)
        
    print("=== BẮT ĐẦU RENDER 20 LONG VIDEOS ===")
    state = render_videos(state, "long_topics", "explainer")
    
    print("=== BẮT ĐẦU RENDER 100 SHORT VIDEOS ===")
    state = render_videos(state, "short_topics", "short")
    
    print("=== KIỂM TRA TRẠNG THÁI VÀ TẢI VỀ (DOWNLOADER) ===")
    download_ready_videos(state)
    
    print("\n[V] MODULE 2 & 3 HOÀN TẤT: Hệ thống đã nạp xong toàn bộ lệnh Render. Đang chờ tải về.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Module 2 & 3: Video Factory Render")
    parser.add_argument("--channel-dir", type=str, default="", help="Thư mục xuất dữ liệu kênh")
    args = parser.parse_args()
    
    if args.channel_dir and os.path.exists(args.channel_dir):
        # Update output paths inside state if channel-dir specified
        pass
        
    main()
