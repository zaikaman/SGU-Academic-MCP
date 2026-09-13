import asyncio
import sys

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from sgu_mcp.modules.schedule import (
    tool_get_registered_courses,
    tool_get_weekly_schedule,
    tool_get_today_schedule,
    tool_check_schedule_conflict,
)


async def check():
    print("=== TEST 1: Registered Courses ===")
    reg = await tool_get_registered_courses()
    print("Tổng số môn đăng ký học kỳ 1 (2026-2027):", reg["tong_so_mon"])
    for c in reg["danh_sach_mon_dang_ky"]:
        print(f"  • {c['ten_mon']} ({c['so_tc']} TC) - Mã: {c['ma_mon']}")

    print("\n=== TEST 2: Weekly Schedule (Nhóm theo thứ) ===")
    weekly = await tool_get_weekly_schedule()
    for d in weekly["thoi_khoa_bieu_tuan"]:
        if d["cac_mon"]:
            print(f"[{d['thu']}]:")
            for m in d["cac_mon"]:
                print(f"   + {m['ten_mon']}: {m['tiet']} | Phòng: {m['phong']} | {m['giang_vien']}")

    print("\n=== TEST 3: Lịch học Hôm nay & Ngày mai ===")
    today = await tool_get_today_schedule()
    print(f"Hôm nay ({today['hom_nay']}): Có {today['so_mon_hoc_hom_nay']} môn.")
    print(f"Ngày mai ({today['lich_ngay_mai']['ngay_mai']}): Có {today['lich_ngay_mai']['so_mon_ngay_mai']} môn:")
    for m in today["lich_ngay_mai"]["cac_mon_ngay_mai"]:
        print(f"   * {m['ten_mon']}: {m['tiet']} ({m['phong']}) - {m['giang_vien']}")

    print("\n=== TEST 4: Kiểm tra Trùng lịch học ===")
    # Thử kiểm tra trùng lịch: Giả sử sinh viên muốn đăng ký 1 lớp vào Thứ 7 tiết 4 (2 tiết)
    # Lớp này sẽ trùng với môn 'Các công nghệ lập trình hiện đại' (Thứ 7 tiết 3->5 của Thầy Vương)
    conflict = await tool_check_schedule_conflict(target_thu=7, target_tiet_bd=4, target_so_tiet=2)
    print("Kiểm tra đăng ký thêm môn vào Thứ 7 (tiết 4-5):")
    print("  • Có bị trùng lịch không?:", conflict["co_trung_lich"])
    for item in conflict["danh_sach_trung"]:
        print(f"  • Chi tiết: {item['chi_tiet']}")


if __name__ == "__main__":
    asyncio.run(check())
