"""
Module MCP Resources: Tài nguyên tĩnh và ngữ cảnh đào tạo SGU
Cho phép AI Client đọc trực tiếp tài liệu quy chế, sơ đồ đào tạo, chuẩn đầu ra qua URI.
"""

import json

SGU_RESOURCES = {
    "sgu://curriculum/it-roadmap": {
        "name": "Chương trình đào tạo Kỹ sư Công nghệ Thông tin SGU",
        "mimeType": "application/json",
        "description": "Toàn bộ lộ trình 9 học kỳ (4.5 năm) và khung chương trình đào tạo Kỹ sư ngành CNTT Trường ĐH Sài Gòn",
        "content": json.dumps(
            {
                "truong": "Trường Đại học Sài Gòn (SGU)",
                "khoa": "Công nghệ Thông tin",
                "nganh": "Công nghệ Thông tin",
                "ma_nganh": "7480201",
                "he_dao_tao": "Kỹ sư chính quy (Trình độ 7)",
                "thoi_gian_dao_tao": "4,5 năm (9 học kỳ chính)",
                "tong_tin_chi": 152,
                "ghi_chu_tin_chi": "Tích lũy tối thiểu 152 tín chỉ chuyên môn (chưa bao gồm Giáo dục thể chất và Giáo dục quốc phòng - an ninh được cấp chứng chỉ riêng)",
                "lo_trinh_hoc_ky": {
                    "Học kỳ 1": [
                        "Nhập môn lập trình (3TC)",
                        "Đại số tuyến tính (3TC)",
                        "Giải tích 1 (3TC)",
                        "Triết học Mác - Lênin (3TC)",
                        "Tiếng Anh 1 (3TC)",
                        "Pháp luật đại cương (2TC)",
                    ],
                    "Học kỳ 2": [
                        "Kỹ thuật lập trình (3TC)",
                        "Cấu trúc rời rạc (3TC)",
                        "Giải tích 2 (3TC)",
                        "Vật lý đại cương (3TC)",
                        "Kinh tế chính trị Mác - Lênin (2TC)",
                        "Tiếng Anh 2 (3TC)",
                    ],
                    "Học kỳ 3": [
                        "Cấu trúc dữ liệu và giải thuật (4TC)",
                        "Lập trình hướng đối tượng (3TC)",
                        "Cơ sở dữ liệu (3TC)",
                        "Xác suất thống kê (3TC)",
                        "Chủ nghĩa xã hội khoa học (2TC)",
                        "Tiếng Anh 3 (3TC)",
                    ],
                    "Học kỳ 4": [
                        "Hệ điều hành (3TC)",
                        "Mạng máy tính (3TC)",
                        "Hệ quản trị cơ sở dữ liệu (3TC)",
                        "Kiến trúc máy tính và Hợp ngữ (3TC)",
                        "Tư tưởng Hồ Chí Minh (2TC)",
                        "Tiếng Anh 4 (3TC)",
                    ],
                    "Học kỳ 5": [
                        "Công nghệ phần mềm (3TC)",
                        "Lập trình mạng (3TC)",
                        "Trí tuệ nhân tạo (3TC)",
                        "An toàn và bảo mật thông tin (3TC)",
                        "Lịch sử Đảng Cộng sản Việt Nam (2TC)",
                        "Phân tích và thiết kế thuật toán (3TC)",
                    ],
                    "Học kỳ 6": [
                        "Các công nghệ lập trình hiện đại (3TC)",
                        "Phát triển ứng dụng Web nâng cao (3TC)",
                        "Phân tích thiết kế hệ thống thông tin (3TC)",
                        "Học máy và Khai phá dữ liệu (3TC)",
                        "Đồ họa máy tính & Xử lý ảnh (3TC)",
                        "Kỹ thuật giao diện và trải nghiệm người dùng UI/UX (3TC)",
                    ],
                    "Học kỳ 7": [
                        "Quản trị dự án CNTT (3TC)",
                        "Chuyên đề phát triển ứng dụng di động (3TC)",
                        "Điện toán đám mây và Công nghệ ảo hóa (3TC)",
                        "Kiến trúc phần mềm và Mẫu thiết kế (3TC)",
                        "Internet kết nối vạn vật - IoT (3TC)",
                        "Chuyên đề tự chọn nâng cao 1 (3TC)",
                    ],
                    "Học kỳ 8": [
                        "Thực tập doanh nghiệp / Thực tập tốt nghiệp (4TC)",
                        "Phương pháp nghiên cứu khoa học trong CNTT & Tiểu luận chuyên ngành (3TC)",
                        "Kiểm thử và Đảm bảo chất lượng phần mềm (3TC)",
                        "DevOps và Triển khai hệ thống phần mềm (3TC)",
                        "Chuyên đề tự chọn nâng cao 2 (3TC)",
                    ],
                    "Học kỳ 9": [
                        "Khóa luận tốt nghiệp Kỹ sư CNTT (10TC) hoặc Học các môn chuyên đề tốt nghiệp thay thế (10TC)"
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
        "description": "Quy chế tính điểm hệ 4, các khung cảnh cáo học vụ và điều kiện buộc thôi học của Trường ĐH Sài Gòn",
        "content": """QUY CHẾ HỌC VỤ VÀ XỬ LÝ HỌC TẬP TRƯỜNG ĐẠI HỌC SÀI GÒN (SGU)
(Áp dụng theo Quy chế đào tạo trình độ đại học theo học chế tín chỉ của SGU và Thông tư 08/2021/TT-BGDĐT)

1. Thang điểm đánh giá và Quy đổi:
- Điểm đánh giá bộ phận và điểm thi kết thúc học phần được chấm theo thang điểm 10 (0 - 10), làm tròn đến một chữ số thập phân.
- Điểm học phần là tổng điểm của tất cả các điểm đánh giá bộ phận nhân với trọng số tương ứng.
- Điểm học phần được quy đổi sang thang điểm chữ và thang điểm 4:
  + Từ 9.0 - 10.0: Điểm A+ (4.0) - Xuất sắc
  + Từ 8.5 - 8.9:  Điểm A  (3.8 - 4.0) - Giỏi
  + Từ 7.7 - 8.4:  Điểm B+ (3.5) - Khá giỏi
  + Từ 7.0 - 7.6:  Điểm B  (3.0) - Khá
  + Từ 6.2 - 6.9:  Điểm C+ (2.5) - Trung bình khá
  + Từ 5.5 - 6.1:  Điểm C  (2.0) - Trung bình
  + Từ 4.7 - 5.4:  Điểm D+ (1.5) - Trung bình yếu
  + Từ 4.0 - 4.6:  Điểm D  (1.0) - Đạt yêu cầu tối thiểu
  + Dưới 4.0:      Điểm F  (0.0) - Không đạt (Bắt buộc phải đăng ký học lại)

- Phân loại học lực theo điểm trung bình chung tích lũy (GPA thang 4):
  + Xuất sắc:       3.60 - 4.00
  + Giỏi:           3.20 - 3.59
  + Khá:            2.50 - 3.19
  + Trung bình:     2.00 - 2.49
  + Yếu:            1.00 - 1.99
  + Kém:            Dưới 1.00

2. Quy chế Cảnh báo học vụ (Academic Warning):
Cảnh báo kết quả học tập được thực hiện theo từng học kỳ chính nhằm cảnh báo sinh viên có kết quả học tập kém để có phương án phấn đấu khắc phục:
- Sinh viên bị cảnh báo học vụ nếu rơi vào một trong các trường hợp sau:
  a) Điểm trung bình chung học kỳ (ĐTBHK):
     * Dưới 0.80 đối với học kỳ đầu tiên của khóa học;
     * Dưới 1.00 đối với các học kỳ tiếp theo.
  b) Điểm trung bình chung tích lũy (ĐTBTCL):
     * Dưới 1.20 đối với sinh viên năm thứ nhất;
     * Dưới 1.40 đối với sinh viên năm thứ hai;
     * Dưới 1.60 đối với sinh viên năm thứ ba;
     * Dưới 1.80 đối với sinh viên các năm tiếp theo đến cuối khóa.
  c) Nợ tín chỉ tồn đọng:
     * Tổng số tín chỉ của các học phần bị điểm F chưa được tích lũy vượt quá 24 tín chỉ tính đến thời điểm xét.
- Phân mức cảnh báo & Hệ quả:
  + Cảnh báo học vụ Mức 1 và Mức 2.
  + Sinh viên đang trong diện bị cảnh báo học vụ bị giới hạn số tín chỉ đăng ký tối đa trong học kỳ kế tiếp (tối đa không quá 14 tín chỉ).
  + Sinh viên có trách nhiệm gặp Cố vấn học tập (CVHT) để được tư vấn lộ trình học cải thiện.

3. Quy định Buộc thôi học:
Sinh viên bị buộc thôi học nếu vi phạm một trong các trường hợp sau:
- Bị cảnh báo học vụ 02 lần liên tiếp (hoặc vượt quá số lần cảnh báo quy định trong toàn khóa học).
- Vượt quá thời gian tối đa được phép học tập tại trường:
  * Thời gian tối đa hoàn thành chương trình = 2N (với N là thời gian thiết kế theo kế hoạch chuẩn: 9 năm đối với hệ Kỹ sư 4,5 năm; 8 năm đối với hệ 4 năm).
- Tự ý bỏ học không có lý do chính đáng từ 01 học kỳ chính trở lên mà không đăng ký học phần hoặc không làm thủ tục tạm dừng học tập theo quy định.
- Bị kỷ luật ở mức buộc thôi học do gian lận thi cử (thi hộ, nhờ người thi hộ) hoặc vi phạm pháp luật.""",
    },
    "sgu://graduation/standards": {
        "name": "Chuẩn đầu ra tốt nghiệp SGU",
        "mimeType": "text/plain",
        "description": "Điều kiện bắt buộc xét công nhận tốt nghiệp hệ Kỹ sư CNTT tại Trường ĐH Sài Gòn",
        "content": """ĐIỀU KIỆN XÉT CÔNG NHẬN TỐT NGHIỆP TRƯỜNG ĐẠI HỌC SÀI GÒN (HỆ KỸ SƯ CNTT):
(Căn cứ theo Quy chế đào tạo đại học và các Quyết định chuẩn đầu ra hiện hành của Trường ĐH Sài Gòn)

1. Tích lũy đủ số tín chỉ và hoàn thành chương trình đào tạo:
- Sinh viên phải tích lũy tối thiểu 152 tín chỉ của chương trình đào tạo Kỹ sư Công nghệ Thông tin (4,5 năm).
- Hoàn thành đầy đủ các học phần bắt buộc, tự chọn chuyên ngành, Thực tập doanh nghiệp và Khóa luận tốt nghiệp (hoặc các học phần tốt nghiệp thay thế).

2. Điểm trung bình chung tích lũy (GPA toàn khóa):
- Điểm trung bình chung tích lũy toàn khóa đạt từ 2.00 / 4.00 trở lên.
- Xếp loại tốt nghiệp:
  + Xuất sắc:   3.60 - 4.00 (không bị hạ bậc do kỷ luật hoặc thi lại quá số tín chỉ quy định)
  + Giỏi:       3.20 - 3.59
  + Khá:        2.50 - 3.19
  + Trung bình: 2.00 - 2.49

3. Chuẩn trình độ Ngoại ngữ (Tiếng Anh):
Sinh viên phải đạt một trong các chứng chỉ ngoại ngữ sau đây (còn thời hạn hiệu lực tại thời điểm xét tốt nghiệp):
- Chứng chỉ VSTEP: Đạt từ Bậc 3 trở lên (tương đương B1 theo Khung năng lực ngoại ngữ 6 bậc dùng cho Việt Nam).
- Chứng chỉ quốc tế tương đương:
  + TOEIC (Nghe & Đọc): Đạt từ 500 - 550 điểm trở lên.
  + IELTS (Academic): Đạt từ 4.5 - 5.0 trở lên.
  + TOEFL ITP: Đạt từ 450 điểm trở lên; TOEFL iBT: Đạt từ 45 điểm trở lên.
  + Cambridge: PET (Preliminary English Test) hoặc Linguaskill B1 (từ 140 điểm trở lên).
  + Aptis ESOL: Đạt trình độ B1.

4. Chuẩn trình độ Công nghệ thông tin:
- ĐẶC BIỆT DÀNH CHO KHOA CNTT: Sinh viên theo học các ngành thuộc Khoa Công nghệ Thông tin (Công nghệ Thông tin, Kỹ thuật Phần mềm) được MIỄN nộp chứng chỉ Ứng dụng CNTT đầu ra, do khối lượng kiến thức chuyên môn trong chương trình đào tạo đã hoàn toàn đáp ứng và vượt trên chuẩn kỹ năng CNTT theo Thông tư 03/2014/TT-BTTTT.
- (Lưu ý: Đối với sinh viên các khoa khác ngoài ngành CNTT, chuẩn đầu ra tin học bắt buộc là Chứng chỉ Ứng dụng CNTT cơ bản hoặc chứng chỉ quốc tế MOS/IC3).

5. Giáo dục Thể chất (GDTC) & Giáo dục Quốc phòng - An ninh (GDQP-AN):
- Hoàn thành và tích lũy đủ các học phần Giáo dục Thể chất theo quy định của nhà trường.
- Có chứng chỉ Giáo dục Quốc phòng - An ninh hợp lệ do cơ quan có thẩm quyền cấp.

6. Điểm rèn luyện toàn khóa:
- Điểm rèn luyện toàn khóa đạt từ loại Trung bình trở lên (từ 50 điểm / 100 điểm trở lên).

7. Tư cách đạo đức và trách nhiệm:
- Cho đến thời điểm xét tốt nghiệp không bị truy cứu trách nhiệm hình sự hoặc không đang trong thời gian bị kỷ luật từ mức đình chỉ học tập trở lên.
- Đã hoàn tất mọi nghĩa vụ tài chính (học phí, lệ phí) và hoàn trả đầy đủ sách, tài liệu mượn từ Thư viện trường.""",
    },
    "sgu://campuses/directory": {
        "name": "Danh bạ các Cơ sở Trường Đại học Sài Gòn",
        "mimeType": "text/plain",
        "description": "Địa chỉ các cơ sở đào tạo, ký hiệu giảng đường và quy tắc tra cứu phòng học của SGU",
        "content": """DANH BẠ CÁC CƠ SỞ ĐÀO TẠO VÀ KÝ HIỆU GIẢNG ĐƯỜNG TRƯỜNG ĐẠI HỌC SÀI GÒN (SGU):

1. Cơ sở chính: 273 An Dương Vương, Phường Chợ Quán (Phường 3 cũ), Quận 5, TP.HCM.
- Vai trò: Trụ sở trung tâm hành chính, điều hành và là địa điểm học tập chính của sinh viên Khoa Công nghệ Thông tin, Khoa Toán - Ứng dụng, Khoa Ngoại ngữ, Khoa Sư phạm Khoa học Tự nhiên...
- Quy tắc mã phòng trên Thời khóa biểu SGU: [C].[Khu/Dãy][Tầng][Số phòng]
  + Dãy A: Giảng đường học lý thuyết (ví dụ: C.A102 - Cơ sở chính, Dãy A, Lầu 1, Phòng 02; C.A501 - Lầu 5, Phòng 501).
  + Dãy B: Giảng đường học lý thuyết (ví dụ: C.B001 - Tầng trệt dãy B; C.B204 - Lầu 2, Phòng 04).
  + Dãy C: Dãy phòng học tổng hợp, kế cận Thư viện trung tâm SGU.
  + Dãy D: Văn phòng Khoa và các phòng hội thảo chuyên đề (ví dụ: C.D301 - Văn phòng Khoa Công nghệ Thông tin tại Lầu 3).
  + Dãy E: Giảng đường dãy E.
  + Khu HB: Khu Nhà Hiệu bộ (Nơi làm việc của Ban Giám hiệu, Phòng Đào tạo, Phòng Công tác Sinh viên; phòng học ví dụ C.HB406).
  + Khu NT: Khu Nhà Nghệ thuật (Dành riêng cho khối ngành Âm nhạc, Mỹ thuật, Sư phạm Nghệ thuật).
  + Khu S: Khu vực Sân thể dục thể thao, sân bãi phục vụ học phần Giáo dục Thể chất và Quốc phòng (ví dụ: C.S001).
  + Dãy phòng máy tính thực hành CNTT: Ký hiệu PM.01 đến PM.08 (hoặc C.PMxx) bố trí tại Lầu 2 & Lầu 3 Dãy C/D, trang bị máy tính cấu hình cao phục vụ các môn lập trình, mạng, cơ sở dữ liệu và AI.

2. Cơ sở 1: 105 Bà Huyện Thanh Quan, Phường Xuân Hòa (Phường Võ Thị Sáu cũ), Quận 3, TP.HCM.
- Vai trò: Địa điểm học tập của khối ngành Luật, Sư phạm Khoa học Xã hội, Quản trị Kinh doanh.
- Quy tắc mã phòng: [1].[Khu][Tầng][Số phòng] (ví dụ: 1.A302 - Cơ sở 1, Khu A, Lầu 3, Phòng 302) hoặc ký hiệu truyền thống BHTQ (ví dụ: BHTQ.101, BHTQ.202).

3. Cơ sở 2: 04 Tôn Đức Thắng, Phường Bến Nghé (Phường Sài Gòn), Quận 1, TP.HCM.
- Vai trò: Nơi học tập của sinh viên Khoa Tài chính - Kế toán, Khoa Quản trị Kinh doanh.
- Quy tắc mã phòng: [2].[Khu][Tầng][Số phòng] (ví dụ: 2.B301 - Cơ sở 2, Khu B, Lầu 3, Phòng 301) hoặc ký hiệu truyền thống TĐT (ví dụ: TĐT.101).

4. Cơ sở 3: 20 Ngô Thời Nhiệm, Phường Xuân Hòa (Phường Võ Thị Sáu cũ), Quận 3, TP.HCM.
- Vai trò: Cơ sở đào tạo dành cho Khoa Giáo dục Tiểu học, Khoa Giáo dục Mầm non.
- Quy tắc mã phòng: [3].[Khu][Tầng][Số phòng] (ví dụ: 3.A101).

5. Ký túc xá SGU: 99 An Dương Vương, Phường Phú Định (Phường 16 cũ), Quận 8, TP.HCM.
- Khu nội trú khang trang dành cho sinh viên xa nhà, tích hợp phòng tự học, sân thể thao và canteen.

6. Trường Trung học Thực hành Sài Gòn (trực thuộc SGU): 220 Trần Bình Trọng, Phường Chợ Quán, Quận 5, TP.HCM.
- Trường thực hành sư phạm và cơ sở thực tập giảng dạy của sinh viên khối Sư phạm SGU.""",
    },
}
