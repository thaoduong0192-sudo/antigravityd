from typing import List, Dict, Any
from config import VIDEO_STUDIO_RULES

class NotebookLMPromptGenerator:
    """Bộ sinh Prompt chuyên sâu Tiếng Việt cho NotebookLM Chat & Studio Video Overview"""

    @staticmethod
    def build_master_curriculum_prompt(
        topic: str,
        target_audience: str,
        num_sessions: int = 7,
        session_duration_min: int = 20
    ) -> str:
        """Prompt Master Tổng Quan cho toàn bộ khóa học 7 buổi"""
        return f"""Dựa vào TẤT CẢ 50 nguồn YouTube uy tín mới nhất được cung cấp làm Nguồn (Sources), hãy đóng vai Chuyên gia Đào tạo & Thiết kế Giáo trình E-Learning (Instructional Designer) hàng đầu để tạo ra một **BẢN GIÁO TRÌNH TỔNG QUAN TOÀN KHÓA HỌC {num_sessions} NGÀY** hoàn chỉnh về chủ đề: "{topic}".

### THÔNG TIN KHÓA HỌC:
- **Chủ đề**: {topic}
- **Đối tượng học viên**: {target_audience}
- **Tổng thời lượng**: {num_sessions} ngày x {session_duration_min} phút = {num_sessions * session_duration_min} phút bài giảng.
- **Ngôn ngữ xuất ra**: TIẾNG VIỆT HOÀN TOÀN (100%).

---
### NGUYÊN TẮC BẮT BUỘC CHO MỖI NGÀY HỌC (TỔNG 100% THỜI LƯỢNG):
1. **40% LÝ THUYẾT CỐT LÕI ({int(session_duration_min * 0.4)} phút)**:
   - Trình bày kiến thức nền tảng, khái niệm chuẩn học thuật.
   - Trích dẫn số liệu, nguyên lý và mốc video tham chiếu cụ thể.
2. **30% VÍ DỤ THỰC TẾ MINH HỌA ({int(session_duration_min * 0.3)} phút)**:
   - Case study thực tiễn, phân tích tình huống thực tế áp dụng cho {target_audience}.
   - Trực quan hóa dưới dạng Đồ họa thông tin (Infographics), sơ đồ, bảng biểu dữ liệu.
3. **30% BÀI TẬP LÀM THEO & NỘP BÀI CHẤM ĐIỂM ({int(session_duration_min * 0.3)} phút)**:
   - Hướng dẫn thực hành từng bước (Step-by-step Hands-on) để học viên làm theo.
   - Thang điểm và Tiêu chí chấm điểm (Grading Rubric 1 - 10 điểm) rõ ràng.

---
### YÊU CẦU TRÌNH BÀY:
Hãy lập Bảng Lộ Trình Đào Tạo 7 Ngày và Tóm Tắt Mục Tiêu Đầu Ra (Learning Outcomes) sắc nét cho học viên là {target_audience}.
"""

    @staticmethod
    def build_deep_dive_session_prompts(
        topic: str,
        target_audience: str,
        num_sessions: int = 7,
        session_duration_min: int = 20
    ) -> List[Dict[str, Any]]:
        """Sinh 7 Prompts Đào Sâu Chi Tiết từng buổi 1 cho NotebookLM Chat"""
        prompts = []
        for day in range(1, num_sessions + 1):
            prompt_text = f"""Dựa vào các nguồn YouTube đã cung cấp, hãy biên soạn bài giảng ĐÀO SÂU CHI TIẾT VÀ ĐẦY ĐỦ NHẤT cho **NGÀY HỌC THỨ {day}/{num_sessions}** của khóa học "{topic}" dành cho đối tượng {target_audience}.

YÊU CẦU NỘI DUNG CHI TIẾT BÀI HỌC NGÀY {day} ({session_duration_min} PHÚT):

1. **PHẦN 1: LÝ THUYẾT CỐT LÕI & SỐ LIỆU CHUYÊN SÂU (40% - {int(session_duration_min * 0.4)} Phút)**
   - Giải thích chi tiết các thuật ngữ, nguyên lý chuyên môn liên quan đến Ngày {day}.
   - Trích dẫn các số liệu, dẫn chứng thực nghiệm và công thức/quy trình từ các video nguồn.
   - Đưa ra mốc tham chiếu cụ thể để học viên tự xem lại.

2. **PHẦN 2: VÍ DỤ THỰC TẾ & MÔ HÌNH ĐỒ HỌA THÔNG TIN (30% - {int(session_duration_min * 0.3)} Phút)**
   - Phân tích 2-3 Ví dụ thực tế/Case Study thực chiến minh họa cho bài học Ngày {day}.
   - Trình bày thông tin dạng Đồ họa chữ (Infographic Text Diagram), Bảng so sánh hoặc Quy trình xử lý lỗi thực tế.

3. **PHẦN 3: BÀI TẬP THỰC HÀNH LÀM THEO & BÀI NỘP CHẤM ĐIỂM (30% - {int(session_duration_min * 0.3)} Phút)**
   - Đề bài thực hành chi tiết từng bước (Step 1, Step 2, Step 3...).
   - Sản phẩm đầu ra yêu cầu học viên nộp (File / Ảnh chụp màn hình / Báo cáo).
   - Bảng tiêu chí chấm điểm (Rubric):
     * Đúng yêu cầu kỹ thuật & định dạng (4 điểm)
     * Mức độ hoàn thiện & chính xác dữ liệu (4 điểm)
     * Tính ứng dụng & cải tiến sáng tạo (2 điểm)

Ngôn ngữ xuất ra hoàn toàn bằng TIẾNG VIỆT, chuyên nghiệp, dài và chi tiết.
"""
            prompts.append({
                "day": day,
                "title": f"Prompt Đào Sâu Chi Tiết - Bài Học Ngày {day}",
                "prompt": prompt_text
            })
        return prompts

    @staticmethod
    def build_video_studio_prompts(
        topic: str,
        target_audience: str,
        num_sessions: int = 7,
        session_duration_min: int = 20
    ) -> List[Dict[str, Any]]:
        """Sinh 7 Prompts Chuẩn Rule cho Video Overview Studio của NotebookLM"""
        video_prompts = []
        for day in range(1, num_sessions + 1):
            prompt_text = f"""Hãy đóng vai 2 Giảng viên AI xuất sắc của NotebookLM và tạo VIDEO BÀI GIẢNG CHI TIẾT (Audio/Video Overview) cho **BÀI HỌC NGÀY {day}/{num_sessions}** chủ đề: "{topic}".

QUY TẮC TẠO VIDEO BÀI GIẢNG BẮT BUỘC:
- **Thời lượng**: ~{session_duration_min} phút.
- **Phong cách bài giảng**: {VIDEO_STUDIO_RULES['style']}.
- **Giọng đọc**: {VIDEO_STUDIO_RULES['tone_voice']}.
- **Yếu tố hình ảnh & Dữ liệu**: {VIDEO_STUDIO_RULES['visual_elements']}.
- **Dẫn chứng**: {VIDEO_STUDIO_RULES['evidence']}.
- **Ngôn ngữ**: {VIDEO_STUDIO_RULES['language']}.

CẤU TRÚC KỊCH BẢN VIDEO BÀI GIẢNG NGÀY {day}:
- **00:00 - 08:00 (40%)**: Giảng giải Lý thuyết cốt lõi, trích dẫn số liệu và kiến thức nền tảng cho {target_audience}.
- **08:00 - 14:00 (30%)**: Phân tích Ví dụ thực tế minh họa, mô tả Đồ họa thông tin và Case study thực chiến.
- **14:00 - 20:00 (30%)**: Hướng dẫn Bài tập làm theo từng bước và phổ biến tiêu chí nộp bài chấm điểm.
"""
            video_prompts.append({
                "day": day,
                "title": f"Prompt Studio Sinh Video Bài Giảng Ngày {day} ({session_duration_min} Phút)",
                "prompt": prompt_text
            })
        return video_prompts
