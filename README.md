# SGU Academic MCP Server 🎓🤖

> **Đề tài:** Tìm hiểu MCP SDK và hiện thực MCP Server hỗ trợ tra cứu tiện ích học vụ SGU cho trợ lý AI  
> **Môn học:** Các Công nghệ Lập trình Hiện đại (CCNLTHD)  
> **Track:** AI / Data  
> **Công nghệ chính (Phần A4):** `MCP SDK` (Model Context Protocol Python SDK v2.x)  
> **Hồ sơ đề tài (Phần B1):** `MCP Server`  
> **Đơn vị áp dụng:** Trường Đại học Sài Gòn (SGU) — Cổng thông tin đào tạo `thongtindaotao.sgu.edu.vn`

---

## 📖 1. Giới thiệu tổng quan

Dự án hiện thực một **MCP Server** theo chuẩn mở **Model Context Protocol (MCP)** do Anthropic khởi xướng. Hệ thống đóng vai trò cầu nối trung gian (Middleware Bridge), cho phép các Trợ lý Trí tuệ Nhân tạo hiện đại (Claude Desktop, Cursor IDE, Custom Chatbots) kết nối trực tiếp với **Cổng thông tin đào tạo trường Đại học Sài Gòn (SGU)** để tra cứu và thực thi các nghiệp vụ học vụ thông minh bằng ngôn ngữ tự nhiên.

### ✨ Các điểm nổi bật:
* **Dữ liệu thật 100% (Real Data):** Kết nối trực tiếp vào REST API chính thức của SGU (`thongtindaotao.sgu.edu.vn`).
* **Bảo mật hai lớp:** Tự động tạo header mã hóa `ua` (User-Agent dynamic XOR encryption) để vượt qua cơ chế chống bot của trường và bảo vệ token sinh viên trong môi trường cục bộ.
* **Bộ nhớ đệm thông minh (SQLite Caching):** Tự động cache dữ liệu học kỳ vào database SQLite cục bộ, giảm thiểu số lần gọi trùng lặp lên server trường và đảm bảo tốc độ phản hồi < 0.05s.
* **Đúng chuẩn môn học 3 Tầng:** Đạt đầy đủ tiêu chí Tầng 1 (Bản chất lõi), Tầng 2 (Kỹ nghệ phần mềm với Docker, CI/CD, Pytest) và Tầng 3 (Nâng cao).

---

## 🏛️ 2. Kiến trúc Ba Tầng theo chuẩn môn học

```
┌────────────────────────────────────────────────────────┐
│                   Trợ lý AI (Clients)                  │
│       Claude Desktop  │  Cursor IDE  │  Web Client     │
└───────────────────────────┬────────────────────────────┘
                            │ Giao thức JSON-RPC (stdio / SSE)
                            ▼
┌────────────────────────────────────────────────────────┐
│                SGU ACADEMIC MCP SERVER                 │
│                                                        │
│  [15 MCP Tools]      [4 Resources]       [3 Prompts]   │
│  • TKB tuần/ngày     • Sơ đồ CNTT        • Kế hoạch học│
│  • Lịch thi/Đếm ngày • Chuẩn tốt nghiệp  • Lộ trình thi│
│  • Bảng điểm & GPA   • Quy chế cảnh báo  • Audit hồ sơ │
│  • Học phí & Nợ      • Danh bạ cơ sở                   │
│                                                        │
│  [Tầng 2 & 3: Security & Performance Engine]           │
│  • SguEncryptor: Thuật toán sinh dynamic 'ua' header   │
│  • SguCache: SQLite Caching & Fallback Controller      │
└───────────────────────────┬────────────────────────────┘
                            │ HTTPS (REST API)
                            ▼
┌────────────────────────────────────────────────────────┐
│     Cổng thông tin đào tạo SGU (AQTech / PSC)          │
│            thongtindaotao.sgu.edu.vn                   │
└────────────────────────────────────────────────────────┘
```

---

## 🛠️ 3. Danh mục chức năng

### 3.1. 15 MCP Tools (Hành động AI có thể gọi)
| STT | Tên Tool | Mô tả chức năng |
| :---: | :--- | :--- |
| 1 | `sgu_login` | Đăng nhập tài khoản sinh viên vào cổng thông tin đào tạo SGU |
| 2 | `get_registered_courses` | Lấy danh sách các môn đã đăng ký trong kỳ của sinh viên |
| 3 | `get_weekly_schedule` | Lấy thời khóa biểu học kỳ chi tiết theo tuần |
| 4 | `get_today_schedule` | Tra cứu nhanh lịch học hôm nay (phòng, ca học, giảng viên) |
| 5 | `check_schedule_conflict` | Kiểm tra trùng lịch học khi định đăng ký thêm môn học mới |
| 6 | `get_exam_schedule` | Tra cứu lịch thi chính thức từ SGU (ngày thi, phòng, ca, SBD) |
| 7 | `get_exam_countdown` | Đếm ngược ngày thi và cảnh báo các môn thi dồn dập trong 1 ngày |
| 8 | `get_student_profile` | Lấy hồ sơ sinh viên chính thức (họ tên, lớp, ngành, cố vấn học tập) |
| 9 | `get_semester_grades` | Lấy bảng điểm học tập chi tiết từng học kỳ |
| 10 | `calculate_gpa_summary` | Tổng hợp GPA tích lũy, số tín chỉ đạt và các môn nợ |
| 11 | `simulate_target_gpa` | Thuật toán mô phỏng điểm số cần đạt ở các môn tới để đạt bằng Giỏi |
| 12 | `get_tuition_fees` | Tra cứu học phí từng kỳ, số tiền đã đóng và số tiền nợ đọng |
| 13 | `get_sgu_notifications` | Lấy thông báo mới nhất từ Ban Giám hiệu và Phòng Đào tạo |
| 14 | `get_course_offerings` | Tra cứu các lớp học phần đang mở kèm số lượng slot còn lại |
| 15 | `check_prerequisites` | Kiểm tra điều kiện môn tiên quyết ngành CNTT SGU |

