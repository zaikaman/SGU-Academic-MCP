#!/usr/bin/env python3
''''exec python3 "$0" "$@" # '''
"""
SGU Academic MCP Server - Universal 1-Click Zero-Flag Auto Setup
Tự động nhận diện và cấu hình tương thích đồng thời cả 3 môi trường trong 1 lần chạy duy nhất:
  1. Windows Native (Stdio Transport - Mặc định cho người dùng cá nhân)
  2. WSL Native (Linux Stdio / Remote Environment)
  3. Docker Container (SSE Transport - Port 8000)

Không cần truyền bất kỳ tham số hay cờ lệnh nào!
"""

import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

# Đảm bảo in tiếng Việt chuẩn xác trên mọi console (đặc biệt là Windows)
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def print_banner():
    print("=" * 72)
    print("   SGU ACADEMIC MCP SERVER - UNIVERSAL 1-CLICK AUTO SETUP")
    print("   Tự động tương thích 100%: Windows Native • WSL • Docker")
    print("   (Antigravity • VS Code • Cursor • Claude Desktop • Windsurf)")
    print("=" * 72)


def setup_env_file(project_root: Path):
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"

    print("\n[Bước 1/4] Kiểm tra file cấu hình .env...")
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
            except Exception:
                backup_path = config_path.with_suffix(".json.bak")
                shutil.copy(config_path, backup_path)
                config = {}

        if not isinstance(config, dict):
            config = {}

        if "mcpServers" not in config:
            config["mcpServers"] = {}

        config["mcpServers"][server_name] = server_config

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print(f"  [OK] Đã cấu hình: {app_name}")
        print(f"       -> {config_path}")
        return True
    except Exception as e:
        print(f"  [!] Bỏ qua {app_name}: {e}")
        return False


def setup_workspace_configs(project_root: Path, server_name: str, stdio_config: dict, docker_config: dict):
    print("\n[Bước 2/4] Cấu hình Workspace Repo (.cursor & .vscode)...")

    # 1. Cấu hình mặc định: Stdio Native (chạy ngay không cần mở port)
    cursor_workspace = project_root / ".cursor" / "mcp.json"
    vscode_workspace = project_root / ".vscode" / "mcp.json"
    write_mcp_config(cursor_workspace, server_name, stdio_config, "Cursor Workspace (Stdio Default)")
    write_mcp_config(vscode_workspace, server_name, stdio_config, "VS Code Workspace (Stdio Default)")

    # 2. Tạo sẵn profile Docker SSE (.cursor/mcp.docker.json & .vscode/mcp.docker.json)
    docker_cursor = project_root / ".cursor" / "mcp.docker.json"
    docker_vscode = project_root / ".vscode" / "mcp.docker.json"
    write_mcp_config(docker_cursor, server_name, docker_config, "Cursor Profile Docker (SSE)")
    write_mcp_config(docker_vscode, server_name, docker_config, "VS Code Profile Docker (SSE)")


def setup_global_clients(server_name: str, stdio_config: dict):
    print("\n[Bước 3/4] Quét & Tích hợp vào các AI Client / IDE trên máy...")
    system = platform.system()
    home = Path.home()
    appdata = os.environ.get("APPDATA")

    clients_to_check = []

    # 1. Google Antigravity
    antigravity_dir = home / ".gemini" / "antigravity"
    antigravity_config_dir = home / ".gemini" / "config"
    if antigravity_dir.exists() or antigravity_config_dir.exists():
        clients_to_check.append(("Google Antigravity", antigravity_dir / "mcp_config.json"))
        clients_to_check.append(("Google Antigravity (Global)", antigravity_config_dir / "mcp_config.json"))

    # 2. Claude Desktop
    claude_path = None
    if system == "Windows" and appdata:
        claude_path = Path(appdata) / "Claude" / "claude_desktop_config.json"
    elif system == "Darwin":
        claude_path = home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    elif system == "Linux":
        claude_path = home / ".config" / "Claude" / "claude_desktop_config.json"

    if claude_path:
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

    for app_name, cfg_path in clients_to_check:
        write_mcp_config(cfg_path, server_name, stdio_config, app_name)


