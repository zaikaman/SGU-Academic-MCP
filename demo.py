"""
Script chạy thử nghiệm nhanh (Interactive CLI Demo) cho SGU Academic MCP Server
"""

import asyncio
import sys

# Đảm bảo hiển thị tiếng Việt và emoji tốt trên Windows console
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from sgu_mcp.modules.academic import tool_simulate_target_gpa
from sgu_mcp.modules.tuition import tool_check_prerequisites
from sgu_mcp.resources.content import SGU_RESOURCES
from sgu_mcp.core.crypto import SguEncryptor
from sgu_mcp.config import settings
from sgu_mcp.core.sgu_client import sgu_client


async def run_demo():
    print("=" * 60)
    print("DEMO NHANH SGU ACADEMIC MCP SERVER")
    print("=" * 60)

    # 1. Test thuật toán mã hóa UA
    enc = SguEncryptor()
    sample_ua = enc.generate_ua_header("/api/dkmh/w-locsinhvieninfo")
    print(f"\n[1] Thử nghiệm tạo Header 'ua' bảo mật SGU:")
    print(f"    Endpoint: /api/dkmh/w-locsinhvieninfo")
    print(f"    Dynamic UA: {sample_ua[:35]}... (Độ dài: {len(sample_ua)} chars)")

    # 2. Test Tool tra cứu môn tiên quyết
    print(f"\n[2] Thử nghiệm Tool 'check_prerequisites':")
    for subject in ["Lập trình mạng", "Công nghệ phần mềm", "Khóa luận tốt nghiệp"]:
        res = await tool_check_prerequisites(subject)
        prereqs = res.get("mon_tien_quyet", [])
        print(f"    • Môn: {subject} -> Môn tiên quyết: {prereqs if prereqs else 'Không có'}")

    # 3. Test Tool mô phỏng GPA mục tiêu
    print(f"\n[3] Thử nghiệm Tool 'simulate_target_gpa':")
    sim = await tool_simulate_target_gpa(
        current_gpa=3.0,
        current_credits=60,
        target_gpa=3.2,
        remaining_credits=30
    )
    print(f"    • GPA hiện tại: {sim['gpa_hien_tai']} ({sim['tin_chi_hien_tai']} TC)")
    print(f"    • Mục tiêu: Bằng {sim['xep_loai_muc_tieu']} (GPA {sim['gpa_muc_tieu']})")
    print(f"    • Kết quả: {sim['loi_khuyen']}")

    # 4. Test đọc Resource Chuẩn đầu ra tốt nghiệp SGU
    print(f"\n[4] Thử nghiệm đọc Resource 'sgu://graduation/standards':")
    lines = SGU_RESOURCES["sgu://graduation/standards"]["content"].strip().split("\n")
    for line in lines[:5]:
        print(f"    {line}")
    print("    ...")

    # 5. Kiểm tra kết nối API thật SGU nếu đã cấu hình tài khoản
    print(f"\n[5] Kiểm tra kết nối API trường (thongtindaotao.sgu.edu.vn):")
    if settings.student_id and settings.password and settings.student_id != "3122410001":
        print(f"    Đang thử đăng nhập tài khoản: {settings.student_id}...")
        login_res = await sgu_client.login()
        if login_res.get("success"):
            print(f"    Đăng nhập THÀNH CÔNG! Xin chào: {login_res.get('name')}")
        else:
            print(f"    Đăng nhập thất bại: {login_res.get('error')}")
    else:
        print("    (Chưa điền MSSV & mật khẩu thật trong .env - Hệ thống sẵn sàng kết nối khi bạn cập nhật)")

    print("\n" + "=" * 60)
    print("MCP Server da san sang phuc vu cac Tro ly AI!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_demo())
