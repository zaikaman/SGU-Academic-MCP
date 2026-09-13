import asyncio
import sys

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from sgu_mcp.modules.academic import tool_calculate_gpa_summary, tool_get_student_profile


async def check():
    profile = await tool_get_student_profile()
    summary = await tool_calculate_gpa_summary()

    print("=== THÔNG TIN SINH VIÊN SGU ===")
    print(f"• Họ và tên: {profile['ho_ten']} | MSSV: {profile['ma_sinh_vien']}")
    print(f"• Lớp: {profile['lop']} | Ngành: {profile['nganh']} ({profile['chuyen_nganh']})")
    print(f"• Cố vấn học tập: {profile['co_van_hoc_tap']['ho_ten']} ({profile['co_van_hoc_tap']['email']})")

    print("\n=== KẾT QUẢ ĐIỂM SỐ THỰC TẾ TỪ CỔNG ĐÀO TẠO SGU ===")
    print(f"• Điểm trung bình tích lũy (GPA Hệ 4): {summary['gpa_tich_luy_he_4']} / 4.00")
    print(f"• Điểm trung bình tích lũy (Hệ 10):    {summary['gpa_tich_luy_he_10']} / 10.00")
    print(f"• Tổng số tín chỉ đã tích lũy:         {summary['tong_tin_chi_tich_luy']} / 145 tín chỉ")
    print(f"• Học kỳ gần nhất có điểm:             {summary['hoc_ky_gan_nhat_co_diem']} (GPA học kỳ: {summary['gpa_hoc_ky_gan_nhat']})")
    print(f"• Số môn nợ đọng:                      {summary['so_mon_no']} môn")

    print("\n=== LỊCH SỬ KẾT QUẢ CÁC HỌC KỲ GẦN ĐÂY ===")
    for s in summary["lich_su_hoc_ky"][:5]:
        print(f"  - {s['hoc_ky']}: GPA {s['gpa_he_4']} (Tích lũy: {s['gpa_tich_luy']} - {s['tin_chi_tich_luy']} TC) -> Xếp loại: {s['xep_loai']}")


if __name__ == "__main__":
    asyncio.run(check())