def setup_wsl_and_docker_compatibility(project_root: Path, server_name: str):
    print("\n[Bước 4/4] Kiểm tra & Tích hợp WSL và Docker...")

    # 1. Kiểm tra & Cấu hình WSL (nếu máy chạy Windows)
    wsl_status = "Không phát hiện"
    if platform.system() == "Windows":
        try:
            res = subprocess.run(["wsl", "which", "python3"], capture_output=True, text=True, timeout=3)
            if res.returncode == 0 and res.stdout.strip():
                wsl_python = res.stdout.strip()
                # Chuyển đổi đường dẫn sang WSL format (/mnt/c/...)
                path_str = str(project_root).replace("\\", "/")
                wsl_path = subprocess.run(
                    ["wsl", "wslpath", "-u", path_str], capture_output=True, text=True, timeout=3
                ).stdout.strip()

                wsl_config = {
                    "command": wsl_python,
                    "args": ["-m", "sgu_mcp.server", "--transport", "stdio"],
                    "cwd": wsl_path,
                    "env": {"PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"},
                }
                # Tạo profile WSL trong repo
                write_mcp_config(project_root / ".cursor" / "mcp.wsl.json", server_name, wsl_config, "Cursor Profile WSL")
                write_mcp_config(project_root / ".vscode" / "mcp.wsl.json", server_name, wsl_config, "VS Code Profile WSL")
                wsl_status = f"Sẵn sàng (Python: {wsl_python})"
        except Exception:
            wsl_status = "Không khả dụng"
    else:
        wsl_status = "Đang chạy trực tiếp trên Linux / WSL"

    # 2. Kiểm tra Docker
    docker_status = "Chưa chạy"
    try:
        import httpx
        with httpx.Client(timeout=0.6) as client:
            resp = client.get("http://localhost:8000/health")
            if resp.status_code == 200:
                docker_status = "Đang chạy & Khỏe mạnh (http://localhost:8000/sse)"
    except Exception:
        docker_status = "Chưa bật container (chạy 'docker compose up -d' nếu muốn dùng)"

    print(f"  • Môi trường WSL:   {wsl_status}")
    print(f"  • Môi trường Docker: {docker_status}")


def print_dashboard():
    print("\n" + "=" * 72)
    print(" HOÀN TẤT CÀI ĐẶT 1-CLICK TƯƠNG THÍCH ĐA NỀN TẢNG (0 CẦN CỜ LỆNH)!")
    print("=" * 72)
    print("Hệ thống đã tự động kích hoạt:")
    print(" 1. [Windows Native] (Mặc định):")
    print("    -> Đã cấu hình Stdio chuẩn cho mọi IDE (Antigravity, Cursor, VS Code, Claude).")
    print("    -> Mở bất kỳ IDE nào là 15 Native Tools của SGU sẵn sàng ngay trong chat!")
    print(" 2. [WSL Native]:")
    print("    -> Đã tự động tạo profile Stdio cho Linux/WSL (.cursor/mcp.wsl.json).")
    print(" 3. [Docker Container]:")
    print("    -> Đã chuẩn bị sẵn docker-compose.yml và profile SSE (.cursor/mcp.docker.json).")
    print("=" * 72)


def main():
    print_banner()

    project_root = Path(__file__).resolve().parent
    python_exe = sys.executable.replace("\\", "/")
    server_name = "sgu_academic_server"

    stdio_config = {
        "command": python_exe,
        "args": ["-m", "sgu_mcp.server", "--transport", "stdio"],
        "cwd": str(project_root).replace("\\", "/"),
        "env": {
            "PYTHONIOENCODING": "utf-8",
            "PYTHONUNBUFFERED": "1",
        },
    }

    docker_config = {
        "url": "http://localhost:8000/sse",
    }

    setup_env_file(project_root)
    setup_workspace_configs(project_root, server_name, stdio_config, docker_config)
    setup_global_clients(server_name, stdio_config)
    setup_wsl_and_docker_compatibility(project_root, server_name)
    print_dashboard()


if __name__ == "__main__":
    main()
