import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

# Default Curriculum Settings
DEFAULT_SESSIONS_COUNT = 7
DEFAULT_SESSION_DURATION_MIN = 20
DEFAULT_TOTAL_DURATION_MIN = 140

# Curriculum Ratios (Must total 1.0)
RATIO_THEORY = 0.40      # 40% Lý thuyết
RATIO_EXAMPLES = 0.30    # 30% Ví dụ thực tế
RATIO_PRACTICE = 0.30    # 30% Bài tập làm theo & nộp bài

# -------------------------------------------------------------
# YOUTUBE SCRAPER RULES (QUY TẮC CÀO NGUỒN YOUTUBE UY TÍN 150 NGUỒN)
# -------------------------------------------------------------
MAX_YOUTUBE_SOURCES = 150

YOUTUBE_SCRAPER_RULES = {
    "min_sources": 150,
    "prefer_languages": ["vi", "en"], # Cả Việt Nam & Quốc Tế
    "ranking_criteria": [
        "1. Kênh uy tín nhất & Subscriber lớn nhất (Channel Authority)",
        "2. Thời gian ra mắt mới nhất (Recency & Updated Knowledge)",
        "3. Hướng dẫn từ A-Z dễ hiểu, rõ ràng, tính ứng dụng cao",
        "4. Tương thích nhất với đối tượng mục tiêu chỉ định"
    ]
}

# -------------------------------------------------------------
# MULTI-CHANNEL OUTPUT DIRECTORY HELPER
# Cấu hình thư mục theo Số thứ tự & Mã kênh (VD: channel_01_nobocos)
# -------------------------------------------------------------
def get_channel_dir(channel_index: str = "01", channel_id: str = "default") -> Path:
    """ Trả về đường dẫn thư mục riêng cho từng kênh theo STT và Mã kênh """
    clean_id = "".join(c for c in channel_id if c.isalnum() or c in ('_', '-')).lower()
    folder_name = f"channel_{int(channel_index):02d}_{clean_id}"
    channel_dir = BASE_DIR / "output_factory" / folder_name
    
    # Tạo các thư mục con chuẩn
    (channel_dir / "chrome_profile").mkdir(parents=True, exist_ok=True)
    
    return channel_dir

def get_topic_dir(channel_index: str = "01", channel_id: str = "default", topic_index: str = "01", topic_id: str = "default") -> Path:
    """ Trả về đường dẫn thư mục riêng cho từng chủ đề trong kênh """
    channel_dir = get_channel_dir(channel_index, channel_id)
    clean_topic = "".join(c for c in topic_id if c.isalnum() or c in ('_', '-')).lower()
    topic_name = f"topic_{int(topic_index):02d}_{clean_topic}"
    topic_dir = channel_dir / topic_name
    
    for sub in ["long_videos", "short_videos", "metadata", "uploaded", "ebook", "sources"]:
        (topic_dir / sub).mkdir(parents=True, exist_ok=True)
    
    return topic_dir
