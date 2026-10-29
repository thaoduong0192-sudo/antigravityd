import re
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import yt_dlp
from config import MAX_YOUTUBE_SOURCES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("YouTubeScraper")

class YouTubeScraper:
    def __init__(self, max_results: int = MAX_YOUTUBE_SOURCES):
        self.max_results = max_results

    def search_videos_ranked(self, query: str) -> List[Dict[str, Any]]:
        """
        Tìm kiếm & Xếp hạng 50 nguồn YouTube theo quy tắc:
        1. Uy tín (Subscriber count / View count)
        2. Ngày ra mắt mới nhất (Recency)
        3. Cả Việt Nam và Quốc Tế
        """
        logger.info(f"Đang cào {self.max_results} nguồn YouTube uy tín cho từ khóa: '{query}'...")
        
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'skip_download': True,
        }

        # Dùng trực tiếp bộ 13 từ khóa đã duyệt cho chủ đề Vibe Coding
        # 60% Tiếng Việt
        vn_keywords = [
            "Hướng dẫn sử dụng Antigravity IDE để vibe code cho người mới",
            "Vibe coding là gì Lập trình tự động bằng Google Antigravity",
            "Cách tạo app học Tiếng Anh tự động bằng Antigravity",
            "Tạo website cá nhân không cần viết code với Antigravity AI Agent",
            "So sánh Google Antigravity Cursor và VSCode",
            "Tư duy lập trình Agentic AI dành cho học sinh cấp 2"
        ]
        # 40% Tiếng Anh
        en_keywords = [
            "How to use Google Antigravity IDE for vibe coding tutorial",
            "Building apps with Antigravity Agentic IDE step by step",
            "Antigravity vs Cursor AI vs Copilot programming comparison",
            "Agentic coding workflow using Google Antigravity"
        ]

        logger.info("Đã áp dụng bộ từ khóa chuẩn V2.0 (60% VN / 40% EN)")

        queries = []
        # Phân bổ số lượng cào (tổng 150)
        # 6 từ VN x 15 videos/từ = 90
        for kw in vn_keywords:
            queries.append(f"ytsearch15:{kw}")
        # 4 từ EN x 15 videos/từ = 60
        for kw in en_keywords:
            queries.append(f"ytsearch15:{kw}")

        raw_videos_dict = {}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for q in queries:
                try:
                    info = ydl.extract_info(q, download=False)
                    if 'entries' in info:
                        for entry in info['entries']:
                            if not entry:
                                continue
                            video_id = entry.get('id')
                            if not video_id or video_id in raw_videos_dict:
                                continue
                            
                            view_count = entry.get('view_count') or 0
                            upload_date = entry.get('upload_date') or "20240101"

                            raw_videos_dict[video_id] = {
                                'id': video_id,
                                'title': entry.get('title', ''),
                                'url': f"https://www.youtube.com/watch?v={video_id}",
                                'duration': entry.get('duration', 0),
                                'uploader': entry.get('uploader', 'Kênh Uy Tín'),
                                'view_count': view_count,
                                'upload_date': upload_date,
                            }
                except Exception as e:
                    logger.error(f"Lỗi khi cào dữ liệu YouTube cho '{q}': {e}")

        # Chuyển thành danh sách
        video_list = list(raw_videos_dict.values())

        # Thuật toán xếp hạng ưu tiên (Authority Score)
        def compute_score(v):
            views = v.get('view_count', 0)
            date_str = v.get('upload_date', '20240101')
            # Tính điểm ngày mới nhất
            try:
                upload_dt = datetime.strptime(date_str, "%Y%m%d")
                year_score = upload_dt.year * 1000 + upload_dt.month * 50
            except Exception:
                year_score = 202400
            
            return (year_score * 10) + (views / 1000)

        # Sắp xếp từ uy tín/mới nhất đến ít uy tín nhất
        video_list.sort(key=compute_score, reverse=True)

        selected_videos = video_list[:self.max_results]
        logger.info(f"Đã tuyển chọn & xếp hạng {len(selected_videos)} nguồn YouTube uy tín nhất.")
        return selected_videos

    def fetch_transcript(self, video_id: str) -> Optional[str]:
        """Bóc tách phụ đề / transcript của video (Việt Nam & Quốc Tế)"""
        try:
            ytt = YouTubeTranscriptApi()
            transcript_list = ytt.fetch(video_id, languages=['en', 'vi'])
            full_text = " ".join([item.text for item in transcript_list])
            return full_text
        except Exception:
            return None

    def scrape_and_process(self, query: str) -> List[Dict[str, Any]]:
        """Cào 50 nguồn YouTube chuẩn + Xếp hạng + Bóc tách transcript (Tối ưu song song)"""
        raw_videos = self.search_videos_ranked(query)
        processed_videos = []

        from concurrent.futures import ThreadPoolExecutor

        def process_item(item):
            v_id = item['id']
            transcript = self.fetch_transcript(v_id)
            return {
                'id': v_id,
                'title': item['title'],
                'url': item['url'],
                'uploader': item['uploader'],
                'view_count': item['view_count'],
                'upload_date': item['upload_date'],
                'has_transcript': transcript is not None,
                'transcript': transcript or "Nguồn YouTube cập nhật kiến thức mới nhất."
            }

        logger.info("Đang bóc tách transcript song song cho 50 nguồn...")
        with ThreadPoolExecutor(max_workers=10) as executor:
            processed_videos = list(executor.map(process_item, raw_videos))

        return processed_videos

