"""
SGU Academic MCP Server - 1-Click Setup Script
Tự động cấu hình MCP Server cho Claude Desktop và Cursor IDE.
"""

import sys
import os
import json
import shutil
import platform
from pathlib import Path

# Đảm bảo in tiếng Việt chuẩn xác trên mọi console (đặc biệt là Windows)
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def print_banner():
    print("=" * 65)
    print(" SGU ACADEMIC MCP SERVER - 1-CLICK AUTO SETUP")
    print("=" * 65)


def get_claude_config_path() -> Path | None:
    system = platform.system()
    if system == "Windows":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "Claude" / "claude_desktop_config.json"
    elif system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    elif system == "Linux":
        return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"
    return None


def setup_env_file(project_root: Path):
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"

    print("\n[1/3] Kiểm tra file cấu hình .env...")
    if not env_file.exists():
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print("  [OK] Đã tự động tạo file .env từ mẫu .env.example")
        else:
            with open(env_file, "w", encoding="utf-8") as f:
                f.write("SGU_STUDENT_ID=3122xxxxxx\nSGU_PASSWORD=MatKhauCuaBan\n")
            print("  [OK] Đã tạo file .env mẫu mới")
        print("  -> Vui lòng mở file .env để điền MSSV và Mật khẩu của bạn nếu chưa điền.")
    else:
        # Kiểm tra nhanh nội dung .env
        with open(env_file, "r", encoding="utf-8") as f:
            content = f.read()
            if "3122xxxxxx" in content:
                print("  [CẢNH BÁO] File .env đang dùng MSSV mẫu (3122xxxxxx).")
                print("  -> Hãy mở file .env và cập nhật tài khoản SGU của bạn để sử dụng dữ liệu thật.")
            else:
                print("  [OK] File .env đã sẵn sàng với tài khoản của bạn.")


def setup_claude_desktop(project_root: Path, python_exe: str) -> bool:
    print("\n[2/3] Cấu hình cho Claude Desktop...")
    claude_path = get_claude_config_path()
    if not claude_path:
        print("  [CẢNH BÁO] Không xác định được thư mục Claude Desktop trên hệ điều hành này.")
        return False

    config = {}
    claude_dir = claude_path.parent

    try:
        claude_dir.mkdir(parents=True, exist_ok=True)
        if claude_path.exists():
            try:
                with open(claude_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except Exception as e:
                backup_path = claude_path.with_suffix(".json.bak")
                shutil.copy(claude_path, backup_path)
                print(f"  [CẢNH BÁO] File config cũ bị lỗi cú pháp, đã sao lưu sang {backup_path.name}")
                config = {}

        if "mcpServers" not in config:
            config["mcpServers"] = {}

        # Cấu hình chuẩn cho SGU Academic Server
        config["mcpServers"]["sgu_academic_server"] = {
            "command": python_exe,
            "args": ["-m", "sgu_mcp.server", "--transport", "stdio"],
            "cwd": str(project_root).replace("\\", "/"),
            "env": {
                "PYTHONIOENCODING": "utf-8"
            }
        }

        with open(claude_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print(f"  [OK] Đã tự động tích hợp thành công vào Claude Desktop!")
        print(f"       Đường dẫn config: {claude_path}")
        return True
    except Exception as e:
        print(f"  [LỖI] Lỗi khi ghi file Claude Desktop config: {e}")
        return False


def setup_cursor(project_root: Path, python_exe: str) -> bool:
    print("\n[3/3] Cấu hình Workspace cho Cursor / Antigravity...")
    cursor_dir = project_root / ".cursor"
    cursor_config_path = cursor_dir / "mcp.json"

    try:
        cursor_dir.mkdir(parents=True, exist_ok=True)
        config = {}
        if cursor_config_path.exists():
            try:
                with open(cursor_config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except Exception:
                config = {}

        if "mcpServers" not in config:
            config["mcpServers"] = {}

        config["mcpServers"]["sgu_academic_server"] = {
            "command": python_exe,
            "args": ["-m", "sgu_mcp.server", "--transport", "stdio"],
            "cwd": str(project_root).replace("\\", "/"),
            "env": {
                "PYTHONIOENCODING": "utf-8"
            }
        }

        with open(cursor_config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print(f"  [OK] Đã tạo file cấu hình workspace Cursor (.cursor/mcp.json)!")
        return True
    except Exception as e:
        print(f"  [LỖI] Lỗi khi cấu hình Cursor: {e}")
        return False


def main():
    print_banner()

    project_root = Path(__file__).resolve().parent
    python_exe = sys.executable.replace("\\", "/")

    print(f"Thư mục dự án: {project_root}")
    print(f"Python thực thi: {python_exe}")

    setup_env_file(project_root)
    setup_claude_desktop(project_root, python_exe)
    setup_cursor(project_root, python_exe)

    print("\n" + "=" * 65)
    print(" HOÀN TẤT CÀI ĐẶT 1-CLICK!")
    print("=" * 65)
    print("Bây giờ bạn chỉ cần:")
    print(" 1. Điền tài khoản thật vào file .env (nếu chưa điền).")
    print(" 2. Khởi động lại Claude Desktop (hoặc mở folder này trong Cursor).")
    print(" 3. Bắt đầu hỏi điểm, lịch thi, thời khóa biểu SGU.")
    print("=" * 65)


if __name__ == "__main__":
    main()
