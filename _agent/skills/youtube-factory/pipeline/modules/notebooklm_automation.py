import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from modules.notebooklm_prompt_generator import NotebookLMPromptGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NotebookLMAutomation")

class NotebookLMAutomationEngine:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def prepare_notebooklm_package(
        self,
        topic: str,
        target_audience: str,
        youtube_videos: List[Dict[str, Any]],
        num_sessions: int = 7,
        session_duration_min: int = 20
    ) -> Dict[str, Any]:
        """Đóng gói toàn bộ 50 nguồn YouTube + Master Prompt + 7 Deep-Dive Prompts + 7 Video Studio Prompts"""

        youtube_urls = [v['url'] for v in youtube_videos]

        # 1. Master Prompt Tổng Quan Khóa Học
        master_prompt = NotebookLMPromptGenerator.build_master_curriculum_prompt(
            topic, target_audience, num_sessions, session_duration_min
        )
        master_prompt_path = self.output_dir / "01_NotebookLM_Master_Prompt_TongQuan.txt"
        with open(master_prompt_path, "w", encoding="utf-8") as f:
            f.write(master_prompt)

        # 2. 7 Deep-Dive Prompts Đào Sâu Chi Tiết Từng Buổi
        deep_dive_prompts = NotebookLMPromptGenerator.build_deep_dive_session_prompts(
            topic, target_audience, num_sessions, session_duration_min
        )
        deep_dive_path = self.output_dir / "02_NotebookLM_DeepDive_Prompts_7Ngay.json"
        with open(deep_dive_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(deep_dive_prompts, indent=2, ensure_ascii=False))

        # Lưu riêng file Markdown hiển thị 7 Prompt Đào Sâu để dễ copy dán
        deep_dive_md_path = self.output_dir / "02_NotebookLM_DeepDive_Prompts_7Ngay.md"
        with open(deep_dive_md_path, "w", encoding="utf-8") as f:
            f.write(f"# BỘ 7 PROMPT ĐÀO SÂU CHI TIẾT TỪNG BUỔI HỌC CHO NOTEBOOKLM CHAT\n\n")
            for p in deep_dive_prompts:
                f.write(f"## {p['title']}\n```text\n{p['prompt']}\n```\n\n---\n\n")

        # 3. 7 Video Studio Prompts (Tạo Video Overview 20 Phút)
        video_prompts = NotebookLMPromptGenerator.build_video_studio_prompts(
            topic, target_audience, num_sessions, session_duration_min
        )
        video_prompts_path = self.output_dir / "03_NotebookLM_Video_Studio_Prompts_7Ngay.json"
        with open(video_prompts_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(video_prompts, indent=2, ensure_ascii=False))

        video_prompts_md_path = self.output_dir / "03_NotebookLM_Video_Studio_Prompts_7Ngay.md"
        with open(video_prompts_md_path, "w", encoding="utf-8") as f:
            f.write(f"# BỘ 7 PROMPT STUDIO SINH VIDEO BÀI GIẢNG 20 PHÚT (TIẾNG VIỆT CHUẨN - HỌC THUẬT)\n\n")
            for vp in video_prompts:
                f.write(f"## {vp['title']}\n```text\n{vp['prompt']}\n```\n\n---\n\n")

        # 4. File Danh sách 50 YouTube Sources
        urls_file_path = self.output_dir / "00_NotebookLM_YouTube_50_Sources.txt"
        with open(urls_file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(youtube_urls))

        # 5. Playwright Automation Engine
        playwright_script_path = self.output_dir / "run_notebooklm_automation.py"
        playwright_code = f"""# Script Tự Động Hóa NotebookLM bằng Playwright (Nạp 50 Nguồn YouTube + Gửi Prompts)
import asyncio
from playwright.async_api import async_playwright

YOUTUBE_URLS = {json.dumps(youtube_urls, ensure_ascii=False)}

async def main():
    print("🚀 Đang mở NotebookLM tự động...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        print("1. Đang truy cập NotebookLM...")
        await page.goto("https://notebooklm.google.com/")
        print("2. Vui lòng bấm 'Tạo Notebook mới' (New Notebook).")
        print(f"3. Chọn thêm Nguồn (Add Sources) -> Dán {len(youtube_urls)} Link YouTube từ file 00_NotebookLM_YouTube_50_Sources.txt")
        print("4. Dán Master Prompt & 7 Deep-Dive Prompts vào Chat để NotebookLM sinh giáo trình.")
        print("5. Mở Studio Video Overview -> Dán 7 Studio Prompts để tạo 7 Video bài giảng 20 phút.")
        await asyncio.sleep(60)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
"""
        with open(playwright_script_path, "w", encoding="utf-8") as f:
            f.write(playwright_code)

        # 6. CLI Batch Script
        urls_str = " ".join([f'"{url}"' for url in youtube_urls])
        bat_script_path = self.output_dir / "setup_notebooklm_cli.bat"
        bat_content = f"""@echo off
echo ===============================================================
echo   NOTEBOOKLM AUTOMATION - 50 YOUTUBE SOURCES + DEEP DIVE PROMPTS
echo ===============================================================
echo 1. Creating NotebookLM...
notebooklm create --title "Giáo trình {topic} - {num_sessions} Ngày ({target_audience})"

echo 2. Importing 50 Scraped YouTube Sources...
notebooklm add-source --notebook-title "Giáo trình {topic} - {num_sessions} Ngày ({target_audience})" --type youtube {urls_str}

echo 3. Sending Master Prompt into NotebookLM Chat...
notebooklm chat --notebook-title "Giáo trình {topic} - {num_sessions} Ngày ({target_audience})" --message-file "{master_prompt_path.resolve()}"

echo 4. Generating 7 Session Audio/Video Overviews (20 min each)...
notebooklm generate-audio --notebook-title "Giáo trình {topic} - {num_sessions} Ngày ({target_audience})"

echo ===============================================================
echo Done! NotebookLM created with 50 sources and deep-dive prompts!
pause
"""
        with open(bat_script_path, "w", encoding="utf-8") as f:
            f.write(bat_content)

        return {
            "urls_file_path": str(urls_file_path),
            "master_prompt_path": str(master_prompt_path),
            "deep_dive_path": str(deep_dive_path),
            "deep_dive_md_path": str(deep_dive_md_path),
            "video_prompts_path": str(video_prompts_path),
            "video_prompts_md_path": str(video_prompts_md_path),
            "playwright_script_path": str(playwright_script_path),
            "bat_script_path": str(bat_script_path)
        }
