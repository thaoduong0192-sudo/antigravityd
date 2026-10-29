import os
import sys
import json
import shutil
import asyncio
import subprocess
import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from config import BASE_DIR, get_channel_dir

app = FastAPI(title="YouTube Factory Control Panel API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global execution logs storage
execution_logs = []

def add_log(msg: str):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {msg}"
    print(log_entry)
    execution_logs.append(log_entry)
    if len(execution_logs) > 500:
        execution_logs.pop(0)

class ChannelConfigModel(BaseModel):
    channel_index: int = 1
    channel_id: str = "nobocos"
    channel_name: str = "Noboco's House"
    topic: str = "Vibe code bằng Antigravity cho Gen Alpha"
    target_audience: str = "Học sinh cấp 2 & Phụ huynh"
    topic_description: str = "Hướng dẫn học sinh cấp 2 tự làm game và giao diện lơ lửng bằng vibe code antigravity"
    desired_outcome: str = "Tự viết được ứng dụng mini và nhận Ebook giáo trình miễn phí"
    language: str = "vi"
    start_date: str = "2026-08-16"

class ModuleRunModel(BaseModel):
    channel_index: int = 1
    channel_id: str = "nobocos"
    topic: str = "Vibe code bằng Antigravity cho Gen Alpha"
    target_audience: str = "Học sinh cấp 2 & Phụ huynh"
    topic_description: str = "Hướng dẫn học sinh cấp 2 tự làm game và giao diện lơ lửng bằng vibe code antigravity"
    desired_outcome: str = "Tự viết được ứng dụng mini và nhận Ebook giáo trình miễn phí"
    start_date: str = "2026-08-16"

@app.post("/api/step1/analyze-keywords")
async def analyze_and_propose_keywords(req: ModuleRunModel):
    """ Điểm Duyệt 1: Dùng Gemini AI phân tích Insight chuyên sâu và Đề xuất từ khóa tìm kiếm """
    add_log(f"🧠 [CHECKPOINT 1] Đang dùng Gemini AI phân tích Insight chuyên sâu cho kênh #{req.channel_index:02d}...")
    add_log(f"  📌 Chủ đề: {req.topic}")
    add_log(f"  🎯 Đối tượng: {req.target_audience}")
    add_log(f"  📝 Mô tả chi tiết: {req.topic_description}")
    add_log(f"  🏆 Kết quả mong muốn: {req.desired_outcome}")
    
    from config import GEMINI_API_KEY
    
    insight_summary = ""
    proposed_yt_keywords = []
    proposed_google_keywords = []
    
    if GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-2.0-flash")
            
            prompt = f"""Bạn là chuyên gia nghiên cứu nội dung YouTube và SEO. Dựa trên 4 thông tin đầu vào sau, hãy phân tích chuyên sâu và trả về JSON:

**1. Chủ đề kênh:** {req.topic}
**2. Đối tượng mục tiêu:** {req.target_audience}
**3. Mô tả chi tiết chủ đề:** {req.topic_description}
**4. Kết quả mong muốn:** {req.desired_outcome}

Hãy trả về JSON duy nhất (không markdown, không ```json```) với cấu trúc:
{{
  "insight": "Phân tích tâm lý, nhu cầu, pain point, ngôn ngữ, sở thích của đối tượng mục tiêu. Giải thích vì sao họ cần nội dung này và cách tiếp cận hiệu quả nhất.",
  "youtube_keywords": ["từ khóa 1", "từ khóa 2", ..., "từ khóa 10"],
  "google_keywords": ["từ khóa 1", "từ khóa 2", ..., "từ khóa 5"]
}}

Yêu cầu:
- youtube_keywords: 10 từ khóa tìm kiếm trên YouTube, NGẮN GỌN (3-8 từ), đúng ngôn ngữ người dùng sẽ gõ, mix cả tiếng Việt và tiếng Anh.
- google_keywords: 5 từ khóa tìm kiếm trên Google để tìm tài liệu chuyên sâu bổ sung.
- insight: 2-4 câu phân tích chất lượng cao về đối tượng."""

            response = model.generate_content(prompt)
            raw_text = response.text.strip()
            # Clean up any markdown code fences
            if raw_text.startswith("```"):
                raw_text = raw_text.split("\n", 1)[1] if "\n" in raw_text else raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            raw_text = raw_text.strip()
            
            result = json.loads(raw_text)
            insight_summary = result.get("insight", "")
            proposed_yt_keywords = result.get("youtube_keywords", [])
            proposed_google_keywords = result.get("google_keywords", [])
            
            add_log(f"[✓] Gemini AI đã phân tích xong! {len(proposed_yt_keywords)} YouTube keywords + {len(proposed_google_keywords)} Google keywords.")
        except Exception as e:
            add_log(f"[!] Lỗi gọi Gemini API: {e}. Chuyển sang chế độ thủ công.")
    
    # Fallback nếu không có API key hoặc lỗi
    if not proposed_yt_keywords:
        add_log("[!] Không có Gemini API key hoặc lỗi API. Dùng logic rút gọn từ chủ đề.")
        # Tách lấy cụm từ ngắn nhất từ topic
        short_topic = req.topic.split(" cho ")[0] if " cho " in req.topic else req.topic
        if len(short_topic) > 30:
            short_topic = " ".join(short_topic.split()[:5])
        proposed_yt_keywords = [
            short_topic,
            f"hướng dẫn {short_topic} cho người mới",
            f"{short_topic} tutorial",
            f"học {short_topic} từ đầu",
            f"dạy {short_topic} dễ hiểu"
        ]
        proposed_google_keywords = [
            f"{short_topic} giáo trình PDF",
            f"{short_topic} tài liệu học",
            f"best {short_topic} course"
        ]
        insight_summary = f"Đối tượng '{req.target_audience}' có nhu cầu tìm hiểu '{short_topic}' với mục tiêu: '{req.desired_outcome}'. Cần cách tiếp cận dễ hiểu, thực hành ngay, phù hợp trình độ ban đầu."

    add_log(f"[⏳] Đang chờ USER DUYỆT từ khóa tại Checkpoint 1 trên giao diện GUI.")
    
    return {
        "status": "pending_approval",
        "insight": insight_summary,
        "youtube_keywords": proposed_yt_keywords,
        "google_keywords": proposed_google_keywords
    }

@app.get("/api/logs")
async def get_logs():
    return {"logs": execution_logs}

@app.get("/api/channels")
async def list_channels():
    factory_dir = BASE_DIR / "output_factory"
    channels = []
    if factory_dir.exists():
        for d in factory_dir.iterdir():
            if d.is_dir() and d.name.startswith("channel_"):
                longs = len(list((d / "long_videos").glob("*.mp4")))
                shorts = len(list((d / "short_videos").glob("*.mp4")))
                uploaded = len(list((d / "uploaded").glob("*.mp4")))
                channels.append({
                    "folder": d.name,
                    "path": str(d),
                    "long_videos": longs,
                    "short_videos": shorts,
                    "uploaded_videos": uploaded
                })
    return {"channels": sorted(channels, key=lambda x: x['folder'])}

@app.post("/api/channel/init")
async def init_channel(config: ChannelConfigModel):
    try:
        c_dir = get_channel_dir(str(config.channel_index), config.channel_id)
        config_path = c_dir / "channel_config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config.dict(), f, ensure_ascii=False, indent=4)
        add_log(f"Đã khởi tạo thư mục kênh #{config.channel_index:02d} ({config.channel_id}) tại: {c_dir}")
        return {"status": "success", "channel_dir": str(c_dir)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/step1/content-gen")
async def run_step1(req: ModuleRunModel, background_tasks: BackgroundTasks):
    def task():
        add_log(f"🚀 BẮT ĐẦU BƯỚC 1: Cào 150 nguồn & Sinh giáo trình cho kênh #{req.channel_index:02d} ({req.topic})...")
        c_dir = get_channel_dir(str(req.channel_index), req.channel_id)
        
        cmd = [
            "uv", "run", "python", "module_1_content_gen.py",
            req.topic
        ]
        try:
            proc = subprocess.Popen(cmd, cwd=str(BASE_DIR), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
            for line in iter(proc.stdout.readline, ''):
                if line.strip():
                    add_log(line.strip())
            proc.wait()
            add_log(f"[✓] HOÀN THÀNH BƯỚC 1 cho kênh #{req.channel_index:02d}!")
        except Exception as e:
            add_log(f"[!] LỖI BƯỚC 1: {e}")

    background_tasks.add_task(task)
    return {"status": "started", "step": 1, "message": "Đã khởi chạy Bước 1 trong background."}

@app.post("/api/step2-3/video-factory")
async def run_step2_3(req: ModuleRunModel, background_tasks: BackgroundTasks):
    def task():
        add_log(f"🎬 BẮT ĐẦU BƯỚC 2-3: Render Video qua NotebookLM cho kênh #{req.channel_index:02d}...")
        c_dir = get_channel_dir(str(req.channel_index), req.channel_id)
        
        cmd = [
            "uv", "run", "python", "module_2_3_video_factory.py",
            "--channel-dir", str(c_dir)
        ]
        try:
            proc = subprocess.Popen(cmd, cwd=str(BASE_DIR), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
            for line in iter(proc.stdout.readline, ''):
                if line.strip():
                    add_log(line.strip())
            proc.wait()
            add_log(f"[✓] HOÀN THÀNH BƯỚC 2-3 cho kênh #{req.channel_index:02d}!")
        except Exception as e:
            add_log(f"[!] LỖI BƯỚC 2-3: {e}")

    background_tasks.add_task(task)
    return {"status": "started", "step": "2-3", "message": "Đã khởi chạy Bước 2-3 trong background."}

@app.post("/api/step4/youtube-bot")
async def run_step4(req: ModuleRunModel, background_tasks: BackgroundTasks):
    def task():
        add_log(f"📤 BẮT ĐẦU BƯỚC 4: Upload & Lên lịch YouTube Studio cho kênh #{req.channel_index:02d} từ ngày {req.start_date}...")
        c_dir = get_channel_dir(str(req.channel_index), req.channel_id)
        
        cmd = [
            "uv", "run", "python", "module_4_youtube_bot.py",
            "--channel-dir", str(c_dir),
            "--start-date", req.start_date
        ]
        try:
            proc = subprocess.Popen(cmd, cwd=str(BASE_DIR), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
            for line in iter(proc.stdout.readline, ''):
                if line.strip():
                    add_log(line.strip())
            proc.wait()
            add_log(f"[✓] HOÀN THÀNH BƯỚC 4 cho kênh #{req.channel_index:02d}!")
        except Exception as e:
            add_log(f"[!] LỖI BƯỚC 4: {e}")

    background_tasks.add_task(task)
    return {"status": "started", "step": 4, "message": "Đã khởi chạy Bước 4 trong background."}

@app.post("/api/step5/auto-mailer")
async def run_step5(req: ModuleRunModel, background_tasks: BackgroundTasks):
    def task():
        add_log(f"✉️ BẮT ĐẦU BƯỚC 5: Lắng nghe & Gửi Auto-Mailer Ebook cho kênh #{req.channel_index:02d}...")
        c_dir = get_channel_dir(str(req.channel_index), req.channel_id)
        
        cmd = [
            "uv", "run", "python", "module_5_auto_mailer.py",
            "--channel-dir", str(c_dir)
        ]
        try:
            proc = subprocess.Popen(cmd, cwd=str(BASE_DIR), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
            for line in iter(proc.stdout.readline, ''):
                if line.strip():
                    add_log(line.strip())
            proc.wait()
            add_log(f"[✓] HOÀN THÀNH BƯỚC 5 cho kênh #{req.channel_index:02d}!")
        except Exception as e:
            add_log(f"[!] LỖI BƯỚC 5: {e}")

    background_tasks.add_task(task)
    return {"status": "started", "step": 5, "message": "Đã khởi chạy Bước 5 trong background."}

# Daemon 24/7 State
daemon_active = False

async def daemon_worker_loop():
    global daemon_active
    add_log("🔄 24/7 Daemon Worker Loop đã được khởi động.")
    while daemon_active:
        try:
            add_log("⏱️ [Daemon 24/7] Đang chạy chu kỳ quét Auto-Mailer & Lên lịch...")
            # 1. Run Auto-Mailer
            cmd_mail = ["uv", "run", "python", "module_5_auto_mailer.py"]
            proc1 = subprocess.Popen(cmd_mail, cwd=str(BASE_DIR), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
            proc1.wait()
            
            # 2. Sleep 15 minutes before next poll cycle
            for _ in range(900):
                if not daemon_active:
                    break
                await asyncio.sleep(1)
        except Exception as e:
            add_log(f"[!] Lỗi Daemon Loop: {e}")
            await asyncio.sleep(60)
            
    add_log("⏹️ [Daemon 24/7] Daemon Worker đã dừng.")

@app.get("/api/daemon/status")
async def daemon_status():
    return {"active": daemon_active}

@app.post("/api/daemon/toggle")
async def daemon_toggle(background_tasks: BackgroundTasks):
    global daemon_active
    daemon_active = not daemon_active
    if daemon_active:
        background_tasks.add_task(daemon_worker_loop)
        return {"status": "started", "active": True, "message": "Đã bật chế độ 24/7 Daemon Worker Mode thành công."}
    else:
        return {"status": "stopped", "active": False, "message": "Đã tắt 24/7 Daemon Worker Mode."}

# Static UI serving
WEB_APP_DIR = Path(__file__).resolve().parent / "web_app"
WEB_APP_DIR.mkdir(exist_ok=True)
app.mount("/", StaticFiles(directory=str(WEB_APP_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Khởi chạy YouTube Factory Control Panel GUI tại: http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
