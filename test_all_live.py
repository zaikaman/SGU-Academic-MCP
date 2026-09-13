"""
Kiểm thử toàn diện 15 Tools của SGU MCP Server trực tiếp trên dữ liệu thật
"""

import asyncio
import json
import sys

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from sgu_mcp.core.sgu_client import sgu_client


async def probe_endpoints():
    print("Đăng nhập SGU...")
    login = await sgu_client.login()
    print("Đăng nhập:", login.get("success"), f"({login.get('name')})")

    endpoints_to_test = [
        ("Đăng ký môn học", "/api/dkmh/w-locdskqdkmhsinhvien", {"is_CVHT": False, "is_Clear": False}),
        ("Danh mục lớp mở", "/api/dkmh/w-locdsnhomto", {"is_CVHT": False, "additional": {"paging": {"limit": 5, "page": 1}, "ordering": [{"name": "", "order_type": ""}]}}),
        ("Bảng điểm sinh viên", "/api/srm/w-locdsdiemsinhvien", {}),
        ("Học kỳ kết quả học tập", "/api/srm/w-lochockydanhgia", {}),
        ("Tổng hợp học phí", "/api/rms/w-locdstonghophocphisv", {}),
        ("Chi tiết học phí theo HK", "/api/rms/w-locdschitiethocphisvtheohocky", {}),
        ("Học kỳ học phí", "/api/report/w-locdshockyhocphisinhvien", {}),
        ("Học kỳ lịch thi", "/api/report/w-locdshockylichthisinhvien", {}),
        ("Lịch thi theo HK", "/api/epm/w-locdslichthisvtheohocky", {}),
        ("Học kỳ TKB", "/api/sch/w-locdshockytkbuser", {}),
        ("TKB tuần", "/api/sch/w-locdstkbtuanusertheohocky", {}),
        ("Thông báo", "/api/web/w-locdsthongbao", {"filter": {"id": None, "is_noi_dung": True}, "additional": {"paging": {"limit": 5, "page": 1}, "ordering": [{"name": "ngay_gui", "order_type": 1}]}})
    ]

    print("\n" + "=" * 70)
    print("KẾT QUẢ GỌI TRỰC TIẾP TẤT CẢ ENDPOINTS CỦA SGU")
    print("=" * 70)

    for label, ep, payload in endpoints_to_test:
        try:
            res = await sgu_client._post_api(ep, payload=payload)
            code = res.get("code")
            result = res.get("result")
            has_data = bool(res.get("data"))
            msg = res.get("message", "")
            print(f"[{label:22}] {ep:38} -> code={code}, result={result}, has_data={has_data}")
            if not result and msg:
                print(f"   Lỗi: {msg[:100]}")
        except Exception as e:
            print(f"[{label:22}] {ep:38} -> EXCEPTION: {e}")


if __name__ == "__main__":
    asyncio.run(probe_endpoints())
