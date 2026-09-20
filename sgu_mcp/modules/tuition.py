"""
Module MCP Tools: Học phí, Thông báo & Đăng ký môn học SGU
Gọi API thật từ thongtindaotao.sgu.edu.vn
"""

from typing import Any

from sgu_mcp.core.sgu_client import sgu_client

# Bảng tra cứu môn tiên quyết chính thức ngành CNTT trường Đại học Sài Gòn
SGU_IT_PREREQUISITES = {
    "Kỹ thuật lập trình": ["Nhập môn lập trình"],
    "Cấu trúc dữ liệu và giải thuật": ["Kỹ thuật lập trình"],
    "Lập trình hướng đối tượng": ["Kỹ thuật lập trình"],
    "Cơ sở dữ liệu": ["Nhập môn lập trình"],
    "Hệ điều hành": ["Kỹ thuật lập trình"],
    "Công nghệ phần mềm": ["Lập trình hướng đối tượng", "Cơ sở dữ liệu"],
    "Lập trình mạng": ["Mạng máy tính"],
    "Trí tuệ nhân tạo": ["Cấu trúc dữ liệu và giải thuật"],
    "Các công nghệ lập trình hiện đại": ["Công nghệ phần mềm"],
    "Phát triển ứng dụng Web nâng cao": ["Công nghệ phần mềm"],
    "Khóa luận tốt nghiệp": ["Công nghệ phần mềm", "Các công nghệ lập trình hiện đại"],
}


async def tool_get_tuition_fees() -> dict[str, Any]:
    """
    Tra cứu thông tin học phí của sinh viên từ hệ thống SGU.
    Bao gồm: Học phí từng học kỳ, số tiền được miễn giảm, tổng tiền đã thu, và số tiền CÒN NỢ đọng.
    """
    raw_data = await sgu_client.get_tuition()
    data = raw_data.get("data", {})
    fee_list = data.get("ds_hoc_phi_hoc_ky", []) if isinstance(data, dict) else []

    total_debt = 0
    formatted_fees = []

    for item in fee_list:
        debt_str = str(item.get("con_no") or "0").replace(",", "").replace(".", "")
        try:
            debt = int(debt_str)
        except Exception:
            debt = 0
        total_debt += debt

        formatted_fees.append(
            {
                "hoc_ky": item.get("ten_hoc_ky"),
                "hoc_phi": item.get("hoc_phi"),
                "mien_giam": item.get("mien_giam"),
                "phai_thu": item.get("phai_thu"),
                "da_dong": item.get("da_thu"),
                "con_no": item.get("con_no"),
                "ghi_chu": item.get("ghi_chu"),
            }
        )

    return {
        "tong_tien_no_hoc_phi": total_debt,
        "trang_thai_no": "Còn nợ học phí" if total_debt > 0 else "Đã hoàn thành toàn bộ học phí",
        "chi_tiet_hoc_phi": formatted_fees,
    }


async def tool_get_sgu_notifications(limit: int = 10) -> dict[str, Any]:
    """
    Lấy danh sách các thông báo mới nhất từ Ban Giám hiệu và Phòng Đào tạo SGU.
    Bao gồm: Lịch nghỉ lễ, thông báo đóng học phí, lịch xét tốt nghiệp, điều chỉnh lịch học.
    """
    raw_data = await sgu_client.get_notifications(limit=limit)
    data = raw_data.get("data", {})
    notices = data.get("ds_thong_bao", []) if isinstance(data, dict) else []

    result = []
    for n in notices:
        result.append(
            {
                "id": n.get("id"),
                "tieu_de": n.get("tieu_de"),
                "ngay_gui": n.get("ngay_gui"),
                "noi_dung": n.get("noi_dung"),
                "is_phai_xem": n.get("is_phai_xem"),
            }
        )

    return {"tong_thong_bao": len(result), "danh_sach_thong_bao": result}


async def tool_get_course_offerings(page: int = 1, limit: int = 20) -> dict[str, Any]:
    """
    Tra cứu danh mục các lớp học phần đang mở của trường SGU để phục vụ đăng ký môn học.
    Cho biết mã môn, tên môn, số tín chỉ, số lượng đã đăng ký (sl_dk) và số lượng slot còn lại (sl_cl).
    """
    raw_data = await sgu_client.get_course_catalog(page=page, limit=limit)
    data = raw_data.get("data", {})
    groups = data.get("ds_nhom_to", []) if isinstance(data, dict) else []

    courses = []
    for g in groups:
        courses.append(
            {
                "ma_mon": g.get("ma_mon"),
                "ten_mon": g.get("ten_mon"),
                "nhom_to": g.get("nhom_to"),
                "so_tin_chi": g.get("so_tc_so"),
                "lop": g.get("lop"),
                "da_dang_ky": g.get("sl_dk"),
                "tong_slot": g.get("sl_cp"),
                "slot_con_lai": g.get("sl_cl"),
                "thoi_khoa_bieu": g.get("tkb"),
                "con_cho": (g.get("sl_cl") or 0) > 0,
            }
        )

    return {"trang": page, "so_lop_tra_ve": len(courses), "danh_sach_lop_mo": courses}


async def tool_check_prerequisites(course_name: str) -> dict[str, Any]:
    """
    Kiểm tra điều kiện môn học tiên quyết đối với một môn học cụ thể trong chương trình đào tạo ngành CNTT SGU.
    Giúp sinh viên biết cần phải học và thi đậu môn nào trước khi được phép đăng ký môn này.
    """
    clean_name = course_name.strip().title()

    found_key = None
    for k in SGU_IT_PREREQUISITES:
        if clean_name.lower() in k.lower():
            found_key = k
            break

    if not found_key:
        return {
            "mon_hoc": course_name,
            "mon_tien_quyet": [],
            "thong_bao": f"Môn '{course_name}' không có điều kiện môn tiên quyết hoặc không nằm trong danh mục chuyên ngành CNTT.",
        }

    prereqs = SGU_IT_PREREQUISITES[found_key]
    return {
        "mon_hoc": found_key,
        "mon_tien_quyet": prereqs,
        "thong_bao": f"Để đăng ký môn '{found_key}', sinh viên SGU bắt buộc phải tích lũy đạt các môn sau: {', '.join(prereqs)}.",
    }

# [toansiuuu commit 52: fix prerequisite recursion check on circ]