### 3.2. 4 MCP Resources (Tài nguyên đọc ngữ cảnh)
* `sgu://curriculum/it-roadmap`: Toàn bộ lộ trình 8 học kỳ và khung môn học ngành CNTT SGU.
* `sgu://regulations/academic-warning`: Quy chế tính điểm hệ 4 và các mức cảnh cáo học vụ.
* `sgu://graduation/standards`: Điều kiện xét tốt nghiệp (tín chỉ, TOEIC 500/VSTEP, chứng chỉ tin học).
* `sgu://campuses/directory`: Địa chỉ và ký hiệu phòng học các cơ sở của Trường ĐH Sài Gòn.

### 3.3. 3 MCP Prompts (Mẫu tác vụ AI định sẵn)
* `plan_weekly_routine`: Tự động lập lịch học và sinh hoạt tối ưu dựa trên thời khóa biểu tuần thực tế.
* `exam_cramming_strategy`: Lập chiến lược ôn thi nước rút theo mức độ khẩn cấp của lịch thi.
* `graduation_audit`: Đối soát toàn diện điểm và số tín chỉ của sinh viên so với chuẩn đầu ra tốt nghiệp.

---

## 🚀 4. Hướng dẫn cài đặt và khởi chạy

### Yêu cầu hệ thống:
* Python 3.10+ (Khuyến nghị 3.12)
* Docker & Docker Compose (tùy chọn)

### Cách 1: Chạy trực tiếp bằng Python
1. Clone repo và cài đặt thư viện:
   ```bash
   git clone <repo-url>
   cd CCNLTHD
   pip install -r requirements.txt
   ```
2. Cấu hình file `.env` (tạo từ `.env.example`):
   ```env
   SGU_STUDENT_ID=3122410001
   SGU_PASSWORD=MatKhauCuaBan
   ```
3. Chạy kiểm thử tự động:
   ```bash
   pytest
   ```
4. Khởi động MCP Server ở chế độ stdio (dùng cho Claude Desktop / Cursor):
   ```bash
   python -m sgu_mcp.server --transport stdio
   ```
   Hoặc chế độ SSE (dùng cho mạng mạng LAN / Web API):
   ```bash
   python -m sgu_mcp.server --transport sse --port 8000
   ```

### Cách 2: Chạy 1 lệnh với Docker Compose (Chuẩn Tầng 2)
```bash
docker compose up -d --build
```
Server sẽ tự động khởi chạy tại `http://localhost:8000/sse`.

---

## 🔌 5. Tích hợp với Claude Desktop

Mở file cấu hình của Claude Desktop:
* **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
* **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

Thêm cấu hình server:
```json
{
  "mcpServers": {
    "sgu_academic_server": {
      "command": "python",
      "args": [
        "-m",
        "sgu_mcp.server",
        "--transport",
        "stdio"
      ],
      "cwd": "D:/CCNLTHD",
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```
Khởi động lại Claude Desktop, bạn sẽ thấy biểu tượng công cụ xuất hiện với đầy đủ 15 Tools!

---

## 🧪 6. Kết quả Kiểm thử (Pytest Verification)
```bash
$ pytest
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2
collected 12 items

tests\test_cache.py ...                                                  [ 25%]
tests\test_crypto.py ..                                                  [ 41%]
tests\test_mcp_server.py ....                                            [ 75%]
tests\test_tools_offline.py ...                                          [100%]
============================== 12 passed in 2.06s ==============================
```

---

## 📄 7. Cấu trúc mã nguồn
```
├── sgu_mcp/
│   ├── config.py              # Cấu hình Pydantic Settings
│   ├── server.py              # Entrypoint MCP Server (Stdio & SSE)
│   ├── core/
│   │   ├── crypto.py          # Thuật toán sinh dynamic 'ua' header
│   │   ├── cache.py           # Bộ nhớ đệm SQLite
│   │   └── sgu_client.py      # HTTP Client kết nối API thongtindaotao.sgu.edu.vn
│   ├── modules/
│   │   ├── schedule.py        # 5 Tools về TKB, đăng ký môn & trùng lịch
│   │   ├── exams.py           # 2 Tools về Lịch thi & đếm ngược ngày thi
│   │   ├── academic.py        # 4 Tools về Hồ sơ SV, bảng điểm & mô phỏng GPA
│   │   └── tuition.py         # 4 Tools về Học phí, thông báo & môn tiên quyết
│   ├── resources/
│   │   └── content.py         # 4 Tài nguyên đọc ngữ cảnh SGU
│   └── prompts/
│       └── templates.py       # 3 Mẫu prompt thông minh
├── hands_on_lab/
│   └── HANDS_ON_LAB.md        # Tài liệu thực hành 30-45 phút cho nhóm khác chấm chéo
├── tests/                     # 12 bài kiểm thử tự động pytest
├── Dockerfile & docker-compose.yml
└── requirements.txt
```
