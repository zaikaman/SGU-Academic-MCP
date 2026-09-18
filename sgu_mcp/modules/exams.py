"""
Module MCP Tools: Khảo thí & Lịch thi SGU
Gọi API thật từ thongtindaotao.sgu.edu.vn
"""

from datetime import datetime
from typing import Any

from sgu_mcp.core.sgu_client import sgu_client


async def tool_get_exam_schedule(semester_id: str | None = None) -> dict[str, Any]:
    """
    Tra cứu lịch thi học kỳ chính thức của sinh viên từ hệ thống đào tạo SGU.
    Bao gồm: Môn thi, ngày thi, giờ thi, ca thi, phòng thi, hình thức thi và số báo danh (SBD).
    """
    return await sgu_client.get_exam_schedule(semester_id=semester_id)


async def tool_get_exam_countdown(semester_id: str | None = None) -> dict[str, Any]:
    """
    Phân tích lịch thi của sinh viên:
    1. Đếm ngược số ngày còn lại đến từng môn thi.
    2. Sắp xếp thứ tự các môn thi từ gần nhất đến xa nhất.
    3. Cảnh báo các ngày thi dồn dập (ví dụ: thi 2 môn trong cùng 1 ngày).
    """
    raw_data = await sgu_client.get_exam_schedule(semester_id=semester_id)
    exam_list = raw_data.get("data", []) if isinstance(raw_data.get("data"), list) else []

    today = datetime.now().date()
    upcoming_exams: list[dict[str, Any]] = []
    exams_by_date: dict[str, list[str]] = {}

    for exam in exam_list:
        date_str = exam.get("ngay_thi") or exam.get("ngay")
        exam_name = exam.get("ten_mon") or exam.get("ten_mon_hoc") or "Không rõ tên môn"

        days_left = None
        if date_str:
            try:
                # Định dạng phổ biến: DD/MM/YYYY hoặc YYYY-MM-DD
                if "/" in date_str:
                    exam_date = datetime.strptime(date_str.split()[0], "%d/%m/%Y").date()
                else:
                    exam_date = datetime.strptime(date_str.split()[0], "%Y-%m-%d").date()

                days_left = (exam_date - today).days
            except Exception:
                pass

        item = {
            "ten_mon": exam_name,
            "ngay_thi": date_str,
            "gio_thi": exam.get("gio_thi") or exam.get("tiet_bat_dau"),
            "phong_thi": exam.get("phong_thi") or exam.get("ten_phong"),
            "hinh_thuc": exam.get("hinh_thuc_thi"),
            "so_ngay_con_lai": days_left,
        }
        upcoming_exams.append(item)

        if date_str:
            exams_by_date.setdefault(date_str, []).append(exam_name)

    # Kiểm tra cảnh báo trùng ngày
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

# [toansiuuu commit 37: quick fix for null candidate number form]
