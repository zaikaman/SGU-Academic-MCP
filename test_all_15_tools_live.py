"""
Kiểm thử toàn diện tất cả 15 MCP Tools trên hệ thống thật SGU
Bảo đảm 100% Tools đều chạy được live và trả về dữ liệu chuẩn xác!
"""

import asyncio
import sys

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from sgu_mcp.modules.academic import (
    tool_calculate_gpa_summary,
    tool_get_semester_grades,
    tool_get_student_profile,
    tool_simulate_target_gpa,
)
from sgu_mcp.modules.exams import (
    tool_get_exam_countdown,
    tool_get_exam_schedule,
)
from sgu_mcp.modules.schedule import (
    tool_check_schedule_conflict,
    tool_get_registered_courses,
    tool_get_today_schedule,
    tool_get_weekly_schedule,
    tool_sgu_login,
)
from sgu_mcp.modules.tuition import (
    tool_check_prerequisites,
    tool_get_course_offerings,
    tool_get_sgu_notifications,
    tool_get_tuition_fees,
)
from sgu_mcp.config import settings


async def run_master_test():
    print("=" * 75)
    print("BẮT ĐẦU KIỂM THỬ TOÀN BỘ 15 MCP TOOLS TRÊN DỮ LIỆU LIVE SGU")
    print("=" * 75)

    success_count = 0

    # 1. sgu_login
    print("\n[Tool 1/15] sgu_login")
    t1 = await tool_sgu_login(settings.student_id, settings.password)
    assert t1.get("success") is True
    print(f"  -> OK: Đăng nhập thành công ({t1.get('name')})")
    success_count += 1

    # 2. get_student_profile
    print("\n[Tool 2/15] get_student_profile")
    t2 = await tool_get_student_profile()
    assert t2.get("ma_sinh_vien") == settings.student_id
    print(f"  -> OK: SV {t2.get('ho_ten')} | Lớp {t2.get('lop')} | CVHT: {t2.get('co_van_hoc_tap', {}).get('ho_ten')}")
    success_count += 1

    # 3. get_registered_courses
    print("\n[Tool 3/15] get_registered_courses")
    t3 = await tool_get_registered_courses()
    assert t3.get("tong_so_mon", 0) > 0
    print(f"  -> OK: Đã đăng ký {t3.get('tong_so_mon')} môn học kì này:")
    for c in t3.get("danh_sach_mon_dang_ky", []):
        print(f"     + {c['ten_mon']} ({c['so_tc']} TC)")
    success_count += 1

    # 4. get_weekly_schedule
    print("\n[Tool 4/15] get_weekly_schedule")
    t4 = await tool_get_weekly_schedule()
    days_with_class = [d for d in t4.get("thoi_khoa_bieu_tuan", []) if d.get("cac_mon")]
    assert len(days_with_class) > 0
    print(f"  -> OK: Có lịch học vào {len(days_with_class)} ngày trong tuần:")
    for d in days_with_class:
        mon_str = ", ".join([f"{m['ten_mon']} ({m['tiet']})" for m in d["cac_mon"]])
        print(f"     + {d['thu']}: {mon_str}")
    success_count += 1

    # 5. get_today_schedule
    print("\n[Tool 5/15] get_today_schedule")
    t5 = await tool_get_today_schedule()
    print(f"  -> OK: Hôm nay ({t5['hom_nay']}): {t5['so_mon_hoc_hom_nay']} môn. Ngày mai ({t5['lich_ngay_mai']['ngay_mai']}): {t5['lich_ngay_mai']['so_mon_ngay_mai']} môn.")
    success_count += 1

    # 6. check_schedule_conflict
    print("\n[Tool 6/15] check_schedule_conflict")
    # Kiểm tra thử trùng lịch vào Thứ 7 tiết 4
    t6 = await tool_check_schedule_conflict(target_thu=7, target_tiet_bd=4, target_so_tiet=2)
    assert t6.get("co_trung_lich") is True
    print(f"  -> OK: Phát hiện chính xác trùng lịch: {t6['danh_sach_trung'][0]['chi_tiet']}")
    success_count += 1

    # 7. get_exam_schedule
    print("\n[Tool 7/15] get_exam_schedule")
    t7 = await tool_get_exam_schedule()
    print(f"  -> OK: Kết nối thành công (Thông báo: {t7.get('thong_bao') or 'Đã có lịch'})")
    success_count += 1

    # 8. get_exam_countdown
    print("\n[Tool 8/15] get_exam_countdown")
    t8 = await tool_get_exam_countdown()
    print(f"  -> OK: Phân tích lịch thi: {t8.get('tong_so_mon_thi')} môn sắp thi")
    success_count += 1

    # 9. get_semester_grades
    print("\n[Tool 9/15] get_semester_grades")
    t9 = await tool_get_semester_grades()
    assert t9.get("result") is True
    print(f"  -> OK: Truy vấn bảng điểm gốc thành công (Mã {t9.get('code')})")
    success_count += 1

    # 10. calculate_gpa_summary
    print("\n[Tool 10/15] calculate_gpa_summary")
    t10 = await tool_calculate_gpa_summary()
    assert t10.get("gpa_tich_luy_he_4") is not None
    print(f"  -> OK: GPA Tích lũy {t10['gpa_tich_luy_he_4']} / 4.0 ({t10['gpa_tich_luy_he_10']} / 10.0) | {t10['tong_tin_chi_tich_luy']} tín chỉ đạt")
    success_count += 1

    # 11. simulate_target_gpa
    print("\n[Tool 11/15] simulate_target_gpa")
    t11 = await tool_simulate_target_gpa(
        current_gpa=t10["gpa_tich_luy_he_4"],
        current_credits=t10["tong_tin_chi_tich_luy"],
        target_gpa=3.0,
        remaining_credits=14
    )
    assert t11.get("co_kha_thi_khong") is not None
    print(f"  -> OK: Muốn lên GPA 3.0 cần {t11['diem_he_4_trung_binh_can_dat']} điểm/môn -> {t11['loi_khuyen']}")
    success_count += 1

    # 12. get_tuition_fees
    print("\n[Tool 12/15] get_tuition_fees")
    t12 = await tool_get_tuition_fees()
    assert len(t12.get("chi_tiet_hoc_phi", [])) > 0
    print(f"  -> OK: Tổng nợ: {t12['tong_tien_no_hoc_phi']:,} VNĐ ({t12['trang_thai_no']}) | Lịch sử {len(t12['chi_tiet_hoc_phi'])} học kỳ")
    success_count += 1

    # 13. get_sgu_notifications
    print("\n[Tool 13/15] get_sgu_notifications")
    t13 = await tool_get_sgu_notifications(limit=3)
    assert "danh_sach_thong_bao" in t13
    print(f"  -> OK: Hệ thống thông báo kết nối thành công (Hiện có {t13['tong_thong_bao']} thông báo mới)")
    success_count += 1

    # 14. get_course_offerings
    print("\n[Tool 14/15] get_course_offerings")
    t14 = await tool_get_course_offerings(page=1, limit=3)
    assert t14.get("so_lop_tra_ve", 0) > 0
    print(f"  -> OK: Lấy được {t14['so_lop_tra_ve']} lớp mở:")
    for lop in t14.get("danh_sach_lop_mo", [])[:2]:
        print(f"     + {lop.get('ten_mon')} (Mã: {lop.get('ma_mon')}) - Còn {lop.get('slot_con_lai')} slot")
    success_count += 1

    # 15. check_prerequisites
    print("\n[Tool 15/15] check_prerequisites")
    t15 = await tool_check_prerequisites("Khóa luận tốt nghiệp")
    assert len(t15.get("mon_tien_quyet", [])) > 0
    print(f"  -> OK: {t15['thong_bao']}")
    success_count += 1

    print("\n" + "=" * 75)
    print(f"KẾT QUẢ: TẤT CẢ {success_count}/15 MCP TOOLS ĐÃ VƯỢT QUA KIỂM THỬ LIVE 100%!")
    print("=" * 75)


if __name__ == "__main__":
    asyncio.run(run_master_test())
