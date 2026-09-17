# SGU Academic MCP Server

[![CI Pipeline](https://github.com/zaikaman/SGU-Academic-MCP/actions/workflows/ci.yml/badge.svg)](https://github.com/zaikaman/SGU-Academic-MCP/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Model Context Protocol](https://img.shields.io/badge/MCP-Protocol-purple.svg)](https://modelcontextprotocol.io/)
[![Tests](https://img.shields.io/badge/tests-52%20passed-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](tests/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](Dockerfile)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A production-grade **Model Context Protocol (MCP)** Server bridging AI Assistants (Claude Desktop, Antigravity, VS Code, Cursor, Windsurf) directly with the **Saigon University (SGU) Academic Portal** (`thongtindaotao.sgu.edu.vn`).

---

## Giới thiệu

**SGU Academic MCP Server** được xây dựng theo chuẩn mở [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) của Anthropic. Hệ thống đóng vai trò cầu nối thông minh (Bridge Middleware), giúp các Trợ lý AI có thể tương tác trực tiếp với dữ liệu học tập thực tế từ cổng thông tin đào tạo Đại học Sài Gòn (SGU) bằng ngôn ngữ tự nhiên.

### Tính năng nổi bật

* **100% Dữ liệu thực tế:** Tích hợp trực tiếp với API cổng đào tạo SGU (`thongtindaotao.sgu.edu.vn`), không dùng dữ liệu giả lập.
* **Cơ chế Reverse-Engineered Security:** Tự động tạo dynamic header `ua` với thuật toán mã hóa timestamp + XOR bitwise, tương thích hoàn toàn với cơ chế bảo mật của cổng đào tạo.
* **Smart SQLite Caching:** Tự động cache kết quả học tập và thời khóa biểu cục bộ, đảm bảo tốc độ phản hồi < 0.05s và giảm thiểu áp lực request lên máy chủ trường.
* **Hỗ trợ đa phương thức truyền tải (Transports):**
  * `stdio`: Tích hợp chuẩn cho Claude Desktop, Cursor, Antigravity.
  * `SSE` (Server-Sent Events): Dùng khi triển khai dạng dịch vụ mạng LAN hoặc Web container.
* **Bộ tính năng phong phú:** 15 Tools, 4 Resources ngữ cảnh, và 3 Prompts mẫu thông minh.

---

## Kiến trúc hệ thống

```
┌────────────────────────────────────────────────────────┐
│                   Trợ lý AI (Clients)                  │
│ Claude Desktop │ Antigravity │ VS Code │ Cursor │ CLI  │
└───────────────────────────┬────────────────────────────┘
                            │ JSON-RPC (stdio / SSE)
                            ▼
┌───────────────────────────────────────────────────────────┐
│                   SGU ACADEMIC MCP SERVER                 │
│                                                           │
│  [15 MCP Tools]      [4 Resources]       [3 Prompts]      │
│  • TKB tuần / ngày   • Lộ trình CNTT     • Kế hoạch học   │
│  • Lịch thi & Đếm    • Chuẩn tốt nghiệp  • Ôn thi cấp tốc │
│  • Điểm & GPA audit  • Quy chế học vụ    • Audit hồ sơ    │
│  • Học phí & Nợ môn  • Danh bạ cơ sở                      │
│                                                           │
│  [Security & Performance Engine]                          │
│  • SguEncryptor: Thuật toán tạo header dynamic 'ua'       │
│  • SguCache: SQLite Caching & Fallback Controller         │
└───────────────────────────┬───────────────────────────────┘
                            │ HTTPS (REST API)
                            ▼
┌────────────────────────────────────────────────────────┐
│              Cổng thông tin đào tạo SGU                │
│              thongtindaotao.sgu.edu.vn                 │
└────────────────────────────────────────────────────────┘
```

---

## Danh mục năng lực MCP

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

## Cài đặt & Sử dụng (1-Click Setup)

### 1. Yêu cầu môi trường
* Python 3.10 trở lên

### 2. Các bước thiết lập

**Bước 1: Tải mã nguồn & cài đặt thư viện**
```bash
git clone https://github.com/zaikaman/SGU-Academic-MCP.git
cd SGU-Academic-MCP
pip install -r requirements.txt
```

**Bước 2: Cấu hình tài khoản sinh viên**
Tạo file `.env` từ `.env.example` và điền tài khoản SGU của bạn:
```env
SGU_STUDENT_ID=3122xxxxxx
SGU_PASSWORD=MatKhauCuaBan
```

**Bước 3: Tích hợp tự động 3-in-1 (Zero-Flag Universal 1-Click)**
Chạy script cài đặt tự động:
- **Trên Windows:** Nhấp đúp chuột vào file `setup.bat` (hoặc chạy `python setup.py`)
- **Trên Linux / WSL:** Chạy `bash setup.sh` (hoặc `python3 setup.py`)

> **Script `setup.py` tự động nhận diện và cấu hình đồng thời cả 3 môi trường:**
> 1. **Windows Native (Stdio Default):** Tự inject cấu hình Stdio vào **Antigravity** (`~/.gemini/...`), **Cursor** (`.cursor/mcp.json`), **VS Code** (`.vscode/mcp.json`), **Claude Desktop** (`%APPDATA%/Claude/...`), **Windsurf**...
> 2. **WSL Native:** Tự động phát hiện WSL (`python3`, chuyển đổi đường dẫn sang `/mnt/...`) và tạo sẵn profile `.cursor/mcp.wsl.json` & `.vscode/mcp.wsl.json`.
> 3. **Docker Container:** Tự động kiểm tra sức khỏe container và tạo sẵn profile SSE `.cursor/mcp.docker.json` & `.vscode/mcp.docker.json`.
>
> Sau khi chạy xong, chỉ cần mở bất kỳ IDE hoặc AI Client nào lên là toàn bộ 15 Native Tools của SGU đã sẵn sàng ngay trong khung chat!


---

## Trải nghiệm trò chuyện tự nhiên cùng Trợ lý AI (Native AI Chat)

Sau khi chạy **1-Click Setup**, bạn chỉ cần mở IDE (Google Antigravity, Cursor, VS Code, Claude Desktop...) và chat trực tiếp bằng tiếng Việt tự nhiên. AI sẽ tự động kích hoạt các Native MCP Tool tương ứng:

| Câu hỏi thực tế của sinh viên | MCP Tool được AI tự động gọi | Kết quả AI phản hồi |
| :--- | :--- | :--- |
| *"Hôm nay mình có tiết học nào không?"* | `get_today_schedule` | Liệt kê chi tiết môn học, phòng học, ca học, giảng viên hôm nay & ngày mai |
| *"Xem giúp mình học phí học kỳ này và nợ đọng"* | `get_tuition_fees` | Thống kê số tiền cần nộp, số tiền đã đóng, biên lai và số dư còn nợ |
| *"GPA hiện tại của mình bao nhiêu, có nợ môn nào không?"* | `calculate_gpa_summary` | Tổng kết GPA thang 4 & thang 10, tổng tín chỉ tích lũy và danh sách môn nợ |
| *"Mục tiêu tốt nghiệp loại Giỏi (GPA 3.2), các kỳ tới mình cần đạt bao nhiêu?"* | `simulate_target_gpa` | Thuật toán mô phỏng điểm trung bình tối thiểu cần đạt ở các tín chỉ còn lại |
| *"Sắp tới mình có lịch thi nào không, có bị trùng hay dồn dập không?"* | `get_exam_schedule`<br/>`get_exam_countdown` | Bảng đếm ngược ngày thi, số báo danh, phòng thi và cảnh báo thi 2 môn/ngày |
| *"Kỳ này mình tính đăng ký môn Lập trình mạng thì có cần học trước môn nào không?"* | `check_prerequisites` | Đối soát cây môn tiên quyết ngành CNTT và tư vấn lộ trình học phù hợp |

> [!TIP]
> **Không cần gõ lệnh hay nhớ tên hàm!** Bạn chỉ cần hỏi tự nhiên như nói chuyện với một người bạn cố vấn học tập SGU.

---

### Kiểm thử Server & Công cụ Developer (Developer Testing)

Dành cho các nhà phát triển (Developers) muốn kiểm thử trực tiếp giao thức MCP hoặc gỡ lỗi (debug):

* **MCP Inspector (Giao diện Web GUI trực quan để debug từng tool):**
  ```bash
  npx @modelcontextprotocol/inspector python -m sgu_mcp.server --transport stdio
  ```

* **Claude Code CLI (Thêm MCP Server vào CLI):**
  ```bash
  claude mcp add sgu_academic_server python -m sgu_mcp.server --transport stdio
  ```

* **Khởi chạy trực tiếp Server ở chế độ Stdio (Dòng lệnh):**
  ```bash
  python -m sgu_mcp.server --transport stdio
  ```

> **Dành cho Trợ lý AI (AI Agents):** Xem chi tiết quy chuẩn vận hành 100% Native MCP Tools tại [AGENTS.md](AGENTS.md) và hướng dẫn nghiệp vụ học vụ tại [skills/sgu-academic/SKILL.md](skills/sgu-academic/SKILL.md).



---

<details>
<summary><b>Cấu hình thủ công & Triển khai nâng cao (Docker, SSE, Manual JSON)</b></summary>

### Chế độ SSE (HTTP Web Service cho mạng LAN hoặc Web Client)
```bash
python -m sgu_mcp.server --transport sse --port 8000
```

### Triển khai với Docker & Docker Compose (SSE Mode)

Dự án đã được đóng gói container hóa chuẩn production với non-root user (`appuser`), Docker build cache, volume mount cho SQLite database, và endpoint Healthcheck tự động.

#### Cách 1: Sử dụng Docker Compose (Khuyên dùng)
```bash
# 1. Khởi động MCP Server ở chế độ nền (Background)
docker compose up -d --build

# 2. Xem logs hoạt động thời gian thực
docker compose logs -f

# 3. Kiểm tra trạng thái container và healthcheck
docker compose ps

# 4. Dừng dịch vụ
docker compose down
```

#### Cách 2: Sử dụng Docker CLI thuần
```bash
# Build image
docker build -t sgu-mcp-server:latest .

# Chạy container kèm mount thư mục data và nạp .env
docker run -d \
  --name sgu_mcp_academic_server \
  -p 8000:8000 \
  --env-file .env \
  -v ${PWD}/data:/app/data \
  sgu-mcp-server:latest
```

#### Các Endpoint hoạt động:
* **MCP SSE Endpoint:** `http://localhost:8000/sse` (Dành cho AI Agent kết nối qua mạng)
* **Healthcheck Endpoint:** `http://localhost:8000/health` (Trả về trạng thái dịch vụ `{"status": "healthy", ...}`)
* **Messages Endpoint:** `http://localhost:8000/messages/`


### Mẫu cấu hình thủ công JSON (Dành cho mọi Client)

Cấu trúc JSON này tương thích 100% với Claude Desktop, Antigravity, VS Code, Cursor, Windsurf, v.v.:
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
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```
</details>

---

## Kiểm thử tự động (Unit Tests & 100% Coverage)

Dự án đi kèm bộ test tự động sử dụng `pytest` với **độ bao phủ tuyệt đối 100%** toàn bộ mã nguồn (cả Statement Coverage và Branch Coverage):

```bash
# Chạy toàn bộ 52 test cases kèm báo cáo độ bao phủ
python -m pytest --cov=sgu_mcp --cov-branch --cov-report=term-missing tests/
```

Kết quả kiểm thử thực tế:
```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
collected 52 items

tests/test_cache.py ....                                                 [  7%]
tests/test_crypto.py ..                                                  [ 11%]
tests/test_mcp_server.py .............                                   [ 32%]
tests/test_modules.py ..................                                 [ 67%]
tests/test_sgu_client.py ...............                                 [ 94%]
tests/test_tools_offline.py ...                                          [100%]

=============================== tests coverage ================================
Name                           Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------------------------
sgu_mcp\__init__.py                1      0      0      0   100%
sgu_mcp\config.py                 12      0      0      0   100%
sgu_mcp\core\cache.py             45      0      6      0   100%
sgu_mcp\core\crypto.py            38      0      4      0   100%
sgu_mcp\core\sgu_client.py        76      0     12      0   100%
sgu_mcp\modules\academic.py       49      0     12      0   100%
sgu_mcp\modules\exams.py          31      0     12      0   100%
sgu_mcp\modules\schedule.py       84      0     34      0   100%
sgu_mcp\modules\tuition.py        45      0     12      0   100%
sgu_mcp\prompts\templates.py       2      0      0      0   100%
sgu_mcp\resources\content.py       2      0      0      0   100%
sgu_mcp\server.py                102      0      8      0   100%
--------------------------------------------------------------------------
TOTAL                            487      0    100      0   100%
======================== 52 passed, 1 warning in 6.49s ========================
```

---

## Cấu trúc thư mục

```
SGU-Academic-MCP/
├── AGENTS.md                  # Hướng dẫn đa môi trường & cây quyết định cho AI Agents
├── sgu_mcp/
│   ├── config.py              # Cấu hình Pydantic BaseSettings
│   ├── server.py              # Entrypoint MCP Server (Stdio & SSE)
│   ├── core/
│   │   ├── crypto.py          # Reverse-engineered dynamic 'ua' header
│   │   ├── cache.py           # SQLite Caching Layer & Fallback
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
│       └── SKILL.md           # Agent Skill nghiệp vụ học vụ SGU
├── hands_on_lab/
│   └── HANDS_ON_LAB.md        # Hướng dẫn thực hành từng bước (Hands-on Guide)
├── tests/                     # 52 unit tests tự động (100% Coverage)
│   ├── test_cache.py          # Kiểm thử SQLite Caching, TTL & Error handling
│   ├── test_crypto.py         # Kiểm thử tạo header 'ua' reverse-engineered
│   ├── test_sgu_client.py     # Kiểm thử API Client, Auto-login & HTTP communication
│   ├── test_modules.py        # Kiểm thử toàn diện 15 Tools & nghiệp vụ học vụ
│   ├── test_mcp_server.py     # Kiểm thử MCP Protocol (Tools, Resources, Prompts & Server Lifecycle)
│   └── test_tools_offline.py  # Kiểm thử offline mô phỏng GPA & môn tiên quyết
├── setup.py                   # Script cài đặt tự động 3-in-1 đa nền tảng (Polyglot)
├── setup.bat                  # 1-Click setup dành cho Windows
├── setup.sh                   # 1-Click setup dành cho Linux / WSL
├── Dockerfile                 # Container image build (Python 3.12-slim, non-root)
├── docker-compose.yml         # Container orchestration & live volume mount
└── requirements.txt           # Python dependencies
```

---

## Bảo mật & Quyền riêng tư

* **Xử lý cục bộ (Local Execution):** Mọi thông tin đăng nhập và dữ liệu học tập cá nhân được xử lý hoàn toàn trên máy cục bộ của người dùng.
* **Không lưu trữ tập trung:** Máy chủ không chuyển tiếp hoặc lưu trữ thông tin nhạy cảm lên bất kỳ server bên thứ ba nào.
* **File `.env` được bảo vệ:** Cấu hình git mặc định đã ignore `.env` và database cache để tránh vô tình công khai tài khoản.

---

## Giấy phép (License)

Dự án được phát hành theo giấy phép [MIT License](LICENSE).
Tự do sử dụng, chỉnh sửa và tích hợp cho các mục đích học tập và nghiên cứu cá nhân.
