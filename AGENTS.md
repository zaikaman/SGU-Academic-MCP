# AGENTS.md — Hướng dẫn Vận hành Dành cho Trợ lý AI (Native MCP Protocol)

Tài liệu này cung cấp quy chuẩn kiến trúc và quy tắc hành vi bắt buộc cho các AI Agent (Antigravity, Cursor, Claude Code, Windsurf, v.v.) khi làm việc với dự án **SGU Academic MCP Server**.

---

## 1. Quy tắc Vàng: 100% Native MCP Tools (Golden Rule)

> [!IMPORTANT]
> **QUY TẮC BẮT BUỘC DÀNH CHO AI AGENT:**
> - AI Agent **CHỈ ĐƯỢC PHÉP tương tác với hệ thống thông qua NATIVE MCP TOOLS** (gọi tool dạng JSON-RPC trực tiếp từ context của IDE/chat interface, ví dụ: `get_today_schedule()`, `get_tuition_fees()`, `calculate_gpa_summary()`).
> - **NGHIÊM CẤM** AI Agent tự ý mở terminal (PowerShell / Bash / CMD) để chạy các lệnh `python -m sgu_mcp...` nhằm lấy dữ liệu thay thế cho tool call trong lúc trả lời người dùng.
> - **Nếu Native Tools chưa xuất hiện trong context:** AI Agent phải thông báo thân thiện và hướng dẫn người dùng kết nối lại MCP Server trong IDE (hoặc chạy `python setup.py`), **tuyệt đối không được "chữa cháy" bằng cách chạy lệnh terminal**.

---

## 2. Kiến trúc 3 Tầng theo Thứ tự Ưu tiên (Production-Ready Architecture)

Dự án được thiết kế theo 3 tầng môi trường chuẩn hóa, ưu tiên từ trải nghiệm cá nhân mượt mà nhất đến môi trường container hóa:

| Thứ tự ưu tiên | Môi trường | Giao thức truyền tải (Transport) | Đặc điểm vận hành |
| :--- | :--- | :--- | :--- |
| **Mặc định #1** | **Windows Native** | **Stdio Transport** (`--transport stdio`) | **Khuyên dùng cho 90% người dùng / sinh viên:**<br/>• IDE (Cursor, Antigravity, VS Code, Claude Desktop) tự động spawn server process.<br/>• KHÔNG cần mở port mạng (không sợ trùng port 8000 hay bị Windows Defender chặn).<br/>• KHÔNG cần mở terminal bật server thủ công.<br/>• 15 Tools sẵn sàng ngay khi mở IDE. |
| **Ưu tiên #2** | **Docker Container** | **Stdio Bridge** (`docker exec -i ...` / WSL) | **Chuẩn cô lập Container tối ưu nhất:**<br/>• 100% chạy cách ly bên trong container `sgu_mcp_academic_server`.<br/>• Tự động hỗ trợ cả Docker Desktop Native và Docker daemon trong WSL 2.<br/>• Không phụ thuộc mở cổng mạng, không bị lỗi drop stream hay tường lửa chặn. |
| **Lựa chọn #3** | **Docker / Remote SSE** | **SSE Transport** (`http://localhost:8000/sse`) | Dành cho DevOps hoặc triển khai Server tập trung qua HTTP Server-Sent Events. |
| **Tùy chọn #4** | **WSL Native (Linux)** | **Stdio Transport** (`--transport stdio`) | Dành cho Developers dùng Linux/WSL shell (`python3`). |

---

## 3. Cấu hình 1-Click Tự động (`setup.py` / `setup.bat`)

Để đảm bảo mọi IDE đều tự động nạp đúng 15 Native MCP Tools:

### Cấu hình mặc định (Stdio Native):
Chỉ cần nhấp đúp vào `setup.bat` (trên Windows) hoặc chạy:
```bash
python setup.py
```
Script sẽ tự động nhận diện đường dẫn Python hiện tại và ghi cấu hình Stdio chuẩn vào mọi IDE.

### Cấu hình ưu tiên chạy qua Docker Container:
Để IDE tự động kết nối và chạy 100% bên trong container Docker:
```bash
python setup.py --docker
```
Script sẽ tự động phát hiện Docker Native hoặc Docker trong WSL 2 và cấu hình Stdio Bridge vào:
- **Google Antigravity:** `~/.gemini/config/mcp_config.json` & `~/.gemini/antigravity/mcp_config.json`
- **Cursor IDE:** `.cursor/mcp.json` & `~/.cursor/mcp.json`
- **VS Code:** `.vscode/mcp.json`
- **Claude Desktop:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Windsurf, Cline, Roo Code...**

### Cấu hình qua Docker SSE (Network Mode):
Nếu muốn kết nối qua Docker SSE ở cổng mạng (ví dụ 8000):
```bash
python setup.py --sse --port 8000
```

---

## 4. Bảng Tra cứu 15 Native MCP Tools

Toàn bộ 15 công cụ của hệ thống được gọi trực tiếp từ giao diện chat:

| STT | Tên Tool | Mục đích sử dụng |
| :---: | :--- | :--- |
| 1 | `sgu_login` | Đăng nhập tài khoản sinh viên SGU |
| 2 | `get_today_schedule` | Xem lịch học hôm nay / ngày mai (ca học, phòng, giảng viên) |
| 3 | `get_weekly_schedule` | Thời khóa biểu học kỳ chi tiết theo tuần |
| 4 | `get_registered_courses` | Danh sách các môn học đã đăng ký trong học kỳ |
| 5 | `check_schedule_conflict` | Kiểm tra xung đột / trùng lịch học trước khi ĐKMH |
| 6 | `get_exam_schedule` | Lịch thi học kỳ chính thức (ngày, ca thi, phòng thi, SBD) |
| 7 | `get_exam_countdown` | Đếm ngược ngày thi & cảnh báo thi dồn dập |
| 8 | `get_student_profile` | Hồ sơ sinh viên: Họ tên, MSSV, lớp, ngành, Cố vấn học tập |
| 9 | `get_semester_grades` | Bảng điểm chi tiết từng học kỳ |
| 10 | `calculate_gpa_summary` | Tổng hợp GPA tích lũy, số tín chỉ đạt và danh sách môn nợ |
| 11 | `simulate_target_gpa` | Mô phỏng điểm số cần đạt để tốt nghiệp loại Khá/Giỏi |
| 12 | `get_tuition_fees` | Tra cứu học phí, số tiền đã nộp và nợ học phí |
| 13 | `get_sgu_notifications` | Thông báo mới nhất từ Ban Giám hiệu & Phòng Đào tạo |
| 14 | `get_course_offerings` | Tra cứu lớp học phần đang mở kèm số lượng chỗ còn trống |
| 15 | `check_prerequisites` | Kiểm tra điều kiện môn tiên quyết ngành CNTT SGU |

---

## 5. Nghiệp vụ Học vụ & Kỹ năng (Skills)

Toàn bộ tài liệu chi tiết về nghiệp vụ, 4 MCP Resources, 3 Prompts và quy tắc ứng xử học đường được định nghĩa tại:

- **[skills/sgu-academic/SKILL.md](file:///c:/Users/zaika/OneDrive/Desktop/SGU-Academic-MCP/skills/sgu-academic/SKILL.md)**

Khi hỗ trợ sinh viên về học vụ, Agent hãy tuân thủ hướng dẫn trong file Skill trên!
