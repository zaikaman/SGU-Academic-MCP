# TÀI LIỆU HƯỚNG DẪN THỰC HÀNH (HANDS-ON LAB)
### Môn học: Các Công nghệ Lập trình Hiện đại
### Chủ đề: Xây dựng MCP Server với Model Context Protocol SDK và kết nối Trợ lý AI Claude Desktop
**Thời lượng thực hành:** 30 – 45 phút  
**Đối tượng:** Sinh viên CNTT muốn tích hợp ứng dụng Python vào các Trợ lý AI (Claude Desktop, Cursor).

---

## 1. Mục tiêu học tập (Learning Objectives)
Sau khi hoàn thành bài thực hành này, sinh viên có khả năng:
1. Hiểu và giải thích được bản chất giao thức **Model Context Protocol (MCP)**: Phân biệt Tools, Resources và Prompts.
2. Sử dụng thư viện `mcp` (bản SDK 2.x) để định nghĩa các Tool nghiệp vụ có Pydantic type annotation và docstring chuẩn JSON Schema.
3. Cấu hình file `claude_desktop_config.json` để kết nối Claude Desktop với MCP Server cục bộ qua phương thức `stdio`.
4. Viết các bài kiểm thử tự động với `pytest` để kiểm chứng luồng hoạt động của MCP Server.

---

## 2. Chuẩn bị môi trường (Prerequisites)
1. Máy tính đã cài đặt Python 3.10+ (khuyến nghị Python 3.12).
2. Trợ lý ảo **Claude Desktop** (hoặc IDE **Cursor**).
3. Cài đặt các thư viện cần thiết:
   ```bash
   pip install mcp>=2.2.0 pydantic httpx pytest pytest-asyncio
   ```

---

## 3. Các bước thực hiện (Step-by-Step Guide)

### Bước 1: Khởi tạo MCPServer
Tạo file `my_mcp_server.py` với nội dung khởi tạo server:

```python
import asyncio
from mcp.server.mcpserver import MCPServer

# Khởi tạo instance MCPServer
server = MCPServer(
    name="my_academic_server",
    version="1.0.0",
    description="Demo MCP Server cho học vụ sinh viên"
)
```

### Bước 2: Định nghĩa Tool đầu tiên
Sử dụng decorator `@server.tool()` để đăng ký hàm tính toán học phí theo số tín chỉ:

```python
@server.tool(name="calculate_tuition", description="Tính toán học phí theo số lượng tín chỉ đăng ký")
def calculate_tuition(credits: int, fee_per_credit: int = 450000) -> dict:
    """
    Tính học phí:
    - credits: số tín chỉ đăng ký
    - fee_per_credit: mức học phí mỗi tín chỉ (mặc định 450.000đ/TC)
    """
    total = credits * fee_per_credit
    return {
        "so_tin_chi": credits,
        "don_gia": fee_per_credit,
        "tong_hoc_phi": total,
        "dinh_dang_tien": f"{total:,.0f} VNĐ"
    }
```

### Bước 3: Định nghĩa Resource đọc dữ liệu ngữ cảnh
Đăng ký một URI tài nguyên để AI đọc được quy định chuẩn đầu ra:

```python
@server.resource(uri="academic://graduation/standards", name="Chuẩn tốt nghiệp", mime_type="text/plain")
def get_graduation_rules() -> str:
    return "Yêu cầu tốt nghiệp: Tối thiểu 145 tín chỉ, GPA >= 2.0, chứng chỉ ngoại ngữ B1."
```

### Bước 4: Chạy server ở chế độ stdio
Thêm khối entrypoint vào cuối file:

```python
if __name__ == "__main__":
    asyncio.run(server.run_stdio_async())
```

Chạy thử nghiệm bằng dòng lệnh:
```bash
python my_mcp_server.py
```

### Bước 5: Tích hợp vào Claude Desktop
1. Mở file cấu hình Claude Desktop:
   * Trên Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   * Trên macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
2. Thêm cấu hình MCP server của bạn:
   ```json
   {
     "mcpServers": {
       "my_academic_server": {
         "command": "python",
         "args": ["D:/CCNLTHD/my_mcp_server.py"]
       }
     }
   }
   ```
3. Khởi động lại Claude Desktop. Bạn sẽ thấy biểu tượng chiếc búa (Tool) xuất hiện góc dưới ô chat!

---

## 4. Bài tập thực hành (Hands-on Exercises)

### Bài tập 1: Thêm Tool kiểm tra cảnh báo học vụ (10 phút)
* **Yêu cầu:** Viết thêm một tool tên `check_academic_warning(gpa: float, failed_credits: int)`:
  * Nếu `gpa < 1.2` hoặc `failed_credits > 24` $\rightarrow$ Trả về `{"canh_bao": True, "muc_do": "Cảnh cáo học vụ mức 1"}`.
  * Ngược lại $\rightarrow$ Trả về `{"canh_bao": False, "thong_bao": "Học lực bình thường"}`.
* **Đáp án gợi ý:**
  ```python
  @server.tool(name="check_academic_warning", description="Kiểm tra xem sinh viên có bị cảnh báo học vụ hay không")
  def check_academic_warning(gpa: float, failed_credits: int) -> dict:
      if gpa < 1.2 or failed_credits > 24:
          return {"canh_bao": True, "muc_do": "Cảnh cáo học vụ mức 1", "ly_do": "GPA quá thấp hoặc nợ > 24 tín chỉ"}
      return {"canh_bao": False, "thong_bao": "Học lực bình thường"}
  ```

### Bài tập 2: Thêm Prompt mẫu hướng dẫn AI ôn tập (10 phút)
* **Yêu cầu:** Đăng ký một prompt tên `exam_guide` hướng dẫn AI hỏi sinh viên về các môn chuẩn bị thi và lập lịch ôn tập.
* **Đáp án gợi ý:**
  ```python
  @server.prompt(name="exam_guide", description="Gợi ý lộ trình ôn thi")
  def prompt_exam_guide() -> str:
      return "Bạn là trợ lý học tập. Hãy hỏi sinh viên danh sách các môn thi sắp tới và hỗ trợ họ lập bảng phân chia thời gian ôn tập hợp lý."
  ```

---

## 5. Các lỗi thường gặp và cách khắc phục (Troubleshooting)

1. **Lỗi `ModuleNotFoundError: No module named 'mcp.server.fastmcp'`:**
   * *Nguyên nhân:* Phiên bản `mcp` 2.x đã đổi tên `FastMCP` thành `MCPServer`.
   * *Khắc phục:* Đổi import thành `from mcp.server.mcpserver import MCPServer`.

2. **Claude Desktop không nhận Tool (Không thấy icon cái búa):**
   * *Nguyên nhân:* Đường dẫn file Python trong `claude_desktop_config.json` bị sai hoặc chứa ký tự đặc biệt, hoặc môi trường Python không có sẵn thư viện `mcp`.
   * *Khắc phục:* Dùng đường dẫn tuyệt đối đến `python.exe` (ví dụ: `C:/Users/admin/AppData/Local/Programs/Python/Python312/python.exe`).

3. **Lỗi UnicodeEncodeError trên terminal Windows khi in tiếng Việt:**
   * *Khắc phục:* Đặt biến môi trường `$env:PYTHONIOENCODING='utf-8'` trước khi chạy.
