"""
Module MCP Tools: Khảo thí & Lịch thi SGU
Gọi API thật từ thongtindaotao.sgu.edu.vn
"""

from datetime import datetime
from typing import Any

from sgu_mcp.config import VN_TZ
from sgu_mcp.core.sgu_client import sgu_client
from sgu_mcp.modules.schedule import resolve_campus


async def tool_get_exam_schedule(semester_id: str | None = None) -> dict[str, Any]:
    """
    Tra cứu lịch thi học kỳ chính thức của sinh viên từ hệ thống đào tạo SGU.
    Bao gồm: Môn thi, ngày thi, giờ thi, ca thi, phòng thi, hình thức thi và số báo danh (SBD).
    """
    res = await sgu_client.get_exam_schedule(semester_id=semester_id)
    raw_data = res.get("data", {}) if isinstance(res, dict) else {}

    # Trích xuất danh sách môn thi từ cả 2 dạng: data là dict (API thật) hoặc data là list (mock test)
    if isinstance(raw_data, dict):
        raw_exams = raw_data.get("ds_lich_thi", [])
    elif isinstance(raw_data, list):
        raw_exams = raw_data
    else:
        raw_exams = []

    clean_exams: list[dict[str, Any]] = []
    for item in raw_exams:
        if isinstance(item, dict):
            room = item.get("ma_phong") or item.get("phong_thi") or item.get("ten_phong") or ""
            exam_name = item.get("ten_mon") or item.get("ten_mon_hoc") or "Không rõ tên môn"
            clean_item = {
                "ma_mon": item.get("ma_mon"),
                "ten_mon": exam_name,
                "ngay_thi": item.get("ngay_thi") or item.get("ngay"),
                "gio_thi": item.get("gio_bat_dau")
                or item.get("gio_thi")
                or item.get("tiet_bat_dau"),
                "tiet_bat_dau": item.get("tiet_bat_dau"),
                "so_tiet": item.get("so_tiet"),
                "thoi_gian_lam_bai": f"{item.get('so_phut', '')} phút"
                if item.get("so_phut")
                else None,
                "phong_thi": room,
                "co_so": resolve_campus(room),
                "dia_diem_thi": (item.get("dia_diem_thi") or "").replace("<br>", " ").strip(),
                "hinh_thuc_thi": item.get("hinh_thuc_thi"),
                "to_thi": item.get("to_thi"),
                "nhom_thi": item.get("nhom_thi"),
                "si_so": item.get("si_so"),
                "ky_thi": item.get("ky_thi"),
            }
            clean_exams.append(clean_item)

    return {
        "code": res.get("code", 200) if isinstance(res, dict) else 200,
        "success": True,
        "hoc_ky": semester_id or (raw_data.get("hoc_ky") if isinstance(raw_data, dict) else None),
        "tong_so_mon_thi": len(clean_exams),
        "data": clean_exams,
        "ds_lich_thi": clean_exams,
        "thong_bao": res.get("thong_bao") if (isinstance(res, dict) and not clean_exams) else None,
    }


async def tool_get_exam_countdown(semester_id: str | None = None) -> dict[str, Any]:
    """
    Phân tích lịch thi của sinh viên:
    1. Đếm ngược số ngày còn lại đến từng môn thi.
    2. Sắp xếp thứ tự các môn thi từ gần nhất đến xa nhất.
    3. Cảnh báo các ngày thi dồn dập (ví dụ: thi 2 môn trong cùng 1 ngày hoặc thi 2 ngày liên tiếp).
    """
    raw_res = await tool_get_exam_schedule(semester_id=semester_id)
    exam_list = raw_res.get("ds_lich_thi") or raw_res.get("data") or []
    if not isinstance(exam_list, list):
        exam_list = []

    today = datetime.now(VN_TZ).date()
    upcoming_exams: list[dict[str, Any]] = []
    exams_by_date: dict[str, list[str]] = {}

    for exam in exam_list:
        if not isinstance(exam, dict):
            continue
        date_str = exam.get("ngay_thi") or exam.get("ngay")
        exam_name = exam.get("ten_mon") or exam.get("ten_mon_hoc") or "Không rõ tên môn"
        room_name = exam.get("phong_thi") or exam.get("ten_phong") or exam.get("ma_phong")

        days_left = None
        parsed_date = None
        if date_str:
            try:
                # Định dạng phổ biến: DD/MM/YYYY hoặc YYYY-MM-DD
                if "/" in str(date_str):
                    parsed_date = datetime.strptime(str(date_str).split()[0], "%d/%m/%Y").date()
                else:
                    parsed_date = datetime.strptime(str(date_str).split()[0], "%Y-%m-%d").date()

                days_left = (parsed_date - today).days
            except Exception:
                pass

        item = {
            "ma_mon": exam.get("ma_mon"),
            "ten_mon": exam_name,
            "ngay_thi": date_str,
            "gio_thi": exam.get("gio_thi") or exam.get("gio_bat_dau") or exam.get("tiet_bat_dau"),
            "phong_thi": room_name,
            "co_so": exam.get("co_so") or resolve_campus(room_name),
            "hinh_thuc": exam.get("hinh_thuc_thi") or exam.get("hinh_thuc"),
            "so_ngay_con_lai": days_left,
        }
        upcoming_exams.append(item)

        if date_str:
            exams_by_date.setdefault(str(date_str), []).append(exam_name)

    # Kiểm tra cảnh báo trùng ngày hoặc thi dồn dập
    warnings = []
    for d, names in exams_by_date.items():
        if len(names) > 1:
            warnings.append(
                f"Cảnh báo: Ngày {d} bạn có {len(names)} môn thi cùng ngày ({', '.join(names)})!"
            )

    return {
        "tong_so_mon_thi": len(upcoming_exams),
        "danh_sach_thi": sorted(
            upcoming_exams,
            key=lambda x: (x["so_ngay_con_lai"] is None, x["so_ngay_con_lai"] or 999),
        ),
        "canh_bao_thi_don_dap": warnings,
    }
