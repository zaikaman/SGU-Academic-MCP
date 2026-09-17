"""
Module MCP Tools: Thời khóa biểu & Lịch học SGU
Gọi API thật từ thongtindaotao.sgu.edu.vn và bóc tách dữ liệu chuẩn xác
"""

import re
from datetime import datetime
from typing import Any

from sgu_mcp.core.sgu_client import sgu_client


def parse_tkb_string(tkb_str: str) -> list[dict[str, Any]]:
    """
    Bóc tách chuỗi thời khóa biểu dạng SGU:
    Ví dụ: 'Thứ 7,tiết 3->5,Ph C.HB406,GV Phạm Thi Vương,12/09/26 đến 19/12/26'
    """
    sessions: list[dict[str, Any]] = []
    if not tkb_str:
        return sessions

    for s in tkb_str.split("<hr>"):
        s = s.strip()
        if not s:
            continue
        parts = [p.strip() for p in s.split(",")]
        thu_part = parts[0] if len(parts) > 0 else ""
        tiet_part = parts[1] if len(parts) > 1 else ""
        phong_part = parts[2] if len(parts) > 2 else ""
        gv_part = parts[3] if len(parts) > 3 else ""
        date_part = parts[4] if len(parts) > 4 else ""

        thu_num = 0
        if "thứ" in thu_part.lower():
            digits = re.findall(r"\d+", thu_part)
            if digits:
                thu_num = int(digits[0])
        elif "chủ nhật" in thu_part.lower():
            thu_num = 8

        tbd, tkt, st = 0, 0, 0
        t_digits = re.findall(r"\d+", tiet_part)
        if len(t_digits) >= 2:
            tbd = int(t_digits[0])
            tkt = int(t_digits[1])
            st = tkt - tbd + 1
        elif len(t_digits) == 1:
            tbd = tkt = int(t_digits[0])
            st = 1

        sessions.append(
            {
                "thu_chu": thu_part,
                "thu_so": thu_num,
                "tiet_chu": tiet_part,
                "tiet_bat_dau": tbd,
                "tiet_ket_thuc": tkt,
                "so_tiet": st,
                "phong": phong_part,
                "giang_vien": gv_part,
                "thoi_gian": date_part,
            }
        )
    return sessions


async def tool_sgu_login(student_id: str, password: str) -> dict[str, Any]:
    """
    Đăng nhập vào hệ thống cổng đào tạo SGU bằng tài khoản sinh viên.
    Trả về thông tin phiên đăng nhập và mã token để thực hiện các yêu cầu tiếp theo.
    """
    return await sgu_client.login(username=student_id, password=password)


async def tool_get_registered_courses() -> dict[str, Any]:
    """
    Lấy danh sách các môn học và lớp học phần mà sinh viên ĐÃ ĐĂNG KÝ THÀNH CÔNG trong học kỳ hiện tại.
    Bao gồm: Mã môn, tên môn, số tín chỉ, nhóm tổ, phòng học, thứ và tiết học.
    """
    raw_data = await sgu_client.get_registered_courses()
    data = raw_data.get("data", {})
    courses = []

    for item in data.get("ds_kqdkmh", []):
        to_hoc = item.get("to_hoc", {})
        tkb_raw = to_hoc.get("tkb", "")
        sessions = parse_tkb_string(tkb_raw)

        courses.append(
            {
                "ma_mon": to_hoc.get("ma_mon"),
                "ten_mon": to_hoc.get("ten_mon"),
                "so_tc": to_hoc.get("so_tc"),
                "nhom_to": to_hoc.get("nhom_to"),
                "lop": to_hoc.get("lop"),
                "thoi_khoa_bieu_goc": tkb_raw,
                "cac_buoi_hoc": sessions,
                "trang_thai": item.get("trang_thai_mon"),
            }
        )

    return {"tong_so_mon": len(courses), "danh_sach_mon_dang_ky": courses}


