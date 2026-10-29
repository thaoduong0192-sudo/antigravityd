import os
import json
import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NotebookLMBridge")

class NotebookLMBridge:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def generate_cli_script(
        self,
        topic: str,
        youtube_urls: List[str],
        curriculum_filepath: Path
    ) -> Dict[str, str]:
        """Tạo script CLI tự động hóa tạo Notebook & nạp nguồn trên NotebookLM"""
        
        safe_title = topic.replace('"', '\\"')
        urls_args = " ".join([f'"{url}"' for url in youtube_urls])
        
        # 1. Bash / PowerShell CLI Script
        cmd_create = f'notebooklm create --title "Giáo trình 7 Ngày: {safe_title}"'
        cmd_add_yt = f'notebooklm add-source --notebook-title "Giáo trình 7 Ngày: {safe_title}" --type youtube {urls_args}'
        cmd_add_doc = f'notebooklm add-source --notebook-title "Giáo trình 7 Ngày: {safe_title}" --file "{curriculum_filepath.resolve()}"'
        cmd_generate_audio = f'notebooklm generate-audio --notebook-title "Giáo trình 7 Ngày: {safe_title}"'

        script_content_bat = f"""@echo off
echo ===================================================
echo   AUTOMATING NOTEBOOKLM SETUP VIA CLI
echo ===================================================
echo 1. Creating NotebookLM...
{cmd_create}
echo 2. Importing YouTube Video Sources...
{cmd_add_yt}
echo 3. Importing E-Learning Curriculum Document...
{cmd_add_doc}
echo 4. Generating AI Audio Overview / Podcast...
{cmd_generate_audio}
echo ===================================================
echo Done! NotebookLM fully created and ready for E-Learning.
pause
"""

        script_path = self.output_dir / "setup_notebooklm.bat"
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content_bat)

        # 2. Python Script cho Playwright Browser Automation (Khôi phục fallback nếu CLI chập chờn)
        playwright_script = f"""import asyncio
from playwright.async_api import async_playwright

async def automate_notebooklm():
    print("Mở trình duyệt tự động tạo NotebookLM...")
    async with async_playwright() as p:
        # Khởi chạy trình duyệt với Profile người dùng
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.goto("https://notebooklm.google.com/")
        print("Đã mở NotebookLM. Vui lòng kiểm tra màn hình...")
        await page.wait_for_timeout(5000)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(automate_notebooklm())
"""
        playwright_path = self.output_dir / "automate_notebooklm_playwright.py"
        with open(playwright_path, "w", encoding="utf-8") as f:
            f.write(playwright_script)

        return {
            "bat_script": str(script_path),
            "playwright_script": str(playwright_path),
            "cmd_create": cmd_create,
            "cmd_add_yt": cmd_add_yt,
            "cmd_add_doc": cmd_add_doc
        }

    def execute_cli_if_available(self, topic: str, youtube_urls: List[str], curriculum_filepath: Path) -> Optional[str]:
        """Thử chạy lệnh CLI trực tiếp nếu máy đã cài notebooklm-cli"""
        try:
            # Kiểm tra xem notebooklm hoặc nlm command có tồn tại không
            result = subprocess.run(["notebooklm", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("Tìm thấy notebooklm CLI trên hệ thống! Đang tự động chạy lệnh tạo Notebook...")
                
                # Tạo notebook
                create_res = subprocess.run(
                    ["notebooklm", "create", "--title", f"Giáo trình 7 Ngày: {topic}"],
                    capture_output=True, text=True
                )
                logger.info(f"CLI Create Result: {create_res.stdout}")
                return "NotebookLM đã được tự động tạo qua CLI thành công!"
        except Exception:
            logger.info("Máy chưa cài đặt sẵn notebooklm CLI ngầm. Đã tạo file script tự động .bat và .py sẵn sàng thực thi.")
            return None
        return None
