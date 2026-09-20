"""
Module MCP Prompts: Các mẫu tác vụ thông minh định sẵn cho Trợ lý AI
Hỗ trợ sinh viên lập kế hoạch học tập, chiến lược ôn thi và kiểm tra tốt nghiệp.
"""

from typing import Any

SGU_PROMPTS: dict[str, dict[str, Any]] = {
    "plan_weekly_routine": {
        "name": "plan_weekly_routine",
        "description": "Lập kế hoạch phân bổ thời gian tự học và nghỉ ngơi dựa trên thời khóa biểu tuần thực tế của sinh viên",
        "arguments": [
            {
                "name": "target_hours_per_day",
                "description": "Số giờ muốn dành cho tự học mỗi ngày (ví dụ: 3)",
                "required": False,
            }
        ],
        "template": """Bạn là Trợ lý Cố vấn Học tập thông minh của Trường Đại học Sài Gòn (SGU).
Nhiệm vụ của bạn:
1. Hãy gọi công cụ `get_weekly_schedule` để lấy lịch học chi tiết trong tuần của tôi.
2. Xác định các khoảng thời gian trống giữa các ca học và các buổi không có lịch đến trường.
3. Lập một thời gian biểu chi tiết gồm:
   - Các buổi học trực tiếp trên giảng đường (ghi rõ phòng và cơ sở).
   - Khung giờ tự học/làm bài tập nhóm hợp lý.
   - Thời gian nghỉ ngơi, thể thao cân bằng sức khỏe.""",
    },
    "exam_cramming_strategy": {
        "name": "exam_cramming_strategy",
        "description": "Lập chiến lược ôn thi học kỳ nước rút dựa trên lịch thi và số ngày còn lại",
        "arguments": [
            {
                "name": "priority_courses",
                "description": "Tên các môn học cảm thấy yếu nhất cần ưu tiên ôn tập",
                "required": False,
            }
        ],
        "template": """Bạn là Chuyên gia tư vấn ôn thi của sinh viên SGU.
Nhiệm vụ của bạn:
1. Hãy gọi công cụ `get_exam_countdown` để xem chính xác lịch thi và số ngày còn lại của từng môn.
2. Phân loại các môn thi theo độ khẩn cấp (môn thi sớm nhất) và cảnh báo nếu có ngày nào thi nhiều môn.
3. Xây dựng kế hoạch ôn tập theo từng chặng (Milestones) từ hôm nay đến ngày thi môn cuối cùng, chú trọng phân bổ thời gian cho các môn khó.""",
    },
    "graduation_audit": {
        "name": "graduation_audit",
        "description": "Đối soát toàn diện hồ sơ học tập của sinh viên với chuẩn đầu ra tốt nghiệp SGU",
        "arguments": [],
        "template": """Bạn là Cố vấn học vụ SGU.
Nhiệm vụ của bạn:
1. Gọi công cụ `get_student_profile` và `calculate_gpa_summary` để lấy thông tin điểm và số tín chỉ tích lũy.
2. Đọc tài nguyên `sgu://graduation/standards` để lấy điều kiện tốt nghiệp chính thức của trường.
3. Đối chiếu và đưa ra bản báo cáo đánh giá:
   - Tín chỉ: Đã đạt bao nhiêu / 145 tín chỉ? Còn thiếu bao nhiêu?
   - GPA: Hiện tại bao nhiêu? Dự kiến xếp loại tốt nghiệp gì?
   - Các điều kiện cần bổ sung: Chuẩn tiếng Anh TOEIC, chứng chỉ tin học MOS, chuẩn rèn luyện.
   - Lộ trình hành động cho các học kỳ còn lại.""",
    },
}
