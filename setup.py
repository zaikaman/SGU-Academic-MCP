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

import argparse
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


def detect_docker_config(project_root: Path, server_name: str) -> tuple[dict, str]:
    """
    Tự động phát hiện môi trường Docker (Docker Native hoặc Docker qua WSL 2)
    và sinh cấu hình Stdio Bridge hoặc SSE tối ưu nhất.
    """
    # 1. Kiểm tra Docker Native (Windows/Linux/macOS)
    docker_bin = shutil.which("docker")
    if docker_bin:
        cfg = {
            "command": docker_bin.replace("\\", "/"),
            "args": [
                "exec",
                "-i",
                "sgu_mcp_academic_server",
                "python",
                "-m",
                "sgu_mcp.server",
                "--transport",
                "stdio",
            ],
        }
        return cfg, "Docker Native Stdio Bridge (exec -i)"

    # 2. Nếu chạy trên Windows, kiểm tra Docker daemon bên trong WSL 2
    if platform.system() == "Windows":
        try:
            res = subprocess.run(
                ["wsl", "-d", "Ubuntu", "-e", "which", "docker"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            if res.returncode == 0 and res.stdout.strip():
                cfg = {
                    "command": "wsl",
                    "args": [
                        "-d",
                        "Ubuntu",
                        "-e",
                        "docker",
                        "exec",
                        "-i",
                        "sgu_mcp_academic_server",
                        "python",
                        "-m",
                        "sgu_mcp.server",
                        "--transport",
                        "stdio",
                    ],
                }
                return cfg, "WSL Docker Stdio Bridge (wsl docker exec -i)"
        except Exception:
            pass

    # 3. Fallback: SSE qua cổng mạng
    return {
        "serverUrl": "http://localhost:8000/sse",
        "url": "http://localhost:8000/sse",
    }, "Docker SSE (http://localhost:8000/sse)"


def setup_wsl_and_docker_compatibility(project_root: Path, server_name: str, docker_desc: str):
    print("\n[Bước 4/4] Kiểm tra & Tích hợp WSL và Docker...")

    # 1. Kiểm tra & Cấu hình WSL (nếu máy chạy Windows)
    wsl_status = "Không phát hiện"
    if platform.system() == "Windows":
        try:
            res = subprocess.run(["wsl", "-e", "which", "python3"], capture_output=True, text=True, timeout=3)
            if res.returncode != 0:
                res = subprocess.run(["wsl", "which", "python3"], capture_output=True, text=True, timeout=3)
            if res.returncode == 0 and res.stdout.strip():
                wsl_python = res.stdout.strip()
                # Chuyển đổi đường dẫn sang WSL format (/mnt/c/...)
                path_str = str(project_root).replace("\\", "/")
                wsl_path = subprocess.run(
                    ["wsl", "wslpath", "-u", path_str], capture_output=True, text=True, timeout=3
                ).stdout.strip()

                wsl_config = {
                    "command": "wsl",
                    "args": ["-e", wsl_python, "-m", "sgu_mcp.server", "--transport", "stdio"],
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
    container_running = False
    try:
        check_cmd = (
            ["docker", "inspect", "--format={{.State.Status}}", "sgu_mcp_academic_server"]
            if shutil.which("docker")
            else ["wsl", "-d", "Ubuntu", "-e", "docker", "inspect", "--format={{.State.Status}}", "sgu_mcp_academic_server"]
        )
        res = subprocess.run(check_cmd, capture_output=True, text=True, timeout=3)
        if res.returncode == 0 and "running" in res.stdout.lower():
            container_running = True
    except Exception:
        pass

    if container_running:
        docker_status = f"Container đang chạy (sgu_mcp_academic_server) • Cơ chế: {docker_desc}"
    else:
        try:
            import httpx
            with httpx.Client(timeout=0.6) as client:
                resp = client.get("http://localhost:8000/health")
                if resp.status_code == 200:
                    docker_status = "Đang chạy qua SSE (http://localhost:8000/sse)"
        except Exception:
            docker_status = "Chưa bật container (chạy 'docker compose up -d' nếu muốn dùng)"

    print(f"  • Môi trường WSL:   {wsl_status}")
    print(f"  • Môi trường Docker: {docker_status}")


def print_dashboard(active_mode: str = "Windows Native (Stdio Default)"):
    print("\n" + "=" * 72)
    print(" HOÀN TẤT CÀI ĐẶT 1-CLICK TƯƠNG THÍCH ĐA NỀN TẢNG (0 CẦN CỜ LỆNH)!")
    print("=" * 72)
    print("Hệ thống đã tự động kích hoạt:")
    print(f" 1. [Chế độ Active cho IDEs]: {active_mode}")
    print("    -> Đã cấu hình cho Antigravity, Cursor, VS Code, Claude Desktop, Windsurf.")
    print(" 2. [WSL Native Profile]:")
    print("    -> Sẵn sàng trong .cursor/mcp.wsl.json & .vscode/mcp.wsl.json")
    print(" 3. [Docker Container Profile]:")
    print("    -> Sẵn sàng trong .cursor/mcp.docker.json & .vscode/mcp.docker.json")
    print("    -> Hỗ trợ cả Docker Stdio Bridge và Docker SSE.")
    print("=" * 72)


def main():
    print_banner()

    parser = argparse.ArgumentParser(description="SGU Academic MCP Server 1-Click Auto Setup")
    parser.add_argument("--docker", action="store_true", help="Ưu tiên kích hoạt cấu hình Docker Stdio Bridge cho toàn bộ IDEs")
    parser.add_argument("--sse", action="store_true", help="Cấu hình dùng SSE URL (http://localhost:8000/sse)")
    parser.add_argument("--port", type=int, default=8000, help="Cổng SSE khi dùng chế độ --sse (mặc định: 8000)")
    args, _ = parser.parse_known_args()

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

    docker_config, docker_desc = detect_docker_config(project_root, server_name)
    if args.sse:
        docker_config = {
            "serverUrl": f"http://localhost:{args.port}/sse",
            "url": f"http://localhost:{args.port}/sse",
        }
        docker_desc = f"Docker SSE (http://localhost:{args.port}/sse)"

    # Quyết định cấu hình áp dụng cho Global Clients:
    active_config = docker_config if (args.docker or args.sse) else stdio_config
    active_mode_name = docker_desc if (args.docker or args.sse) else "Windows/Linux Native (Stdio Default)"

    setup_env_file(project_root)
    setup_workspace_configs(project_root, server_name, stdio_config, docker_config)
    setup_global_clients(server_name, active_config)
    setup_wsl_and_docker_compatibility(project_root, server_name, docker_desc)
    print_dashboard(active_mode_name)


if __name__ == "__main__":
    main()

# [zaikaman commit 92: feat(setup): add --docker and --sse para]
