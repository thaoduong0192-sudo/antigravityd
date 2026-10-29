import sys
import json
import re
import time
import subprocess
import os
from factory_state import load_state, save_state
from modules.youtube_scraper import YouTubeScraper

TOPIC_STATE_PATH = None
TOPIC_DIR_PATH = None

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

def create_metadata_file(path, title, hook, description, tags):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    content = f"TITLE: {title}\nHOOK: {hook}\n\nDESCRIPTION:\n{description}\n\nTAGS: {tags}"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def download_font():
    font_dir = "output_factory/fonts"
    os.makedirs(font_dir, exist_ok=True)
    font_path = os.path.join(font_dir, "times.ttf")
    import urllib.request
    if not os.path.exists(font_path):
        print("[*] Đang tải Font Times New Roman...")
        urllib.request.urlretrieve("https://github.com/google/fonts/raw/main/ofl/tinos/Tinos-Regular.ttf", font_path)
    
    bold_path = os.path.join(font_dir, "timesbd.ttf")
    if not os.path.exists(bold_path):
        urllib.request.urlretrieve("https://github.com/google/fonts/raw/main/ofl/tinos/Tinos-Bold.ttf", bold_path)
        
    italic_path = os.path.join(font_dir, "timesi.ttf")
    if not os.path.exists(italic_path):
        urllib.request.urlretrieve("https://github.com/google/fonts/raw/main/ofl/tinos/Tinos-Italic.ttf", italic_path)
        
    return font_path, bold_path, italic_path

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Content Generator with Phases")
    parser.add_argument("topic", type=str, nargs="?", default="Vibe code", help="Chủ đề chính")
    parser.add_argument("--phase", type=int, default=3, help="Giai đoạn muốn chạy")
    parser.add_argument("--topic-dir", type=str, default="", help="Thư mục topic")
    args, _ = parser.parse_known_args()
    
    topic = args.topic
    phase = args.phase
    print(f"\n======================================")
    print(f"KHỞI ĐỘNG MODULE 1 - PHASE {phase}")
    print(f"CHỦ ĐỀ: {topic.upper()}")
    print(f"======================================\n")

    state = load_state(state_path=TOPIC_STATE_PATH)
    state["topic"] = topic
    
    # 1. TẠO NOTEBOOKLM
    if not state.get("notebook_id"):
        title = f"Content Factory: {topic}"
        print(f"[*] Đang tạo Notebook mới: {title}")
        out = run_cmd(["uv", "run", "nlm", "notebook", "create", title, "--json"])
        data = json.loads(out)
        state["notebook_id"] = data["notebook_id"]
        state["notebook_url"] = data["url"]
        save_state(state, state_path=TOPIC_STATE_PATH)
    nb_id = state["notebook_id"]
    print(f"[*] Đang sử dụng Notebook ID: {nb_id}")
    
    # BƯỚC 0: INSIGHT ANALYSIS
    if not state.get("target_insight"):
        print("[*] Đang phân tích Insight Đối tượng mục tiêu...")
        insight_prompt = f"Phân tích đối tượng mục tiêu cho chủ đề '{topic}'. Nếu đây là học sinh cấp 2 tại Việt Nam, họ thích nghe giọng văn thế nào? Quan tâm điều gì? Đưa ra insight cốt lõi."
        try:
            out = run_cmd(["uv", "run", "nlm", "notebook", "query", nb_id, insight_prompt, "--json"])
            query_data = json.loads(out)
            insight_text = query_data.get("answer", "Học sinh cấp 2 thích tò mò, khám phá, ngôn ngữ dễ hiểu, gần gũi như chơi game.")
        except:
            insight_text = "Học sinh cấp 2 thích tò mò, khám phá, ngôn ngữ dễ hiểu, gần gũi như chơi game."
        
        state["target_insight"] = insight_text
        save_state(state, state_path=TOPIC_STATE_PATH)
        print("  => Đã sinh Insight cốt lõi!")

    insight = state.get("target_insight", "")

    # 2. CÀO & GỘP 150 NGUỒN YOUTUBE
    global TOPIC_DIR_PATH
    source_dir = os.path.join(TOPIC_DIR_PATH, "sources") if TOPIC_DIR_PATH else "output_factory/sources"
    os.makedirs(source_dir, exist_ok=True)
    
    if not state.get("sources_uploaded"):
        print("[*] Đang cào 150 nguồn YouTube và tải Transcript...")
        scraper = YouTubeScraper(max_results=150)
        videos = scraper.scrape_and_process(topic + " english")
        
        chunks = [videos[i:i + 30] for i in range(0, len(videos), 30)]
        for i, chunk in enumerate(chunks, 1):
            file_path = os.path.join(source_dir, f"source_pack_{i}.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                for v in chunk:
                    f.write(f"--- VIDEO: {v['title']} ---\n{v.get('transcript', '')}\n\n")
            
            print(f"  + Đang nạp {file_path} vào NotebookLM...")
            try:
                run_cmd(["uv", "run", "nlm", "source", "add", nb_id, "--file", file_path])
            except Exception as e:
                print(f"  -> Lỗi nạp nguồn {file_path}: {e}")
        
        # Nạp thêm tài liệu chuẩn (Official Docs, Framework)
        print("\n[*] Đang nạp các tài liệu chuẩn (Framework, SGK Antigravity, Sách Claude CEO, Official Docs)...")
        docs = [
            "output_factory/sources/curriculum_framework_v2.md",
            "output_factory/sources/official_docs_pack.txt",
            "C:/Users/US/Downloads/SGK_Antigravity_full_v2 (1).pdf",
            "C:/Users/US/Downloads/Claude-AI-cho-CEO-Thuc-hanh-SP-Public_Final68.pdf"
        ]
        for doc in docs:
            print(f"  + Đang nạp {doc} vào NotebookLM...")
            try:
                run_cmd(["uv", "run", "nlm", "source", "add", nb_id, "--file", doc])
            except Exception as e:
                print(f"  -> Lỗi nạp nguồn {doc}: {e}")
        state["sources_uploaded"] = True
        save_state(state, state_path=TOPIC_STATE_PATH)
        print(f"\n[PHASE 1 HOÀN TẤT] Bạn có thể kiểm tra nguồn tại link NotebookLM sau:")
        print(f"🔗 {state.get('notebook_url')}")
        print(f"\nNếu ổn, hãy gõ: /goal Chạy python module_1_content_gen.py \"{topic}\" --phase 2")
    
    if phase < 2:
        return

    # 3. TRÍCH XUẤT 20 CHỦ ĐỀ VÀ 100 SHORT TOPICS
    if not state.get("long_topics") or not state.get("short_topics"):
        if not state.get("long_topics"):
            print("\n[*] Đang phân tách 20 chủ đề dài...")
            prompt = (
                f"Dựa trên Insight đối tượng: '{insight}' và BẮT BUỘC tuân thủ chặt chẽ cấu trúc 4 Chương trong tài liệu 'curriculum_framework_v2.md' (Tư duy, Kiến trúc, KWSR, 6 bước thực chiến). "
                f"Hãy thiết kế 1 giáo trình 20 bài dài về '{topic}'. Các bài học phải được phân bổ logic theo 4 Chương của Framework. "
                "Trả về CHỈ MỘT MẢNG JSON chứa 20 chuỗi tiêu đề."
            )
            out = run_cmd(["uv", "run", "nlm", "notebook", "query", nb_id, prompt, "--json"])
            try:
                data = json.loads(out)
                titles = json.loads(data.get("answer", "[]"))
            except Exception:
                titles = [f"Bài {i}: Tìm hiểu {topic}" for i in range(1, 21)]
            state["long_topics"] = [{"id": f"L{i:02d}", "title": t, "note_created": False, "video_id": None, "video_downloaded": False} for i, t in enumerate(titles, 1)]
            save_state(state, state_path=TOPIC_STATE_PATH)

        if not state.get("short_topics"):
            print("\n[*] Đang chẻ nhỏ 100 chủ đề ngắn (Micro-topics cho Shorts)...")
            short_prompt = (
                f"Chẻ nhỏ khóa học về '{topic}' thành 100 chủ đề video ngắn (Shorts). "
                "Hook phải cực kỳ giật gân, tò mò mạnh. Trả về MẢNG JSON 100 chuỗi tiêu đề."
            )
            out2 = run_cmd(["uv", "run", "nlm", "notebook", "query", nb_id, short_prompt, "--json"])
            try:
                data2 = json.loads(out2)
                short_titles = json.loads(data2.get("answer", "[]"))
            except Exception:
                short_titles = [f"Bí mật {i} về {topic}" for i in range(1, 101)]
                
            state["short_topics"] = [{"id": f"S{i:03d}", "title": t, "video_id": None, "video_downloaded": False} for i, t in enumerate(short_titles, 1)]
            save_state(state, state_path=TOPIC_STATE_PATH)
            
        print("\n[PHASE 2 HOÀN TẤT] Dàn ý đã được sinh xong. Đây là 5 bài dài và 5 bài ngắn đầu tiên để bạn tham khảo giọng văn:")
        print("LONG TOPICS:")
        for t in state.get("long_topics", [])[:5]:
            print(f" - {t['title']}")
        print("\nSHORT TOPICS:")
        for t in state["short_topics"][:5]:
            print(f" - {t['title']}")
            
        print(f"\nNếu ổn, hãy gõ: /goal Chạy python module_1_content_gen.py \"{topic}\" --phase 3")
        
    if phase < 3:
        return
        
    # TẠO NOTE CHUYÊN SÂU
    if not state.get("long_topics")[0].get("note_created"):
        print("\n[*] Đang sinh Note chuyên sâu cho 20 bài học...")
        for l_topic in state["long_topics"]:
            if not l_topic.get("note_created"):
                print(f"  - Đang viết Note cho: {l_topic['title']}")
                try:
                    note_prompt = f"Viết 1 bài học chi tiết (khoảng 800-1000 chữ) cho chủ đề '{l_topic['title']}'. Áp dụng đúng insight đối tượng sau: '{insight}'. Ngôn ngữ Tiếng Việt 100%. Định dạng markdown rõ ràng."
                    out = run_cmd(["uv", "run", "nlm", "notebook", "query", nb_id, note_prompt, "--json"])
                    try:
                        content = json.loads(out).get("answer", "Lỗi sinh nội dung.")
                    except:
                        content = out
                        
                    l_topic["note_content"] = content
                    l_topic["note_created"] = True
                    save_state(state, state_path=TOPIC_STATE_PATH)
                    time.sleep(2)
                except Exception as e:
                    print(f"  -> Lỗi sinh Note: {e}")
        
    # 5. TẠO EBOOK TỪ 20 NOTE DÀI BẰNG FONT TIMES NEW ROMAN (Tinos)
    if not state.get("ebook_full_created"):
        print("\n[*] Đang tổng hợp E-Book PDF hoàn chỉnh (Sử dụng Font Tiếng Việt chuẩn)...")
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
            from reportlab.pdfbase.pdfmetrics import registerFontFamily
            from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
            
            font_path, bold_path, italic_path = download_font()
            pdfmetrics.registerFont(TTFont('TimesNewRoman', font_path))
            pdfmetrics.registerFont(TTFont('TimesNewRoman-Bold', bold_path))
            pdfmetrics.registerFont(TTFont('TimesNewRoman-Italic', italic_path))
            registerFontFamily('TimesNewRoman', normal='TimesNewRoman', bold='TimesNewRoman-Bold', italic='TimesNewRoman-Italic', boldItalic='TimesNewRoman-Bold')
            
            pdf_path = os.path.join(TOPIC_DIR_PATH, "ebook", "Giao_Trinh_Antigravity_Cap2.pdf") if TOPIC_DIR_PATH else "output_factory/ebook/Giao_Trinh_Antigravity_Cap2.pdf"
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            
            doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle(name='CustomTitle', parent=styles['Title'], fontName='TimesNewRoman-Bold', fontSize=24, spaceAfter=30, alignment=TA_CENTER)
            h1_style = ParagraphStyle(name='CustomH1', parent=styles['Heading1'], fontName='TimesNewRoman-Bold', fontSize=18, spaceBefore=20, spaceAfter=15)
            h2_style = ParagraphStyle(name='CustomH2', parent=styles['Heading2'], fontName='TimesNewRoman-Bold', fontSize=16, spaceBefore=15, spaceAfter=10)
            h3_style = ParagraphStyle(name='CustomH3', parent=styles['Heading3'], fontName='TimesNewRoman-Bold', fontSize=14, spaceBefore=10, spaceAfter=8)
            body_style = ParagraphStyle(name='CustomBody', parent=styles['Normal'], fontName='TimesNewRoman', fontSize=12, leading=18, alignment=TA_JUSTIFY, spaceAfter=10)
            bullet_style = ParagraphStyle(name='CustomBullet', parent=styles['Normal'], fontName='TimesNewRoman', fontSize=12, leading=18, leftIndent=20, spaceAfter=8)
            
            def parse_markdown_to_platypus(text):
                elements = []
                lines = text.split('\n')
                bold_re = re.compile(r'\*\*(.*?)\*\*')
                
                def format_inline(line):
                    line = bold_re.sub(r'<b>\1</b>', line)
                    line = re.sub(r'(?<!\*)\*(?!\s)(.*?)(?<!\s)\*(?!\*)', r'<i>\1</i>', line)
                    line = line.replace('`', '')
                    return line

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    if line == '---':
                        elements.append(Spacer(1, 15))
                        continue
                    if line.startswith('### '):
                        elements.append(Paragraph(format_inline(line[4:].strip()), h3_style))
                    elif line.startswith('## '):
                        elements.append(Paragraph(format_inline(line[3:].strip()), h2_style))
                    elif line.startswith('# '):
                        elements.append(Paragraph(format_inline(line[2:].strip()), h1_style))
                    elif line.startswith('- ') or line.startswith('* '):
                        elements.append(Paragraph(f"&bull; {format_inline(line[2:].strip())}", bullet_style))
                    elif re.match(r'^\d+\.\s', line):
                        prefix = re.match(r'^(\d+\.)\s', line).group(1)
                        elements.append(Paragraph(f"{prefix} {format_inline(line[len(prefix):].strip())}", bullet_style))
                    else:
                        elements.append(Paragraph(format_inline(line), body_style))
                return elements
            
            story = []
            story.append(Paragraph(f"GIÁO TRÌNH: {topic.upper()}", title_style))
            story.append(Spacer(1, 20))
            story.append(PageBreak())
            
            for idx, l_topic in enumerate(state.get("long_topics", [])):
                content = l_topic.get("note_content", "Nội dung bài học đang cập nhật...")
                elements = parse_markdown_to_platypus(f"## {l_topic['title']}\n\n" + content)
                story.extend(elements)
                if idx < len(state.get("long_topics", [])) - 1:
                    story.append(PageBreak())
                
            doc.build(story)
            state["ebook_full_created"] = True
            save_state(state, state_path=TOPIC_STATE_PATH)
            print(f"  => Xuất E-Book thành công tại: {pdf_path}")
        except Exception as e:
            print(f"  -> Lỗi tạo E-Book: {e}")

    print("\n[V] MODULE 1 HOÀN TẤT: Dữ liệu (Insight, 20 Notes, 150 Nguồn, Ebook) đã sẵn sàng.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Module 1: Content Gen")
    parser.add_argument("--topic", type=str, default="Vibe code bằng Antigravity cho Gen Alpha", help="Chủ đề từ khóa")
    parser.add_argument("--target", type=str, default="Học sinh cấp 2 & Phụ huynh", help="Đối tượng học viên")
    parser.add_argument("--output-dir", type=str, default="", help="Thư mục xuất dữ liệu kênh")
    parser.add_argument("--topic-dir", type=str, default="", help="Thư mục của topic")
    args, _ = parser.parse_known_args()
    
    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)
        
    global TOPIC_STATE_PATH, TOPIC_DIR_PATH
    if args.topic_dir:
        TOPIC_STATE_PATH = os.path.join(args.topic_dir, 'factory_state.json')
        TOPIC_DIR_PATH = args.topic_dir
        
    main()
