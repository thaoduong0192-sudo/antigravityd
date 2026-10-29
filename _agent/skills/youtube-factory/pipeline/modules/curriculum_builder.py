import os
import json
import logging
from typing import List, Dict, Any
import google.generativeai as genai
from config import GEMINI_API_KEY, RATIO_THEORY, RATIO_EXAMPLES, RATIO_PRACTICE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CurriculumBuilder")

class CurriculumBuilder:
    def __init__(self, api_key: str = GEMINI_API_KEY):
        self.api_key = api_key
        if self.api_key:
            genai.configure(api_key=self.api_key)
            # Dùng mô hình Gemini 1.5/2.0
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    def build_curriculum_prompt(
        self,
        topic: str,
        target_audience: str,
        videos: List[Dict[str, Any]],
        num_sessions: int = 7,
        session_duration_min: int = 20
    ) -> str:
        """Tạo prompt chi tiết chuẩn hóa cấu trúc 40 - 30 - 30"""
        
        theory_min = int(session_duration_min * RATIO_THEORY)
        examples_min = int(session_duration_min * RATIO_EXAMPLES)
        practice_min = int(session_duration_min * RATIO_PRACTICE)

        videos_summary = []
        for idx, v in enumerate(videos, 1):
            videos_summary.append(f"[{idx}] Tiêu đề: {v['title']}\n    URL: {v['url']}\n    Tóm tắt Phụ đề: {v['transcript'][:500]}...\n")

        prompt = f"""
Bạn là một Chuyên gia Thiết kế Giáo trình E-Learning (Instructional Designer) hàng đầu.
Nhiệm vụ của bạn là tổng hợp các video YouTube dưới đây để tạo ra một **GIÁO TRÌNH ĐÀO TẠO {num_sessions} BUỔI** chuẩn hóa.

### THÔNG TIN ĐẦU VÀO:
- **Chủ đề khóa học**: {topic}
- **Đối tượng học viên**: {target_audience}
- **Số buổi đào tạo**: {num_sessions} buổi
- **Thời lượng mỗi buổi**: {session_duration_min} phút (Tổng thời lượng: {num_sessions * session_duration_min} phút)
- **Cấu trúc NGUYÊN TẮC BẮT BUỘC cho MỖI BUỔI HỌC (Tổng {session_duration_min} phút)**:
  1. **40% LÝ THUYẾT ({theory_min} phút)**: Khái niệm cốt lõi, tư duy nền tảng, các mốc thời gian/video cần xem.
  2. **30% VÍ DỤ THỰC TẾ ({examples_min} phút)**: Case study minh họa, tình huống thực tế áp dụng, phân tích bảng mẫu/demo.
  3. **30% BÀI TẬP LÀM THEO & CHẤM ĐIỂM ({practice_min} phút)**: Bài tập thực hành từng bước (Step-by-step Hands-on), tiêu chí chấm điểm chi tiết (Rubric) để học viên làm theo và gửi bài chấm điểm.

---
### DANH SÁCH VIDEO YOUTUBE THAM CHIẾU:
{"".join(videos_summary)}

---
### YÊU CẦU ĐẦU RA (ĐỊNH DẠNG MARKDOWN):

Hãy xuất giáo trình hoàn chỉnh bằng định dạng Markdown cấu trúc chuẩn bao gồm:
1. **Tiêu đề khóa học**: Chuẩn hóa cho đối tượng {target_audience}.
2. **Mục tiêu đầu ra (Learning Outcomes)** sau {num_sessions} buổi.
3. **Chi tiết {num_sessions} Buổi học**, trong mỗi Buổi học PHẢI phân chia đúng 3 phần:
   - **Phần 1: Lý thuyết ({theory_min} phút)**
     - Trích dẫn chính xác Link Video YouTube tham chiếu (URL từ danh sách trên).
     - Kiến thức trọng tâm.
   - **Phần 2: Ví dụ thực tế ({examples_min} phút)**
     - Tình huống áp dụng thực tiễn phù hợp với {target_audience}.
   - **Phần 3: Bài tập thực hành & Tiêu chí chấm điểm ({practice_min} phút)**
     - Nhiệm vụ học viên phải nộp.
     - Tiêu chí chấm điểm (Rubric từ 1 - 10 điểm).
4. **Hướng dẫn tương tác với NotebookLM**: Đặt các câu hỏi gợi ý (Prompts) để học viên hỏi trực tiếp NotebookLM dựa trên tài liệu khóa học.

Hãy trình bày ngôn ngữ tiếng Việt chuyên nghiệp, hấp dẫn và mạch lạc.
"""
        return prompt

    def generate_curriculum(
        self,
        topic: str,
        target_audience: str,
        videos: List[Dict[str, Any]],
        num_sessions: int = 7,
        session_duration_min: int = 20
    ) -> str:
        prompt = self.build_curriculum_prompt(topic, target_audience, videos, num_sessions, session_duration_min)
        
        if not self.model:
            logger.warning("Chưa cấu hình GEMINI_API_KEY. Sinh giáo trình mẫu theo cấu trúc chuẩn...")
            return self._generate_fallback_curriculum(topic, target_audience, videos, num_sessions, session_duration_min)

        logger.info("Đang sinh giáo trình tự động bằng Gemini AI...")
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Lỗi khi gọi Gemini API: {e}. Chuyển sang fallback template.")
            return self._generate_fallback_curriculum(topic, target_audience, videos, num_sessions, session_duration_min)

    def _generate_fallback_curriculum(
        self,
        topic: str,
        target_audience: str,
        videos: List[Dict[str, Any]],
        num_sessions: int = 7,
        session_duration_min: int = 20
    ) -> str:
        theory_min = int(session_duration_min * RATIO_THEORY)
        examples_min = int(session_duration_min * RATIO_EXAMPLES)
        practice_min = int(session_duration_min * RATIO_PRACTICE)

        content = f"# GIÁO TRÌNH ĐÀO TẠO E-LEARNING: {topic.upper()}\n"
        content += f"**Đối tượng hướng tới**: {target_audience}\n"
        content += f"**Cấu trúc khóa học**: {num_sessions} buổi x {session_duration_min} phút/buổi (Tổng {num_sessions * session_duration_min} phút)\n\n"

        content += "## DANH SÁCH TÀI LIỆU VIDEO YOUTUBE NGUỒN\n"
        for v in videos:
            content += f"- [{v['title']}]({v['url']})\n"
        content += "\n---\n"

        for session_idx in range(1, num_sessions + 1):
            ref_video = videos[(session_idx - 1) % len(videos)] if videos else {'title': 'Video tổng hợp', 'url': 'https://youtube.com'}
            content += f"## BUỔI {session_idx}: CHUYÊN ĐỀ PHẦN {session_idx} - {topic.upper()}\n"
            content += f"### 📌 1. LÝ THUYẾT CỐT LÕI ({theory_min} Phút - 40%)\n"
            content += f"- **Video bài giảng tham chiếu**: [{ref_video['title']}]({ref_video['url']})\n"
            content += f"- **Nội dung trọng tâm**: Nắm vững nguyên lý và phương pháp luận chính cho đối tượng {target_audience}.\n"
            content += f"- **Key Takeaways**: Các bước triển khai cốt lõi và thuật ngữ quan trọng.\n\n"

            content += f"### 💡 2. VÍ DỤ THỰC TẾ ({examples_min} Phút - 30%)\n"
            content += f"- **Case Study Thực Tiễn**: Phân tích dự án/tình huống thực tế liên quan đến {topic}.\n"
            content += f"- **Minh Họa Áp Dụng**: Mẫu báo cáo và quy trình xử lý lỗi thực tế.\n\n"

            content += f"### 📝 3. BÀI TẬP LÀM THEO & CHẤM ĐIỂM ({practice_min} Phút - 30%)\n"
            content += f"- **Nhiệm vụ thực hành**: Học viên thực hiện lại các thao tác dựa trên Video nguồn [{ref_video['title']}].\n"
            content += f"- **Yêu cầu nộp bài**: Chụp ảnh màn hình kết quả hoặc đính kèm file sản phẩm.\n"
            content += f"- **Tiêu chí chấm điểm (Rubric)**:\n"
            content += f"  - Đúng định dạng & yêu cầu (40%)\n"
            content += f"  - Tính hoàn thiện & chính xác (40%)\n"
            content += f"  - Sáng tạo / Cải tiến (20%)\n\n"
            content += "---\n\n"

        content += "## HƯỚNG DẪN TƯƠNG TÁC VỚI NOTEBOOKLM\n"
        content += "Học viên có thể copy tài liệu này và nguồn YouTube vào NotebookLM để hỏi các câu hỏi mẫu sau:\n"
        content += "1. *'Tóm tắt 3 điểm cốt lõi của Buổi 1 dưới dạng bảng.'*\n"
        content += "2. *'Giải thích lại bài tập Buổi 2 và cho tôi gợi ý giải.'*\n"
        content += "3. *'Hãy tạo Podcast AI giải thích chủ đề này bằng giọng đọc dễ hiểu.'*\n"

        return content
