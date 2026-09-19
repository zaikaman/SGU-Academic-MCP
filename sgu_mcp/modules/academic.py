"""
Module MCP Tools: Hồ sơ sinh viên, Bảng điểm & Học vụ SGU
Gọi API thật từ thongtindaotao.sgu.edu.vn
"""

from typing import Any

from sgu_mcp.core.sgu_client import sgu_client


async def tool_get_student_profile() -> dict[str, Any]:
    """
    Lấy thông tin cá nhân và hồ sơ đào tạo chính thức của sinh viên SGU.
    Bao gồm: Mã sinh viên, họ và tên, ngày sinh, lớp sinh hoạt, chuyên ngành, khoa, niên khóa, cố vấn học tập (CVHT).
    """
    raw_data = await sgu_client.get_student_info()
    data = raw_data.get("data", {})

    return {
        "ma_sinh_vien": data.get("ma_sv"),
        "ho_ten": data.get("ten_day_du"),
        "gioi_tinh": data.get("gioi_tinh"),
        "ngay_sinh": data.get("ngay_sinh"),
        "lop": data.get("lop"),
        "khoa": data.get("khoa"),
        "nganh": data.get("nganh"),
        "chuyen_nganh": data.get("chuyen_nganh"),
        "nien_khoa": data.get("nien_khoa"),
        "co_van_hoc_tap": {
            "ho_ten": data.get("ho_ten_cvht"),
            "email": data.get("email_cvht"),
            "dien_thoai": data.get("dien_thoai_cvht"),
        },
    }


async def tool_get_semester_grades(semester_id: str | None = None) -> dict[str, Any]:
    """
    Lấy bảng điểm học tập chi tiết của sinh viên theo từng học kỳ từ hệ thống SGU.
    Bao gồm: Điểm quá trình, điểm thi, điểm tổng kết hệ 10, điểm hệ 4, điểm chữ và trạng thái đạt/không đạt.
    """
    return await sgu_client.get_grades(semester_id=semester_id)


async def tool_calculate_gpa_summary(semester_id: str | None = None) -> dict[str, Any]:
    """
    Phân tích và tính toán tổng hợp kết quả học tập của sinh viên:
    - Tổng số tín chỉ đã học và đã tích lũy thành công.
    - Điểm trung bình học kỳ và GPA tích lũy.
    - Danh sách các môn học bị nợ (nếu có) cần học lại hoặc thi lại.
    """
    raw_data = await sgu_client.get_grades(semester_id=semester_id)
    data = raw_data.get("data", {})

    semesters = data.get("ds_diem_hocky", []) if isinstance(data, dict) else []

    cumulative_gpa_4 = None
    cumulative_gpa_10 = None
    total_credits_earned = 0
    latest_semester_name = None
    latest_semester_gpa = None
    failed_courses = []
    semester_summaries = []

    for sem in semesters:
        sem_name = sem.get("ten_hoc_ky")
        gpa_hk4 = sem.get("dtb_hk_he4")
        cum4 = sem.get("dtb_tich_luy_he_4")
        cum10 = sem.get("dtb_tich_luy_he_10")
        credits_accum = sem.get("so_tin_chi_dat_tich_luy")

        if cum4 and cumulative_gpa_4 is None:
            cumulative_gpa_4 = float(cum4)
            cumulative_gpa_10 = float(cum10) if cum10 else None
            try:
                total_credits_earned = int(credits_accum) if credits_accum else 0
            except Exception:
                total_credits_earned = 0
            latest_semester_name = sem_name
            latest_semester_gpa = float(gpa_hk4) if gpa_hk4 else None

        # Thu thập các môn nợ (nếu có)
        for m in sem.get("ds_diem_mon_hoc", []):
            if m.get("ket_qua") == 0 or m.get("diem_tk_chu") == "F":
                failed_courses.append(
                    {
                        "ten_mon": m.get("ten_mon"),
                        "ma_mon": m.get("ma_mon"),
                        "so_tc": m.get("so_tin_chi"),
                        "hoc_ky": sem_name,
                        "diem_tk": m.get("diem_tk"),
                    }
                )

        if gpa_hk4:
            semester_summaries.append(
                {
                    "hoc_ky": sem_name,
                    "gpa_he_4": float(gpa_hk4),
                    "gpa_tich_luy": float(cum4) if cum4 else None,
                    "tin_chi_tich_luy": credits_accum,
                    "xep_loai": sem.get("xep_loai_tkb_hk"),
                }
            )

    return {
        "gpa_tich_luy_he_4": cumulative_gpa_4,
        "gpa_tich_luy_he_10": cumulative_gpa_10,
        "tong_tin_chi_tich_luy": total_credits_earned,
        "hoc_ky_gan_nhat_co_diem": latest_semester_name,
        "gpa_hoc_ky_gan_nhat": latest_semester_gpa,
        "so_mon_no": len(failed_courses),
        "danh_sach_mon_no": failed_courses,
        "tong_so_hoc_ky": len(semester_summaries),
        "lich_su_hoc_ky": semester_summaries,
    }


async def tool_simulate_target_gpa(
    current_gpa: float, current_credits: int, target_gpa: float, remaining_credits: int
) -> dict[str, Any]:
    """
    Thuật toán mô phỏng mục tiêu tốt nghiệp:
    Tính toán xem sinh viên cần đạt điểm trung bình hệ 4 bao nhiêu ở các môn còn lại để đạt mức xếp loại mong muốn (ví dụ: Xuất sắc >= 3.6, Giỏi >= 3.2, Khá >= 2.5).
    """
    if remaining_credits <= 0:
        return {"error": "Số tín chỉ còn lại phải lớn hơn 0."}

    total_credits = current_credits + remaining_credits
    required_points = (target_gpa * total_credits) - (current_gpa * current_credits)
    required_avg_gpa = required_points / remaining_credits

    is_achievable = required_avg_gpa <= 4.0

    classification = (
        "Xuất sắc"
        if target_gpa >= 3.6
        else "Giỏi"
        if target_gpa >= 3.2
        else "Khá"
        if target_gpa >= 2.5
        else "Trung bình"
    )

    return {
        "gpa_hien_tai": current_gpa,
        "tin_chi_hien_tai": current_credits,
        "gpa_muc_tieu": target_gpa,
        "xep_loai_muc_tieu": classification,
        "tin_chi_con_lai": remaining_credits,
        "diem_he_4_trung_binh_can_dat": round(required_avg_gpa, 2),
        "co_kha_thi_khong": is_achievable,
        "loi_khuyen": (
            f"Mục tiêu KHẢ THI! Bạn cần duy trì điểm trung bình các môn tới là {round(required_avg_gpa, 2)} / 4.0."
            if is_achievable
            else f"Mục tiêu KHÔNG KHẢ THI về mặt toán học (cần đạt {round(required_avg_gpa, 2)} > 4.0). Bạn nên cân nhắc học cải thiện các môn điểm thấp."
        ),
    }

# [zaikaman commit 41: feat(academic): implement calculate_gpa_]
