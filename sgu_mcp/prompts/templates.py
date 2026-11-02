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
   - Các buổi học trực tiếp trên giảng đường (ghi rõ phòng và giải mã chính xác cơ sở: C.* là Cơ sở chính 273 An Dương Vương, 1.* là Cơ sở 1 Bà Huyện Thanh Quan, 2.* là Cơ sở 2 Tôn Đức Thắng, 3.* là Cơ sở 3 Ngô Thời Nhiệm, Ph 4.* / 4.* / S_QP* là Trường PTNK TDTT Nguyễn Thị Định).
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
2. Đọc tài nguyên `sgu://graduation/standards` và `sgu://curriculum/it-roadmap` để lấy chuẩn đầu ra và khung chương trình đào tạo theo đúng ngành/khóa học của sinh viên.
3. Đối chiếu và đưa ra bản báo cáo đánh giá khách quan:
   - Tín chỉ: Đối chiếu số tín chỉ tích lũy với khung chương trình đào tạo theo ngành và khóa của sinh viên (ví dụ: Kỹ sư CNTT Khóa 2022 yêu cầu tối thiểu 152 tín chỉ). Nếu chưa xác định được ngành/khóa cụ thể, hãy ghi rõ "Chưa đủ thông tin để xác định số tín chỉ chuẩn".
   - GPA tích lũy: Hiện tại đạt bao nhiêu thang 4? Đạt chuẩn tối thiểu (>= 2.00) chưa? Dự kiến xếp hạng tốt nghiệp.
   - Chuẩn ngoại ngữ và tin học: Căn cứ quy định chuẩn đầu ra theo ngành (Lưu ý: Sinh viên Khoa CNTT được miễn chứng chỉ tin học cơ bản MOS/IC3 theo Quyết định của trường; sinh viên ngành khác áp dụng theo quy định riêng).
   - Trạng thái điều kiện: Nếu dữ liệu điểm hoặc hồ sơ học phần chưa đầy đủ, PHẢI nêu rõ "Chưa đủ thông tin để kết luận điều kiện tốt nghiệp", không tự ý kết luận khi thiếu dữ liệu minh chứng.
   - Lộ trình hành động chi tiết cho các học kỳ còn lại.""",
    },
}
