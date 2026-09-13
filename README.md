# SGU Academic MCP Server 🎓🤖

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Model Context Protocol](https://img.shields.io/badge/MCP-Protocol-purple.svg)](https://modelcontextprotocol.io/)
[![Tests](https://img.shields.io/badge/tests-12%20passed-brightgreen.svg)](tests/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](Dockerfile)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A production-grade **Model Context Protocol (MCP)** Server bridging AI Assistants (Claude Desktop, Antigravity, Cursor) directly with the **Saigon University (SGU) Academic Portal** (`thongtindaotao.sgu.edu.vn`).

---

## 📖 Giới thiệu

**SGU Academic MCP Server** được xây dựng theo chuẩn mở [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) của Anthropic. Hệ thống đóng vai trò cầu nối thông minh (Bridge Middleware), giúp các Trợ lý AI có thể tương tác trực tiếp với dữ liệu học tập thực tế từ cổng thông tin đào tạo Đại học Sài Gòn (SGU) bằng ngôn ngữ tự nhiên.

### ✨ Tính năng nổi bật

* **100% Dữ liệu thực tế:** Tích hợp trực tiếp với API cổng đào tạo SGU (`thongtindaotao.sgu.edu.vn`), không dùng dữ liệu giả lập.
* **Cơ chế Reverse-Engineered Security:** Tự động tạo dynamic header `ua` với thuật toán mã hóa timestamp + XOR bitwise, tương thích hoàn toàn với cơ chế bảo mật của cổng đào tạo.
* **Smart SQLite Caching:** Tự động cache kết quả học tập và thời khóa biểu cục bộ, đảm bảo tốc độ phản hồi < 0.05s và giảm thiểu áp lực request lên máy chủ trường.
* **Hỗ trợ đa phương thức truyền tải (Transports):**
  * `stdio`: Tích hợp chuẩn cho Claude Desktop, Cursor, Antigravity.
  * `SSE` (Server-Sent Events): Dùng khi triển khai dạng dịch vụ mạng LAN hoặc Web container.
* **Bộ tính năng phong phú:** 15 Tools, 4 Resources ngữ cảnh, và 3 Prompts mẫu thông minh.

---

## 🏛️ Kiến trúc hệ thống

```
┌────────────────────────────────────────────────────────┐
│                   Trợ lý AI (Clients)                  │
│       Claude Desktop  │  Cursor IDE  │   Antigravity   │
└───────────────────────────┬────────────────────────────┘
                            │ JSON-RPC (stdio / SSE)
                            ▼
┌────────────────────────────────────────────────────────┐
│                SGU ACADEMIC MCP SERVER                 │
│                                                        │
│  [15 MCP Tools]      [4 Resources]       [3 Prompts]   │
│  • TKB tuần / ngày   • Lộ trình CNTT     • Kế hoạch học│
│  • Lịch thi & Đếm    • Chuẩn tốt nghiệp  • Ôn thi cấp tốc│
│  • Điểm & GPA audit  • Quy chế học vụ    • Audit hồ sơ │
│  • Học phí & Nợ môn  • Danh bạ cơ sở                   │
│                                                        │
│  [Security & Performance Engine]                       │
│  • SguEncryptor: Thuật toán tạo header dynamic 'ua'    │
│  • SguCache: SQLite Caching & Fallback Controller      │
└───────────────────────────┬────────────────────────────┘
                            │ HTTPS (REST API)
                            ▼
┌────────────────────────────────────────────────────────┐
│              Cổng thông tin đào tạo SGU                │
│              thongtindaotao.sgu.edu.vn                 │
└────────────────────────────────────────────────────────┘
```

---

## 🛠️ Danh mục năng lực MCP

### 1. 15 MCP Tools (Hành động có thể gọi)

| STT | Tool Name | Mô tả |
| :---: | :--- | :--- |
| 1 | `sgu_login` | Đăng nhập tài khoản sinh viên vào cổng thông tin đào tạo SGU |
| 2 | `get_registered_courses` | Lấy danh sách các môn đã đăng ký thành công trong kỳ |
| 3 | `get_weekly_schedule` | Lấy thời khóa biểu học kỳ chi tiết theo từng thứ trong tuần |
| 4 | `get_today_schedule` | Tra cứu nhanh lịch học hôm nay và ngày mai (phòng, ca, giảng viên) |
| 5 | `check_schedule_conflict` | Kiểm tra xung đột lịch học khi dự định đăng ký môn mới |
| 6 | `get_exam_schedule` | Tra cứu lịch thi chính thức từ SGU (ngày thi, phòng, ca, SBD) |
| 7 | `get_exam_countdown` | Đếm ngược ngày thi và cảnh báo lịch thi dồn dập trong cùng 1 ngày |
| 8 | `get_student_profile` | Lấy hồ sơ sinh viên chính thức (họ tên, MSSV, lớp, ngành, CVHT) |
| 9 | `get_semester_grades` | Lấy bảng điểm chi tiết theo từng học kỳ |
| 10 | `calculate_gpa_summary` | Tổng hợp GPA tích lũy, số tín chỉ đạt và danh sách môn nợ |
| 11 | `simulate_target_gpa` | Thuật toán mô phỏng điểm số cần đạt ở các môn tới để đạt mục tiêu GPA |
| 12 | `get_tuition_fees` | Tra cứu học phí từng kỳ, số tiền đã đóng và số tiền nợ đọng |
| 13 | `get_sgu_notifications` | Lấy thông báo mới nhất từ Nhà trường và Phòng Đào tạo |
| 14 | `get_course_offerings` | Tra cứu danh sách lớp học phần đang mở kèm số lượng chỗ còn lại |
| 15 | `check_prerequisites` | Kiểm tra điều kiện môn tiên quyết ngành CNTT SGU |

### 2. 4 MCP Resources (Tài nguyên đọc ngữ cảnh)

* `sgu://curriculum/it-roadmap`: Toàn bộ lộ trình 8 học kỳ và khung chương trình ngành CNTT SGU.
* `sgu://regulations/academic-warning`: Quy chế tính điểm hệ 4 và các khung cảnh cáo học vụ.
* `sgu://graduation/standards`: Điều kiện xét tốt nghiệp (tín chỉ, chuẩn ngoại ngữ TOEIC 500/VSTEP, tin học).
* `sgu://campuses/directory`: Danh bạ cơ sở và ký hiệu các phòng học tại trường Đại học Sài Gòn.

### 3. 3 MCP Prompts (Mẫu tác vụ AI định sẵn)

* `plan_weekly_routine`: Tự động phân bổ lịch tự học và sinh hoạt dựa trên thời khóa biểu tuần thực tế.
* `exam_cramming_strategy`: Lập chiến lược ôn thi nước rút tối ưu theo mức độ khẩn cấp của lịch thi.
* `graduation_audit`: Đối soát toàn diện điểm số và tín chỉ tích lũy so với chuẩn đầu ra tốt nghiệp.

---

## 🚀 Cài đặt và Sử dụng

### Yêu cầu môi trường
* Python 3.10 trở lên
* Docker & Docker Compose *(tùy chọn)*

### Cách 1: Chạy trực tiếp qua Python

1. **Clone repository:**
   ```bash
   git clone https://github.com/your-username/sgu-academic-mcp.git
   cd sgu-academic-mcp
   ```

2. **Cài đặt dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Cấu hình thông tin đăng nhập:**
   Tạo file `.env` từ mẫu `.env.example`:
   ```env
   SGU_STUDENT_ID=3122xxxxxx
   SGU_PASSWORD=MatKhauCuaBan
   ```

4. **Khởi động MCP Server:**
   * Chế độ **stdio** (khuyên dùng cho Claude Desktop, Cursor, Antigravity):
     ```bash
     python -m sgu_mcp.server --transport stdio
     ```
   * Chế độ **SSE** (dùng khi deploy qua mạng HTTP):
     ```bash
     python -m sgu_mcp.server --transport sse --port 8000
     ```

---

### Cách 2: Triển khai nhanh với Docker

```bash
docker compose up -d --build
```
Dịch vụ MCP Server sẽ chạy ở cổng `8000` (`http://localhost:8000/sse`).

---

## 🔌 Hướng dẫn tích hợp AI Clients

### 1. Claude Desktop

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
      "cwd": "C:/path/to/sgu-academic-mcp",
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

### 2. Antigravity IDE / Cursor

Cấu hình trong file `mcp_config.json` của workspace hoặc global:
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
      "cwd": "C:/path/to/sgu-academic-mcp",
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

---

## 🧪 Kiểm thử tự động (Unit Tests)

Dự án đi kèm bộ test tự động sử dụng `pytest`:

```bash
pytest -v
```

Kết quả kiểm thử:
```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2
collected 12 items

tests/test_cache.py::test_cache_set_and_get PASSED                       [  8%]
tests/test_cache.py::test_cache_ttl_expiration PASSED                    [ 16%]
tests/test_cache.py::test_cache_clear PASSED                             [ 25%]
tests/test_crypto.py::test_isapi_extraction PASSED                       [ 33%]
tests/test_crypto.py::test_ua_header_generation PASSED                   [ 41%]
tests/test_mcp_server.py::test_server_tools_registration PASSED          [ 50%]
tests/test_mcp_server.py::test_server_resources_registration PASSED      [ 58%]
tests/test_mcp_server.py::test_server_prompts_registration PASSED        [ 66%]
tests/test_mcp_server.py::test_call_prerequisites_tool_via_server PASSED [ 75%]
tests/test_tools_offline.py::test_simulate_target_gpa_achievable PASSED  [ 83%]
tests/test_tools_offline.py::test_simulate_target_gpa_impossible PASSED  [ 91%]
tests/test_tools_offline.py::test_check_prerequisites PASSED             [100%]
============================== 12 passed in 2.07s ==============================
```

---

## 📁 Cấu trúc thư mục

```
sgu-academic-mcp/
├── sgu_mcp/
│   ├── config.py              # Cấu hình Pydantic BaseSettings
│   ├── server.py              # Entrypoint MCP Server (Stdio & SSE)
│   ├── core/
│   │   ├── crypto.py          # Reverse-engineered dynamic 'ua' header
│   │   ├── cache.py           # SQLite Caching Layer
│   │   └── sgu_client.py      # HTTP API Client kết nối thongtindaotao.sgu.edu.vn
│   ├── modules/
│   │   ├── schedule.py        # 5 Tools: Thời khóa biểu, đăng ký môn & kiểm tra trùng
│   │   ├── exams.py           # 2 Tools: Lịch thi & đếm ngược ngày thi
│   │   ├── academic.py        # 4 Tools: Hồ sơ, bảng điểm & mô phỏng GPA
│   │   └── tuition.py         # 4 Tools: Học phí, thông báo & môn tiên quyết
│   ├── resources/
│   │   └── content.py         # 4 MCP Resources ngữ cảnh học vụ
│   └── prompts/
│       └── templates.py       # 3 MCP Prompt templates
├── skills/
│   └── sgu-academic/
│       └── SKILL.md           # Agent Skill tích hợp cho AI assistants
├── hands_on_lab/
│   └── HANDS_ON_LAB.md        # Hướng dẫn thực hành từng bước (Hands-on Guide)
├── tests/                     # 12 unit tests tự động
├── Dockerfile                 # Container image build
├── docker-compose.yml         # Container orchestration
└── requirements.txt           # Python dependencies
```

---

## 🔒 Bảo mật & Quyền riêng tư

* **Xử lý cục bộ (Local Execution):** Mọi thông tin đăng nhập và dữ liệu học tập cá nhân được xử lý hoàn toàn trên máy cục bộ của người dùng.
* **Không lưu trữ tập trung:** Máy chủ không chuyển tiếp hoặc lưu trữ thông tin nhạy cảm lên bất kỳ server bên thứ ba nào.
* **File `.env` được bảo vệ:** Cấu hình git mặc định đã ignore `.env` và database cache để tránh vô tình công khai tài khoản.

---

## 📜 Giấy phép (License)

Dự án được phát hành theo giấy phép [MIT License](LICENSE).
Tự do sử dụng, chỉnh sửa và tích hợp cho các mục đích học tập và nghiên cứu cá nhân.
