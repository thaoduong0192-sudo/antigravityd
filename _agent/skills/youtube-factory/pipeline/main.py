import os
import sys
import io
import json
import argparse
from pathlib import Path

# Đảm bảo Windows console hỗ trợ UTF-8 cho Emoji và Tiếng Việt
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from config import OUTPUT_DIR, DEFAULT_SESSIONS_COUNT, DEFAULT_SESSION_DURATION_MIN, MAX_YOUTUBE_SOURCES
from modules.youtube_scraper import YouTubeScraper
from modules.notebooklm_automation import NotebookLMAutomationEngine

console = Console()

def run_pipeline(
    topic: str,
    target_audience: str,
    num_sessions: int = DEFAULT_SESSIONS_COUNT,
    session_duration: int = DEFAULT_SESSION_DURATION_MIN,
    max_videos: int = MAX_YOUTUBE_SOURCES
):
    console.print(Panel.fit(
        f"[bold cyan]HỆ THỐNG CÀO 50 NGUỒN YOUTUBE UY TÍN -> NOTEBOOKLM -> GIÁO TRÌNH & 7 VIDEO BÀI GIẢNG 20 PHÚT[/bold cyan]\n"
        f"[yellow]Chủ đề:[/yellow] {topic}\n"
        f"[yellow]Đối tượng mục tiêu:[/yellow] {target_audience}\n"
        f"[yellow]Số nguồn cào:[/yellow] 50 Nguồn YouTube uy tín nhất (Việt Nam & Quốc Tế, Mới nhất)\n"
        f"[yellow]Lộ trình đào tạo:[/yellow] {num_sessions} ngày (Mỗi video {session_duration} phút - Tổng {num_sessions * session_duration} phút)\n"
        f"[yellow]Cấu trúc bài giảng:[/yellow] 40% Lý thuyết | 30% Ví dụ thực tế | 30% Bài tập nộp bài chấm điểm\n"
        f"[yellow]Style Video:[/yellow] Học thuật, Số liệu rõ ràng, Đồ họa thông tin sinh động, Giọng đọc Tiếng Việt chuẩn",
        title="🎬 Advanced NotebookLM E-Learning Generator",
        border_style="cyan"
    ))

    # BƯỚC 1: Cào 50 nguồn YouTube uy tín nhất
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description=f"[bold green]1/3. Đang cào & xếp hạng 50 nguồn YouTube uy tín nhất cho '{topic}'...", total=None)
        scraper = YouTubeScraper(max_results=max_videos)
        videos = scraper.scrape_and_process(topic)

    if not videos:
        console.print("[bold red]Không tìm thấy video phù hợp trên YouTube. Vui lòng thử từ khóa khác.[/bold red]")
        return

    table = Table(title=f"Top {len(videos)} Nguồn YouTube Uy Tín & Mới Nhất Được Tuyển Chọn")
    table.add_column("STT", justify="center", style="cyan", no_wrap=True)
    table.add_column("Tiêu Đề Video", style="white")
    table.add_column("Kênh YouTube", style="magenta")
    table.add_column("Lượt Xem", justify="right", style="yellow")
    table.add_column("Ngày Ra Mắt", justify="center", style="blue")

    for i, v in enumerate(videos[:15], 1): # Hiển thị 15 dòng mẫu
        table.add_row(
            str(i),
            v['title'][:50] + "..." if len(v['title']) > 50 else v['title'],
            v['uploader'],
            f"{v['view_count']:,}" if isinstance(v['view_count'], int) else "N/A",
            str(v['upload_date'])
        )
    console.print(table)
    if len(videos) > 15:
        console.print(f"[dim]... và {len(videos) - 15} nguồn YouTube uy tín khác đã được lưu vào file nguồn.[/dim]\n")

    # BƯỚC 2 & 3: Đóng gói Nguồn YouTube & Tạo Master Prompt + 7 Prompt Đào Sâu + 7 Prompt Video Studio
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description=f"[bold green]2/3. Đang tạo Bộ Master Prompt & 7 Prompt Đào Sâu + 7 Studio Prompts...", total=None)
        engine = NotebookLMAutomationEngine(output_dir=OUTPUT_DIR)
        package_info = engine.prepare_notebooklm_package(
            topic=topic,
            target_audience=target_audience,
            youtube_videos=videos,
            num_sessions=num_sessions,
            session_duration_min=session_duration
        )

    # BƯỚC 4: Hiển Thị Hướng Dẫn & Bộ File Prompt Xuất Ra
    console.print(Panel(
        f"[bold green]🎉 ĐÃ TẠO XONG TRỌN BỘ FILE ĐẦU VÀO CAO CẤP CHO NOTEBOOKLM![/bold green]\n\n"
        f"[bold white]1. File Danh Sách {len(videos)} Nguồn YouTube Uy Tín (Việt Nam & Quốc Tế):[/bold white]\n"
        f"   📁 [yellow]{package_info['urls_file_path']}[/yellow]\n\n"
        f"[bold white]2. File Master Prompt Tổng Quan Khóa Học 7 Ngày (Tiếng Việt):[/bold white]\n"
        f"   📁 [yellow]{package_info['master_prompt_path']}[/yellow]\n\n"
        f"[bold white]3. Bộ 7 Prompts Đào Sâu Chi Tiết Từng Buổi (Chat NotebookLM):[/bold white]\n"
        f"   📁 Markdown: [yellow]{package_info['deep_dive_md_path']}[/yellow]\n"
        f"   📁 JSON: [dim]{package_info['deep_dive_path']}[/dim]\n\n"
        f"[bold white]4. Bộ 7 Prompts Video Studio (Tạo 7 Video Bài Giảng 20 Phút - Học Thuật & Đồ Họa):[/bold white]\n"
        f"   📁 Markdown: [yellow]{package_info['video_prompts_md_path']}[/yellow]\n"
        f"   📁 JSON: [dim]{package_info['video_prompts_path']}[/dim]\n\n"
        f"[bold white]5. Script Tự Động Hóa NotebookLM (CLI / Playwright):[/bold white]\n"
        f"   📁 Batch CLI: [cyan]{package_info['bat_script_path']}[/cyan]\n"
        f"   📁 Playwright Automation: [cyan]{package_info['playwright_script_path']}[/cyan]\n\n"
        f"[bold yellow]👉 QUY TRÌNH THỰC HIỆN TRÊN NOTEBOOKLM:[/bold yellow]\n"
        f"   1. Nạp toàn bộ {len(videos)} Link YouTube trong file `00_NotebookLM_YouTube_50_Sources.txt` vào Nguồn của NotebookLM.\n"
        f"   2. Dán Master Prompt trong file `01_NotebookLM_Master_Prompt_TongQuan.txt` vào Chat để tạo tổng quan 7 ngày.\n"
        f"   3. Dán từng Prompt trong `02_NotebookLM_DeepDive_Prompts_7Ngay.md` vào Chat để sinh bài giảng sâu cho Buổi 1 -> Buổi 7.\n"
        f"   4. Mở phần Studio Video Overview -> Dán từng Prompt trong `03_NotebookLM_Video_Studio_Prompts_7Ngay.md` để sinh 7 Video bài giảng 20 phút (Style Học thuật, Đồ họa thông tin, Giọng đọc Tiếng Việt chuẩn) và tải về!",
        title="🚀 KẾT QUẢ ĐẦU RA CAO CẤP NOTEBOOKLM",
        border_style="green"
    ))

def main():
    parser = argparse.ArgumentParser(description="Tool Cào 50 Nguồn YouTube Uy Tín -> Nạp NotebookLM -> Sinh Giáo Trình & 7 Video 20 Phút")
    parser.add_argument("--topic", "-t", type=str, default="Python Automation for Beginners", help="Chủ đề từ khóa cần cào video YouTube")
    parser.add_argument("--target", "-a", type=str, default="Sinh viên & Người đi làm bận rộn", help="Đối tượng học viên chỉ định")
    parser.add_argument("--sessions", "-s", type=int, default=7, help="Số buổi đào tạo (Mặc định 7)")
    parser.add_argument("--duration", "-d", type=int, default=20, help="Thời lượng mỗi video buổi học tính bằng phút (Mặc định 20)")
    parser.add_argument("--max-videos", "-m", type=int, default=50, help="Số lượng video YouTube tối đa cần cào bỏ vào Nguồn NotebookLM (Mặc định 50)")

    args = parser.parse_args()
    run_pipeline(
        topic=args.topic,
        target_audience=args.target,
        num_sessions=args.sessions,
        session_duration=args.duration,
        max_videos=args.max_videos
    )

if __name__ == "__main__":
    main()