async def tool_get_weekly_schedule(semester_id: str | None = None) -> dict[str, Any]:
    """
    Lấy thời khóa biểu học kỳ chi tiết theo tuần của sinh viên từ hệ thống đào tạo SGU.
    Tổng hợp và nhóm các buổi học theo từng thứ trong tuần (Thứ 2 đến Chủ Nhật).
    """
    raw_courses = await tool_get_registered_courses()
    courses = raw_courses.get("danh_sach_mon_dang_ky", [])

    day_schedule: dict[int, dict[str, Any]] = {
        2: {"thu": "Thứ Hai", "cac_mon": []},
        3: {"thu": "Thứ Ba", "cac_mon": []},
        4: {"thu": "Thứ Tư", "cac_mon": []},
        5: {"thu": "Thứ Năm", "cac_mon": []},
        6: {"thu": "Thứ Sáu", "cac_mon": []},
        7: {"thu": "Thứ Bảy", "cac_mon": []},
        8: {"thu": "Chủ Nhật", "cac_mon": []},
    }

    for c in courses:
        for s in c.get("cac_buoi_hoc", []):
            thu = s.get("thu_so")
            if thu in day_schedule:
                day_schedule[thu]["cac_mon"].append(
                    {
                        "ten_mon": c.get("ten_mon"),
                        "ma_mon": c.get("ma_mon"),
                        "so_tc": c.get("so_tc"),
                        "tiet": s.get("tiet_chu"),
                        "tiet_bat_dau": s.get("tiet_bat_dau"),
                        "tiet_ket_thuc": s.get("tiet_ket_thuc"),
                        "phong": s.get("phong"),
                        "giang_vien": s.get("giang_vien"),
                        "thoi_gian": s.get("thoi_gian"),
                    }
                )

    # Sắp xếp các môn trong ngày theo tiết bắt đầu
    for thu in day_schedule:
        day_schedule[thu]["cac_mon"].sort(key=lambda x: x["tiet_bat_dau"])

    return {"thoi_khoa_bieu_tuan": list(day_schedule.values())}


async def tool_get_today_schedule() -> dict[str, Any]:
    """
    Tra cứu nhanh lịch học ngày HÔM NAY của sinh viên dựa trên dữ liệu đăng ký môn học thật.
    Cho biết hôm nay có môn nào, học lúc mấy giờ, phòng nào, giảng viên nào.
    """
    today_weekday = datetime.now().weekday() + 2  # Python: 0=Mon -> SGU: 2=Thứ Hai
    weekly = await tool_get_weekly_schedule()
    day_list = weekly.get("thoi_khoa_bieu_tuan", [])

    day_names = {
        2: "Thứ Hai",
        3: "Thứ Ba",
        4: "Thứ Tư",
        5: "Thứ Năm",
        6: "Thứ Sáu",
        7: "Thứ Bảy",
        8: "Chủ Nhật",
    }
    today_name = day_names.get(today_weekday, f"Thứ {today_weekday}")

    today_item = next((d for d in day_list if d.get("thu") == today_name), None)
    today_classes = today_item.get("cac_mon", []) if today_item else []

    # Nếu hôm nay là cuối tuần, tính đúng ngày mai (nếu CN thì ngày mai là Thứ 2)
    tomorrow_weekday = 2 if today_weekday >= 8 else (today_weekday + 1)
    tomorrow_name = day_names.get(tomorrow_weekday, f"Thứ {tomorrow_weekday}")
    tomorrow_item = next((d for d in day_list if d.get("thu") == tomorrow_name), None)
    tomorrow_classes = tomorrow_item.get("cac_mon", []) if tomorrow_item else []

    return {
        "hom_nay": today_name,
        "so_mon_hoc_hom_nay": len(today_classes),
        "cac_mon_hom_nay": today_classes,
        "lich_ngay_mai": {
            "ngay_mai": tomorrow_name,
            "so_mon_ngay_mai": len(tomorrow_classes),
            "cac_mon_ngay_mai": tomorrow_classes,
        },
    }


async def tool_check_schedule_conflict(
    target_thu: int, target_tiet_bd: int, target_so_tiet: int
) -> dict[str, Any]:
    """
    Kiểm tra xem một môn học mới (theo thứ, tiết bắt đầu và số tiết) có bị TRÙNG LỊCH với các môn đã đăng ký của sinh viên hay không.
    Hỗ trợ sinh viên lập kế hoạch đăng ký học phần an toàn.
    """
    raw_courses = await tool_get_registered_courses()
    registered = raw_courses.get("danh_sach_mon_dang_ky", [])

    target_range = set(range(target_tiet_bd, target_tiet_bd + target_so_tiet))
    conflicts = []

    for c in registered:
        for s in c.get("cac_buoi_hoc", []):
            if s.get("thu_so") == target_thu:
                c_range = set(range(s.get("tiet_bat_dau"), s.get("tiet_ket_thuc") + 1))
                overlap = target_range.intersection(c_range)
                if overlap:
                    conflicts.append(
                        {
                            "ten_mon_bi_trung": c.get("ten_mon"),
                            "ma_mon": c.get("ma_mon"),
                            "tiet_bi_trung": sorted(overlap),
                            "chi_tiet": f"Đã có môn '{c.get('ten_mon')}' ({s.get('tiet_chu')}) tại phòng {s.get('phong')}",
                        }
                    )

    return {
        "co_trung_lich": len(conflicts) > 0,
        "so_lop_bi_trung": len(conflicts),
        "danh_sach_trung": conflicts,
    }

# [zaikaman commit 23: feat(schedule): implement get_weekly_sch]
