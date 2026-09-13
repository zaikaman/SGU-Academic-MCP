"""
SGU Academic MCP Server - Universal 1-Click Auto Setup Script
Tự động cấu hình MCP Server cho mọi IDE & AI Clients:
- Google Antigravity
- VS Code & GitHub Copilot
- Cursor IDE
- Claude Desktop
- Windsurf (Codeium)
- Cline / Roo Code
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
    print("=" * 70)
    print("   SGU ACADEMIC MCP SERVER - UNIVERSAL 1-CLICK AUTO SETUP")
    print("   (Antigravity • VS Code • Cursor • Claude • Windsurf • Cline)")
    print("=" * 70)


def setup_env_file(project_root: Path):
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"

    print("\n[Bước 1/3] Kiểm tra file cấu hình .env...")
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
        with open(env_file, "r", encoding="utf-8") as f:
            content = f.read()
            if "3122xxxxxx" in content:
                print("  [CẢNH BÁO] File .env đang dùng MSSV mẫu (3122xxxxxx).")
                print("  -> Hãy mở file .env và cập nhật tài khoản SGU của bạn để sử dụng dữ liệu thật.")
            else:
                print("  [OK] File .env đã sẵn sàng với tài khoản của bạn.")


def write_mcp_config(config_path: Path, server_name: str, server_config: dict, app_name: str) -> bool:
    """Ghi hoặc cập nhật mcpServers vào file JSON chỉ định."""
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config = {}
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except Exception as e:
                backup_path = config_path.with_suffix(".json.bak")
                shutil.copy(config_path, backup_path)
                print(f"  [!] {app_name}: File config cũ lỗi cú pháp, đã sao lưu sang {backup_path.name}")
                config = {}

        if not isinstance(config, dict):
            config = {}

        if "mcpServers" not in config:
            config["mcpServers"] = {}

        config["mcpServers"][server_name] = server_config

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print(f"  [OK] Đã cấu hình {app_name}")
        print(f"       -> {config_path}")
        return True
    except Exception as e:
        print(f"  [LỖI] Không thể cấu hình {app_name}: {e}")
        return False


def setup_workspace_configs(project_root: Path, server_name: str, server_config: dict):
    print("\n[Bước 2/3] Cấu hình Workspace Repo (VS Code & Cursor)...")

    # 1. Cursor Workspace (.cursor/mcp.json)
    cursor_workspace = project_root / ".cursor" / "mcp.json"
    write_mcp_config(cursor_workspace, server_name, server_config, "Cursor Workspace (.cursor/mcp.json)")

    # 2. VS Code Workspace (.vscode/mcp.json - chuẩn chính thức VS Code & GitHub Copilot Agent)
    vscode_workspace = project_root / ".vscode" / "mcp.json"
    write_mcp_config(vscode_workspace, server_name, server_config, "VS Code Workspace (.vscode/mcp.json)")


def setup_global_clients(project_root: Path, server_name: str, server_config: dict):
    print("\n[Bước 3/3] Tự động quét & cấu hình các AI Clients / IDE trên máy...")
    system = platform.system()
    home = Path.home()
    appdata = os.environ.get("APPDATA")
    
    clients_to_check = []

    # 1. Google Antigravity
    antigravity_dir = home / ".gemini" / "antigravity"
    antigravity_config_dir = home / ".gemini" / "config"
    if antigravity_dir.exists() or antigravity_config_dir.exists():
        clients_to_check.append(("Google Antigravity", antigravity_dir / "mcp_config.json"))
        clients_to_check.append(("Google Antigravity (Global Config)", antigravity_config_dir / "mcp_config.json"))

    # 2. Claude Desktop
    claude_path = None
    if system == "Windows" and appdata:
        claude_path = Path(appdata) / "Claude" / "claude_desktop_config.json"
    elif system == "Darwin":
        claude_path = home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    elif system == "Linux":
        claude_path = home / ".config" / "Claude" / "claude_desktop_config.json"
    
    if claude_path:
        # Nếu thư mục Claude tồn tại hoặc tạo file trực tiếp
        if claude_path.parent.exists() or system == "Windows":
            clients_to_check.append(("Claude Desktop", claude_path))

    # 3. Windsurf (Codeium)
    windsurf_path = home / ".codeium" / "windsurf" / "mcp_config.json"
    if windsurf_path.parent.exists():
        clients_to_check.append(("Windsurf IDE", windsurf_path))

    # 4. Cursor Global
    cursor_global = home / ".cursor" / "mcp.json"
    if cursor_global.parent.exists():
        clients_to_check.append(("Cursor (Global)", cursor_global))

    # 5. Cline Extension (VS Code)
    cline_path = None
    if system == "Windows" and appdata:
        cline_path = Path(appdata) / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json"
    elif system == "Darwin":
        cline_path = home / "Library" / "Application Support" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json"
    elif system == "Linux":
        cline_path = home / ".config" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json"
    
    if cline_path and cline_path.parent.exists():
        clients_to_check.append(("Cline (VS Code Extension)", cline_path))

    # 6. Roo Code Extension (VS Code)
    roo_path = None
    if system == "Windows" and appdata:
        roo_path = Path(appdata) / "Code" / "User" / "globalStorage" / "rooveterinaryinc.roo-cline" / "settings" / "cline_mcp_settings.json"
    elif system == "Darwin":
        roo_path = home / "Library" / "Application Support" / "Code" / "User" / "globalStorage" / "rooveterinaryinc.roo-cline" / "settings" / "cline_mcp_settings.json"
    elif system == "Linux":
        roo_path = home / ".config" / "Code" / "User" / "globalStorage" / "rooveterinaryinc.roo-cline" / "settings" / "cline_mcp_settings.json"
    
    if roo_path and roo_path.parent.exists():
        clients_to_check.append(("Roo Code (VS Code Extension)", roo_path))

    count = 0
    for app_name, cfg_path in clients_to_check:
        if write_mcp_config(cfg_path, server_name, server_config, app_name):
            count += 1

    if count == 0:
        print("  [INFO] Chưa phát hiện cài đặt Global của Claude Desktop hay Antigravity.")
        print("  -> Đừng lo, file cấu hình Workspace (.cursor/mcp.json và .vscode/mcp.json) đã được tạo sẵn!")


def print_cli_instructions(project_root: Path, python_exe: str):
    print("\n" + "=" * 70)
    print(" HƯỚNG DẪN DÀNH CHO CLI TOOLS (NẾU BẠN DÙNG TERMINAL)")
    print("=" * 70)
    print("1. Claude Code CLI:")
    print(f'   claude mcp add sgu_academic_server "{python_exe}" -m sgu_mcp.server --transport stdio')
    print("\n2. MCP Inspector (Giao diện web trực quan để test tool):")
    print(f'   npx @modelcontextprotocol/inspector "{python_exe}" -m sgu_mcp.server --transport stdio')
    print("\n3. Chạy trực tiếp qua lệnh Python:")
    print("   python -m sgu_mcp.server --transport stdio")
    print("=" * 70)


def main():
    print_banner()

    project_root = Path(__file__).resolve().parent
    python_exe = sys.executable.replace("\\", "/")
    server_name = "sgu_academic_server"

    print(f"Thư mục dự án: {project_root}")
    print(f"Python thực thi: {python_exe}")

    server_config = {
        "command": python_exe,
        "args": ["-m", "sgu_mcp.server", "--transport", "stdio"],
        "cwd": str(project_root).replace("\\", "/"),
        "env": {
            "PYTHONIOENCODING": "utf-8",
            "PYTHONUNBUFFERED": "1"
        }
    }

    setup_env_file(project_root)
    setup_workspace_configs(project_root, server_name, server_config)
    setup_global_clients(project_root, server_name, server_config)
    print_cli_instructions(project_root, python_exe)

    print("\n" + "=" * 70)
    print(" HOÀN TẤT CÀI ĐẶT 1-CLICK CHO MỌI NỀN TẢNG!")
    print("=" * 70)
    print("Bây giờ bạn chỉ cần:")
    print(" 1. Điền MSSV và Mật khẩu thật vào file .env (nếu chưa điền).")
    print(" 2. Mở thư mục này bằng VS Code, Cursor, hoặc mở Antigravity / Claude Desktop.")
    print(" 3. Trò chuyện và hỏi ngay: 'Xem lịch học hôm nay', 'Tính GPA tích lũy'...")
    print("=" * 70)


if __name__ == "__main__":
    main()
