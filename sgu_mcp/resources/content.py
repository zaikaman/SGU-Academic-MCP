"""
Module MCP Resources: Tài nguyên tĩnh và ngữ cảnh đào tạo SGU
Cho phép AI Client đọc trực tiếp tài liệu quy chế, sơ đồ đào tạo, chuẩn đầu ra qua URI.
"""

import json

SGU_RESOURCES = {
    "sgu://curriculum/it-roadmap": {
        "name": "Chương trình đào tạo Kỹ sư Công nghệ Thông tin SGU",
        "mimeType": "application/json",
        "description": "Toàn bộ lộ trình 8 học kỳ và các môn học bắt buộc của khoa CNTT Trường ĐH Sài Gòn",
        "content": json.dumps(
            {
                "truong": "Trường Đại học Sài Gòn (SGU)",
                "khoa": "Công nghệ Thông tin",
                "nganh": "Công nghệ Thông tin",
                "he_dao_tao": "Kỹ sư chính quy",
                "tong_tin_chi": 145,
                "lo_trinh_hoc_ky": {
                    "Học kỳ 1": [
                        "Nhập môn lập trình (3TC)",
                        "Đại số tuyến tính (3TC)",
                        "Giải tích 1 (3TC)",
                        "Triết học Mác - Lênin (3TC)",
                        "Tiếng Anh 1 (3TC)",
                    ],
                    "Học kỳ 2": [
                        "Kỹ thuật lập trình (3TC)",
                        "Cấu trúc rời rạc (3TC)",
                        "Giải tích 2 (3TC)",
                        "Vật lý đại cương (3TC)",
                        "Tiếng Anh 2 (3TC)",
                    ],
                    "Học kỳ 3": [
                        "Cấu trúc dữ liệu và giải thuật (4TC)",
                        "Lập trình hướng đối tượng (3TC)",
                        "Cơ sở dữ liệu (3TC)",
                        "Xác suất thống kê (3TC)",
                    ],
                    "Học kỳ 4": [
                        "Hệ điều hành (3TC)",
                        "Mạng máy tính (3TC)",
                        "Hệ quản trị cơ sở dữ liệu (3TC)",
                        "Kiến trúc máy tính (3TC)",
                    ],
                    "Học kỳ 5": [
                        "Công nghệ phần mềm (3TC)",
                        "Lập trình mạng (3TC)",
                        "Trí tuệ nhân tạo (3TC)",
                        "An toàn thông tin (3TC)",
                    ],
                    "Học kỳ 6": [
                        "Các công nghệ lập trình hiện đại (3TC)",
                        "Phát triển ứng dụng Web nâng cao (3TC)",
                        "Học máy (3TC)",
                        "Điện toán đám mây (3TC)",
                    ],
                    "Học kỳ 7": [
                        "Thực tập doanh nghiệp (4TC)",
                        "Chuyên đề phát triển ứng dụng di động (3TC)",
                        "Quản trị dự án CNTT (3TC)",
                    ],
                    "Học kỳ 8": [
                        "Khóa luận tốt nghiệp (10TC) hoặc Học các môn chuyên đề tốt nghiệp thay thế (10TC)"
                    ],
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
    },
    "sgu://regulations/academic-warning": {
        "name": "Quy chế xử lý học vụ theo học chế tín chỉ SGU",
        "mimeType": "text/plain",
        "description": "Các tiêu chí cảnh báo học vụ và buộc thôi học của Trường ĐH Sài Gòn",
        "content": """QUY CHẾ HỌC VỤ TRƯỜNG ĐẠI HỌC SÀI GÒN (SGU)
1. Thang điểm đánh giá:
- Điểm đánh giá theo thang điểm 10 được quy đổi sang thang điểm 4:
  + Từ 8.5 - 10.0: Điểm A (4.0) - Xuất sắc / Giỏi
  + Từ 7.0 - 8.4: Điểm B / B+ (3.0 - 3.5) - Khá
  + Từ 5.5 - 6.9: Điểm C / C+ (2.0 - 2.5) - Trung bình
  + Từ 4.0 - 5.4: Điểm D / D+ (1.0 - 1.5) - Trung bình yếu (Đạt môn)
  + Dưới 4.0: Điểm F (0.0) - Không đạt (Bắt buộc học lại)

2. Cảnh báo học vụ (Học lực yếu):
- Sinh viên bị cảnh báo học vụ nếu rơi vào các trường hợp:
  + Điểm trung bình học kỳ < 1.0 đối với học kỳ đầu tiên; < 1.2 đối với các học kỳ tiếp theo.
  + Điểm trung bình tích lũy đạt dưới: 1.2 (năm 1), 1.4 (năm 2), 1.6 (năm 3), 1.8 (năm 4).
  + Tổng số tín chỉ nợ vượt quá 24 tín chỉ.

3. Buộc thôi học:
- Sinh viên bị buộc thôi học nếu bị cảnh báo học vụ 2 lần liên tiếp hoặc tổng số lần cảnh báo vượt quá 3 lần trong toàn khóa học.""",
    },
    "sgu://graduation/standards": {
        "name": "Chuẩn đầu ra tốt nghiệp SGU",
        "mimeType": "text/plain",
        "description": "Yêu cầu bắt buộc để được công nhận tốt nghiệp tại Trường ĐH Sài Gòn",
        "content": """ĐIỀU KIỆN XÉT CÔNG NHẬN TỐT NGHIỆP TRƯỜNG ĐẠI HỌC SÀI GÒN (NGÀNH CNTT):
1. Tích lũy đủ số tín chỉ quy định: Tối thiểu 145 tín chỉ (hệ Kỹ sư).
2. Điểm trung bình tích lũy toàn khóa: Đạt từ 2.00 / 4.00 trở lên.
3. Chuẩn trình độ Ngoại ngữ:
   - Chứng chỉ TOEIC quốc tế đạt từ 500 điểm trở lên (hoặc TOEFL ITP 450, IELTS 5.0, VSTEP B1).
4. Chuẩn trình độ Công nghệ thông tin:
   - Chứng chỉ Ứng dụng CNTT Nâng cao hoặc các chứng chỉ quốc tế MOS/IC3 tương đương.
5. Giáo dục Quốc phòng & Giáo dục Thể chất:
   - Có chứng chỉ Giáo dục Quốc phòng - An ninh và hoàn thành các học phần Giáo dục Thể chất.
6. Điểm rèn luyện:
   - Điểm rèn luyện toàn khóa đạt từ loại Trung bình (>= 50 điểm) trở lên.""",
    },
    "sgu://campuses/directory": {
        "name": "Danh bạ các Cơ sở Trường Đại học Sài Gòn",
        "mimeType": "text/plain",
        "description": "Địa chỉ các cơ sở đào tạo và ký hiệu phòng học của SGU",
        "content": """DANH BẠ CƠ SỞ ĐÀO TẠO SGU:
1. Cơ sở chính: 273 An Dương Vương, Phường 3, Quận 5, TP.HCM.
   - Nơi học tập chính của sinh viên Khoa CNTT, Toán-Ứng dụng, Ngoại ngữ.
   - Ký hiệu giảng đường: Dãy nhà A, B, C, D (ví dụ: C.A102, C.B204) và Dãy phòng máy tính (PM.01 - PM.08).
2. Cơ sở 1: 105 Bà Huyện Thanh Quan, Phường Võ Thị Sáu, Quận 3, TP.HCM.
   - Ký hiệu giảng đường: BHTQ (ví dụ: BHTQ.101, BHTQ.202).
3. Cơ sở 2: 04 Tôn Đức Thắng, Phường Bến Nghé, Quận 1, TP.HCM.
4. Cơ sở 3: 20 Ngô Thời Nhiệm, Phường Võ Thị Sáu, Quận 3, TP.HCM.""",
    },
}
