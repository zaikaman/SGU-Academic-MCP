"""
Unit tests cho toàn bộ các module trong sgu_mcp/modules:
- academic.py
- exams.py
- schedule.py
- tuition.py
Đảm bảo 100% statement & branch coverage
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

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
    parse_tkb_string,
    tool_check_schedule_conflict,
    tool_get_registered_courses,
    tool_get_today_schedule,
    tool_get_weekly_schedule,
    tool_sgu_login,
)
from sgu_mcp.modules.tuition import (
    tool_get_course_offerings,
    tool_get_sgu_notifications,
    tool_get_tuition_fees,
)

# ==================== ACADEMIC MODULE TESTS ====================


@pytest.mark.asyncio
async def test_tool_get_student_profile():
    mock_data = {
        "data": {
            "ma_sv": "3122410001",
            "ten_day_du": "Nguyễn Văn A",
            "gioi_tinh": "Nam",
            "ngay_sinh": "01/01/2004",
            "lop": "DCT1221",
            "khoa": "Công nghệ thông tin",
            "nganh": "Công nghệ thông tin",
            "chuyen_nganh": "Kỹ thuật phần mềm",
            "nien_khoa": "2022-2026",
            "ho_ten_cvht": "TS. Nguyễn B",
            "email_cvht": "cvht@sgu.edu.vn",
            "dien_thoai_cvht": "0901234567",
        }
    }
    with patch(
        "sgu_mcp.modules.academic.sgu_client.get_student_info", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = mock_data
        profile = await tool_get_student_profile()

        assert profile["ma_sinh_vien"] == "3122410001"
        assert profile["ho_ten"] == "Nguyễn Văn A"
        assert profile["co_van_hoc_tap"]["ho_ten"] == "TS. Nguyễn B"


@pytest.mark.asyncio
async def test_tool_get_semester_grades():
    with patch(
        "sgu_mcp.modules.academic.sgu_client.get_grades", new_callable=AsyncMock
    ) as mock_grades:
        mock_grades.return_value = {"code": 200, "data": []}
        res = await tool_get_semester_grades("20241")
        assert res["code"] == 200
        mock_grades.assert_called_with(semester_id="20241")


@pytest.mark.asyncio
async def test_tool_calculate_gpa_summary():
    mock_data = {
        "data": {
            "ds_diem_hocky": [
                {
                    "ten_hoc_ky": "Học kỳ 1 - Năm học 2024-2025",
                    "dtb_hk_he4": "3.5",
                    "dtb_tich_luy_he_4": "3.4",
                    "dtb_tich_luy_he_10": "8.2",
                    "so_tin_chi_dat_tich_luy": "110",
                    "xep_loai_tkb_hk": "Giỏi",
                    "ds_diem_mon_hoc": [
                        {
                            "ten_mon": "Toán rời rạc",
                            "ma_mon": "MATH101",
                            "so_tin_chi": 3,
                            "diem_tk": 4.0,
                            "ket_qua": 0,
                            "diem_tk_chu": "D",
                        },
                        {
                            "ten_mon": "Lập trình C",
                            "ma_mon": "IT101",
                            "so_tin_chi": 3,
                            "diem_tk": 2.0,
                            "ket_qua": 1,
                            "diem_tk_chu": "F",
                        },
                        {
                            "ten_mon": "Triết học",
                            "ma_mon": "POL101",
                            "so_tin_chi": 2,
                            "diem_tk": 8.5,
                            "ket_qua": 1,
                            "diem_tk_chu": "A",
                        },
                    ],
                },
                {
                    "ten_hoc_ky": "Học kỳ 2 - Năm học 2023-2024",
                    "dtb_hk_he4": "3.2",
                    "dtb_tich_luy_he_4": "3.3",
                    "dtb_tich_luy_he_10": None,
                    "so_tin_chi_dat_tich_luy": "invalid_credits",
                    "xep_loai_tkb_hk": "Khá",
                    "ds_diem_mon_hoc": [],
                },
                {
                    "ten_hoc_ky": "Học kỳ phụ",
                    "dtb_hk_he4": None,
                    "dtb_tich_luy_he_4": None,
                    "dtb_tich_luy_he_10": None,
                    "so_tin_chi_dat_tich_luy": None,
                    "ds_diem_mon_hoc": [],
                },
            ]
        }
    }
    with patch(
        "sgu_mcp.modules.academic.sgu_client.get_grades", new_callable=AsyncMock
    ) as mock_grades:
        mock_grades.return_value = mock_data
        summary = await tool_calculate_gpa_summary()

        assert summary["gpa_tich_luy_he_4"] == 3.4
        assert summary["gpa_tich_luy_he_10"] == 8.2
        assert summary["tong_tin_chi_tich_luy"] == 110
        assert summary["hoc_ky_gan_nhat_co_diem"] == "Học kỳ 1 - Năm học 2024-2025"
        assert summary["gpa_hoc_ky_gan_nhat"] == 3.5
        assert summary["so_mon_no"] == 2
        assert len(summary["lich_su_hoc_ky"]) == 2


@pytest.mark.asyncio
async def test_tool_calculate_gpa_summary_non_dict():
    with patch(
        "sgu_mcp.modules.academic.sgu_client.get_grades", new_callable=AsyncMock
    ) as mock_grades:
        mock_grades.return_value = {"data": None}
        summary = await tool_calculate_gpa_summary()
        assert summary["tong_so_hoc_ky"] == 0


@pytest.mark.asyncio
async def test_tool_calculate_gpa_summary_invalid_credits():
    mock_data = {
        "data": {
            "ds_diem_hocky": [
                {
                    "ten_hoc_ky": "Học kỳ 1",
                    "dtb_hk_he4": "3.5",
                    "dtb_tich_luy_he_4": "3.4",
                    "dtb_tich_luy_he_10": "8.2",
                    "so_tin_chi_dat_tich_luy": "not_an_int",
                }
            ]
        }
    }
    with patch(
        "sgu_mcp.modules.academic.sgu_client.get_grades",
        new_callable=AsyncMock,
        return_value=mock_data,
    ):
        summary = await tool_calculate_gpa_summary()
        assert summary["tong_tin_chi_tich_luy"] == 0


@pytest.mark.asyncio
async def test_tool_simulate_target_gpa_edge_cases():
    # Test remaining_credits <= 0
    res_err = await tool_simulate_target_gpa(3.0, 100, 3.5, 0)
    assert "error" in res_err

    # Test Xuat sac (>= 3.6)
    res_xs = await tool_simulate_target_gpa(3.5, 100, 3.7, 20)
    assert res_xs["xep_loai_muc_tieu"] == "Xuất sắc"

    # Test Gioi (>= 3.2)
    res_g = await tool_simulate_target_gpa(3.0, 100, 3.3, 20)
    assert res_g["xep_loai_muc_tieu"] == "Giỏi"

    # Test Kha (>= 2.5)
    res_k = await tool_simulate_target_gpa(2.0, 100, 2.6, 20)
    assert res_k["xep_loai_muc_tieu"] == "Khá"

    # Test Trung binh (< 2.5)
    res_tb = await tool_simulate_target_gpa(2.0, 100, 2.2, 20)
    assert res_tb["xep_loai_muc_tieu"] == "Trung bình"


# ==================== EXAMS MODULE TESTS ====================


@pytest.mark.asyncio
async def test_tool_get_exam_schedule():
    with patch(
        "sgu_mcp.modules.exams.sgu_client.get_exam_schedule", new_callable=AsyncMock
    ) as mock_exam:
        mock_exam.return_value = {"code": 200, "data": []}
        res = await tool_get_exam_schedule("20241")
        assert res["code"] == 200
        mock_exam.assert_called_with(semester_id="20241")


@pytest.mark.asyncio
async def test_tool_get_exam_countdown():
    mock_data = {
        "data": [
            {
                "ten_mon": "Lập trình Web",
                "ngay_thi": "20/12/2026",
                "gio_thi": "08:00",
                "phong_thi": "A.101",
                "hinh_thuc_thi": "Tự luận",
            },
            {
                "ten_mon_hoc": "Cơ sở dữ liệu",
                "ngay": "20/12/2026",
                "tiet_bat_dau": "7",
                "ten_phong": "B.202",
                "hinh_thuc_thi": "Trắc nghiệm",
            },
            {
                "ngay_thi": "2026-12-25",
                "gio_thi": "07:30",
                "phong_thi": "C.303",
                "hinh_thuc_thi": "Vấn đáp",
            },
            {"ten_mon": "Môn Thi Không Có Ngày", "ngay_thi": None},
            {"ten_mon": "Môn Thi Ngày Lỗi", "ngay_thi": "invalid_date_format"},
        ]
    }

    with patch(
        "sgu_mcp.modules.exams.sgu_client.get_exam_schedule", new_callable=AsyncMock
    ) as mock_exam:
        mock_exam.return_value = mock_data
        countdown = await tool_get_exam_countdown()

        assert countdown["tong_so_mon_thi"] == 5
        # Warnings for 2 exams on 20/12/2026
        assert len(countdown["canh_bao_thi_don_dap"]) == 1
        assert "20/12/2026" in countdown["canh_bao_thi_don_dap"][0]


@pytest.mark.asyncio
async def test_tool_get_exam_countdown_non_list():
    with patch(
        "sgu_mcp.modules.exams.sgu_client.get_exam_schedule", new_callable=AsyncMock
    ) as mock_exam:
        mock_exam.return_value = {"data": None}
        countdown = await tool_get_exam_countdown()
        assert countdown["tong_so_mon_thi"] == 0
        assert countdown["canh_bao_thi_don_dap"] == []


# ==================== SCHEDULE MODULE TESTS ====================


def test_parse_tkb_string():
    # Empty
    assert parse_tkb_string("") == []
    assert parse_tkb_string(None) == []

    # Valid string with hr and various formats
    raw = (
        "Thứ 7,tiết 3->5,Ph C.HB406,GV Phạm Thi Vương,12/09/26 đến 19/12/26 <hr> "
        "<hr> "
        "Chủ nhật,tiết 7,Ph C.A101,GV Nguyễn Văn B,13/09/26 đến 20/12/26 <hr> "
        "Không có thứ,tiết không rõ,Ph D,GV C,2026 <hr> "
        "Chỉ có một phần"
    )
    sessions = parse_tkb_string(raw)
    assert len(sessions) == 4

    assert sessions[0]["thu_so"] == 7
    assert sessions[0]["tiet_bat_dau"] == 3
    assert sessions[0]["tiet_ket_thuc"] == 5
    assert sessions[0]["so_tiet"] == 3

    assert sessions[1]["thu_so"] == 8
    assert sessions[1]["tiet_bat_dau"] == 7
    assert sessions[1]["tiet_ket_thuc"] == 7
    assert sessions[1]["so_tiet"] == 1

    assert sessions[2]["thu_so"] == 0
    assert sessions[2]["so_tiet"] == 0


@pytest.mark.asyncio
async def test_tool_sgu_login():
    with patch("sgu_mcp.modules.schedule.sgu_client.login", new_callable=AsyncMock) as mock_login:
        mock_login.return_value = {"success": True}
        res = await tool_sgu_login("3122410001", "pass")
        assert res["success"] is True
        mock_login.assert_called_with(username="3122410001", password="pass")


@pytest.mark.asyncio
async def test_tool_get_registered_courses():
    mock_data = {
        "data": {
            "ds_kqdkmh": [
                {
                    "to_hoc": {
                        "ma_mon": "841401",
                        "ten_mon": "Lập trình Web",
                        "so_tc": "3",
                        "nhom_to": "01",
                        "lop": "DCT1221",
                        "tkb": "Thứ 2,tiết 1->3,Ph A.101,GV A,2026",
                    },
                    "trang_thai_mon": "Đã lưu vào CSDL",
                }
            ]
        }
    }
    with patch(
        "sgu_mcp.modules.schedule.sgu_client.get_registered_courses", new_callable=AsyncMock
    ) as mock_rc:
        mock_rc.return_value = mock_data
        courses = await tool_get_registered_courses()
        assert courses["tong_so_mon"] == 1
        assert courses["danh_sach_mon_dang_ky"][0]["ma_mon"] == "841401"


@pytest.mark.asyncio
async def test_tool_get_weekly_schedule():
    mock_courses = {
        "danh_sach_mon_dang_ky": [
            {
                "ten_mon": "Mạng máy tính",
                "ma_mon": "841101",
                "so_tc": "3",
                "cac_buoi_hoc": [
                    {
                        "thu_so": 2,
                        "tiet_chu": "tiết 4->6",
                        "tiet_bat_dau": 4,
                        "tiet_ket_thuc": 6,
                        "phong": "A.202",
                        "giang_vien": "GV B",
                        "thoi_gian": "2026",
                    },
                    {
                        "thu_so": 2,
                        "tiet_chu": "tiết 1->3",
                        "tiet_bat_dau": 1,
                        "tiet_ket_thuc": 3,
                        "phong": "A.201",
                        "giang_vien": "GV A",
                        "thoi_gian": "2026",
                    },
                    {
                        "thu_so": 99,  # Invalid day
                        "tiet_chu": "tiết 1",
                        "tiet_bat_dau": 1,
                        "tiet_ket_thuc": 1,
                        "phong": "",
                        "giang_vien": "",
                        "thoi_gian": "",
                    },
                ],
            }
        ]
    }
    with patch(
        "sgu_mcp.modules.schedule.tool_get_registered_courses", new_callable=AsyncMock
    ) as mock_trc:
        mock_trc.return_value = mock_courses
        weekly = await tool_get_weekly_schedule()
        thu_hai = next(d for d in weekly["thoi_khoa_bieu_tuan"] if d["thu"] == "Thứ Hai")
        assert len(thu_hai["cac_mon"]) == 2
        # Check sorting by tiet_bat_dau
        assert thu_hai["cac_mon"][0]["tiet_bat_dau"] == 1
        assert thu_hai["cac_mon"][1]["tiet_bat_dau"] == 4


@pytest.mark.asyncio
async def test_tool_get_today_schedule():
    weekly_mock = {
        "thoi_khoa_bieu_tuan": [
            {"thu": "Thứ Hai", "cac_mon": [{"ten_mon": "Môn Thứ Hai"}]},
            {"thu": "Chủ Nhật", "cac_mon": [{"ten_mon": "Môn Chủ Nhật"}]},
            {"thu": "Thứ Ba", "cac_mon": []},
            {"thu": "Thứ Tư", "cac_mon": []},
            {"thu": "Thứ Năm", "cac_mon": []},
            {"thu": "Thứ Sáu", "cac_mon": []},
            {"thu": "Thứ Bảy", "cac_mon": []},
        ]
    }

    # Case 1: Today is Sunday (weekday = 6) -> today_weekday = 8, tomorrow_weekday = 2 (Thứ Hai)
    mock_datetime = MagicMock()
    mock_datetime.now.return_value.weekday.return_value = 6

    with (
        patch("sgu_mcp.modules.schedule.datetime", mock_datetime),
        patch(
            "sgu_mcp.modules.schedule.tool_get_weekly_schedule",
            new_callable=AsyncMock,
            return_value=weekly_mock,
        ),
    ):
        res = await tool_get_today_schedule()
        assert res["hom_nay"] == "Chủ Nhật"
        assert res["so_mon_hoc_hom_nay"] == 1
        assert res["lich_ngay_mai"]["ngay_mai"] == "Thứ Hai"
        assert res["lich_ngay_mai"]["so_mon_ngay_mai"] == 1

    # Case 2: Today is Monday (weekday = 0) -> today_weekday = 2, tomorrow_weekday = 3 (Thứ Ba)
    mock_datetime.now.return_value.weekday.return_value = 0
    with (
        patch("sgu_mcp.modules.schedule.datetime", mock_datetime),
        patch(
            "sgu_mcp.modules.schedule.tool_get_weekly_schedule",
            new_callable=AsyncMock,
            return_value=weekly_mock,
        ),
    ):
        res2 = await tool_get_today_schedule()
        assert res2["hom_nay"] == "Thứ Hai"
        assert res2["lich_ngay_mai"]["ngay_mai"] == "Thứ Ba"
        assert res2["lich_ngay_mai"]["so_mon_ngay_mai"] == 0


@pytest.mark.asyncio
async def test_tool_check_schedule_conflict():
    mock_courses = {
        "danh_sach_mon_dang_ky": [
            {
                "ten_mon": "Lập trình mạng",
                "ma_mon": "NET101",
                "cac_buoi_hoc": [
                    {
                        "thu_so": 3,
                        "tiet_bat_dau": 1,
                        "tiet_ket_thuc": 3,
                        "tiet_chu": "1->3",
                        "phong": "A.101",
                    }
                ],
            }
        ]
    }
    with patch(
        "sgu_mcp.modules.schedule.tool_get_registered_courses",
        new_callable=AsyncMock,
        return_value=mock_courses,
    ):
        # Case 1: Conflict on Tuesday (3), periods 2 to 4 (overlap on 2, 3)
        res_conflict = await tool_check_schedule_conflict(
            target_thu=3, target_tiet_bd=2, target_so_tiet=3
        )
        assert res_conflict["co_trung_lich"] is True
        assert res_conflict["so_lop_bi_trung"] == 1
        assert res_conflict["danh_sach_trung"][0]["tiet_bi_trung"] == [2, 3]

        # Case 2: No conflict on Tuesday (3), periods 4 to 6
        res_no_conflict = await tool_check_schedule_conflict(
            target_thu=3, target_tiet_bd=4, target_so_tiet=3
        )
        assert res_no_conflict["co_trung_lich"] is False
        assert res_no_conflict["so_lop_bi_trung"] == 0

        # Case 3: Different day (Wednesday / Thứ 4)
        res_diff_day = await tool_check_schedule_conflict(
            target_thu=4, target_tiet_bd=1, target_so_tiet=3
        )
        assert res_diff_day["co_trung_lich"] is False
        assert res_diff_day["so_lop_bi_trung"] == 0


# ==================== TUITION MODULE TESTS ====================


@pytest.mark.asyncio
async def test_tool_get_tuition_fees():
    mock_data = {
        "data": {
            "ds_hoc_phi_hoc_ky": [
                {
                    "ten_hoc_ky": "HK 1 2024-2025",
                    "hoc_phi": "9,500,000",
                    "mien_giam": "0",
                    "phai_thu": "9,500,000",
                    "da_thu": "9,500,000",
                    "con_no": "0",
                    "ghi_chu": "",
                },
                {
                    "ten_hoc_ky": "HK 2 2024-2025",
                    "hoc_phi": "10,200,000",
                    "mien_giam": "0",
                    "phai_thu": "10,200,000",
                    "da_thu": "5,000,000",
                    "con_no": "5,200,000",
                    "ghi_chu": "Hạn đóng 30/03",
                },
                {"ten_hoc_ky": "HK Phụ", "con_no": "invalid_num"},
            ]
        }
    }
    with patch(
        "sgu_mcp.modules.tuition.sgu_client.get_tuition",
        new_callable=AsyncMock,
        return_value=mock_data,
    ):
        res = await tool_get_tuition_fees()
        assert res["tong_tien_no_hoc_phi"] == 5200000
        assert res["trang_thai_no"] == "Còn nợ học phí"
        assert len(res["chi_tiet_hoc_phi"]) == 3

    # Case 2: Zero debt & non-dict data
    with patch(
        "sgu_mcp.modules.tuition.sgu_client.get_tuition",
        new_callable=AsyncMock,
        return_value={"data": []},
    ):
        res_zero = await tool_get_tuition_fees()
        assert res_zero["tong_tien_no_hoc_phi"] == 0
        assert res_zero["trang_thai_no"] == "Đã hoàn thành toàn bộ học phí"


@pytest.mark.asyncio
async def test_tool_get_sgu_notifications():
    mock_data = {
        "data": {
            "ds_thong_bao": [
                {
                    "id": 1,
                    "tieu_de": "Thông báo nghỉ Tết",
                    "ngay_gui": "01/01/2026",
                    "noi_dung": "Nghỉ tết theo quy định",
                    "is_phai_xem": True,
                }
            ]
        }
    }
    with patch(
        "sgu_mcp.modules.tuition.sgu_client.get_notifications",
        new_callable=AsyncMock,
        return_value=mock_data,
    ):
        res = await tool_get_sgu_notifications(limit=5)
        assert res["tong_thong_bao"] == 1
        assert res["danh_sach_thong_bao"][0]["tieu_de"] == "Thông báo nghỉ Tết"

    # Non-dict fallback
    with patch(
        "sgu_mcp.modules.tuition.sgu_client.get_notifications",
        new_callable=AsyncMock,
        return_value={"data": None},
    ):
        res_none = await tool_get_sgu_notifications()
        assert res_none["tong_thong_bao"] == 0


@pytest.mark.asyncio
async def test_tool_get_course_offerings():
    mock_data = {
        "data": {
            "ds_nhom_to": [
                {
                    "ma_mon": "841401",
                    "ten_mon": "Lập trình Web",
                    "nhom_to": "01",
                    "so_tc_so": 3,
                    "lop": "DCT1221",
                    "sl_dk": 45,
                    "sl_cp": 50,
                    "sl_cl": 5,
                    "tkb": "Thứ 2",
                },
                {
                    "ma_mon": "841402",
                    "ten_mon": "Cơ sở dữ liệu",
                    "nhom_to": "02",
                    "so_tc_so": 3,
                    "lop": "DCT1222",
                    "sl_dk": 50,
                    "sl_cp": 50,
                    "sl_cl": 0,
                    "tkb": "Thứ 3",
                },
            ]
        }
    }
    with patch(
        "sgu_mcp.modules.tuition.sgu_client.get_course_catalog",
        new_callable=AsyncMock,
        return_value=mock_data,
    ):
        res = await tool_get_course_offerings(page=1, limit=10)
        assert res["so_lop_tra_ve"] == 2
        assert res["danh_sach_lop_mo"][0]["con_cho"] is True
        assert res["danh_sach_lop_mo"][1]["con_cho"] is False

    # Non-dict fallback
    with patch(
        "sgu_mcp.modules.tuition.sgu_client.get_course_catalog",
        new_callable=AsyncMock,
        return_value={"data": None},
    ):
        res_none = await tool_get_course_offerings()
        assert res_none["so_lop_tra_ve"] == 0
