"""Kiểm thử các nhánh biên còn lại: cấu hình múi giờ, logging Docker,
luồng fallback của SGU API client và thời khóa biểu/lịch thi."""

import importlib
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from sgu_mcp.config import VN_TZ
from sgu_mcp.core.sgu_client import SguApiClient
from sgu_mcp.modules.exams import tool_get_exam_countdown, tool_get_exam_schedule
from sgu_mcp.modules.schedule import (
    tool_get_registered_courses,
    tool_get_today_schedule,
    tool_get_weekly_schedule,
)

# ==================== CONFIG & LOGGING ====================


def test_config_timezone_fallback_and_clock(monkeypatch):
    """time.tzset lỗi + thiếu zoneinfo -> fallback GMT+7, đồng thời kiểm tra get_vietnam_now."""
    import sgu_mcp.config as config_module

    def broken_tzset():
        raise RuntimeError("tzset not available")

    monkeypatch.setattr(time, "tzset", broken_tzset, raising=False)
    monkeypatch.setitem(sys.modules, "zoneinfo", None)

    try:
        reloaded = importlib.reload(config_module)
        assert reloaded.VN_TZ.utcoffset(None) == timedelta(hours=7)
        now = reloaded.get_vietnam_now()
        assert now.tzinfo is not None
    finally:
        monkeypatch.undo()
        importlib.reload(config_module)


def test_docker_log_mirroring(monkeypatch):
    """Trong container: log được nhân bản sang /proc/1/fd/2."""
    import sgu_mcp.server as server_module

    logger = logging.getLogger("sgu_mcp.server")
    monkeypatch.setattr(logger, "handlers", [])
    monkeypatch.setattr(os, "getpid", lambda: 4321)
    monkeypatch.setattr(os.path, "exists", lambda path: path == "/proc/1/fd/2")
    monkeypatch.setattr(os, "access", lambda path, mode: True)
    file_handler = MagicMock()
    monkeypatch.setattr(logging, "FileHandler", MagicMock(return_value=file_handler))

    try:
        importlib.reload(server_module)
        assert file_handler in logger.handlers
        file_handler.setFormatter.assert_called_once()
    finally:
        monkeypatch.undo()
        logger.handlers.clear()
        importlib.reload(server_module)


def test_docker_log_mirroring_failure_is_ignored(monkeypatch):
    """Không mở được /proc/1/fd/2 thì server vẫn khởi động bình thường."""
    import sgu_mcp.server as server_module

    logger = logging.getLogger("sgu_mcp.server")
    monkeypatch.setattr(logger, "handlers", [])
    monkeypatch.setattr(os, "getpid", lambda: 4321)
    monkeypatch.setattr(os.path, "exists", lambda path: True)
    monkeypatch.setattr(os, "access", lambda path, mode: True)
    monkeypatch.setattr(logging, "FileHandler", MagicMock(side_effect=OSError("no fd")))

    try:
        importlib.reload(server_module)
    finally:
        monkeypatch.undo()
        logger.handlers.clear()
        importlib.reload(server_module)


# ==================== SGU API CLIENT ====================


@pytest.mark.asyncio
async def test_post_api_non_500_http_error():
    client = SguApiClient()
    client.access_token = "tok"

    mock_resp = MagicMock()
    mock_resp.status_code = 403
    mock_resp.text = "Forbidden"

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        res = await client._post_api("/api/forbidden")

    assert res["success"] is False
    assert "HTTP 403" in res["error"]
    assert res["details"] == "Forbidden"


@pytest.mark.asyncio
async def test_weekly_schedule_resolves_current_semester(monkeypatch):
    """Không truyền học kỳ -> tự lấy học kỳ hiện tại, fallback 20261 khi cổng trả None."""
    client = SguApiClient()
    client.access_token = "tok"

    async def fake_semesters():
        return {"current_semester_id": None, "semesters": []}

    monkeypatch.setattr(client, "get_semesters_list", fake_semesters)
    mock_post = AsyncMock(return_value={"code": 200, "data": {}})
    monkeypatch.setattr(client, "_post_api", mock_post)

    res = await client.get_weekly_schedule()

    assert res == {"code": 200, "data": {}}
    assert mock_post.await_args.kwargs["payload"]["filter"]["hoc_ky"] == 20261


@pytest.mark.asyncio
async def test_weekly_schedule_invalid_semester_id(monkeypatch):
    """Mã học kỳ không phải số -> dùng 20261."""
    client = SguApiClient()
    client.access_token = "tok"

    mock_post = AsyncMock(return_value={"code": 200, "data": {}})
    monkeypatch.setattr(client, "_post_api", mock_post)

    await client.get_weekly_schedule("hoc-ky-khong-hop-le")

    assert mock_post.await_args.kwargs["payload"]["filter"]["hoc_ky"] == 20261


@pytest.mark.asyncio
async def test_weekly_schedule_falls_back_to_registered_courses(monkeypatch):
    """API tuần lỗi -> trả về danh sách môn đã đăng ký."""
    client = SguApiClient()
    client.access_token = "tok"

    fallback = {"tong_so_mon": 0, "danh_sach_mon_dang_ky": []}

    async def fake_registered():
        return fallback

    monkeypatch.setattr(client, "get_registered_courses", fake_registered)
    monkeypatch.setattr(client, "_post_api", AsyncMock(return_value={"code": 500}))

    res = await client.get_weekly_schedule("20261")

    assert res == fallback


@pytest.mark.asyncio
async def test_exam_schedule_invalid_semester_id(monkeypatch):
    """Mã học kỳ không phải số ở lịch thi -> dùng 20261."""
    client = SguApiClient()
    client.access_token = "tok"

    mock_post = AsyncMock(return_value={"code": 200, "data": {}})
    monkeypatch.setattr(client, "_post_api", mock_post)

    await client.get_exam_schedule("hk-khong-hop-le")

    assert mock_post.await_args.kwargs["payload"]["filter"]["hoc_ky"] == 20261


# ==================== EXAMS MODULE ====================


@pytest.mark.asyncio
async def test_tool_get_exam_schedule_dict_payload():
    """API thật trả data dạng dict kèm phần tử không phải dict."""
    payload = {
        "code": 200,
        "data": {
            "ds_lich_thi": [
                {
                    "ma_mon": "841401",
                    "ten_mon": "Lập trình Web",
                    "ma_phong": "C.A101",
                    "ngay_thi": "20/12/2026",
                    "gio_bat_dau": "08:00",
                    "so_phut": 90,
                    "dia_diem_thi": "Cơ sở chính<br>Phòng C.A101",
                    "hinh_thuc_thi": "Tự luận",
                    "to_thi": 1,
                    "nhom_thi": "01",
                    "si_so": 40,
                    "ky_thi": "Học kỳ 1",
                },
                "du-lieu-khong-hop-le",
            ],
            "hoc_ky": "20261",
        },
    }

    with patch(
        "sgu_mcp.modules.exams.sgu_client.get_exam_schedule", new_callable=AsyncMock
    ) as mock_exam:
        mock_exam.return_value = payload
        res = await tool_get_exam_schedule()

    assert res["code"] == 200
    assert res["tong_so_mon_thi"] == 1
    assert res["hoc_ky"] == "20261"
    assert res["data"][0]["thoi_gian_lam_bai"] == "90 phút"
    assert res["data"][0]["co_so"] == "Cơ sở chính (273 An Dương Vương, Q.5)"


@pytest.mark.asyncio
async def test_tool_get_exam_schedule_without_room_and_notice():
    """Môn thi thiếu phòng, thiếu tên và không có thông báo."""
    payload = {"code": 200, "data": {"ds_lich_thi": [{"ma_mon": "X"}]}}

    with patch(
        "sgu_mcp.modules.exams.sgu_client.get_exam_schedule", new_callable=AsyncMock
    ) as mock_exam:
        mock_exam.return_value = payload
        res = await tool_get_exam_schedule()

    assert res["data"][0]["ten_mon"] == "Không rõ tên môn"
    assert res["data"][0]["co_so"] == "Chưa xác định"
    assert res["data"][0]["thoi_gian_lam_bai"] is None
    assert res["thong_bao"] is None


@pytest.mark.asyncio
async def test_tool_get_exam_countdown_non_list_and_invalid_items():
    """ds_lich_thi là dict và danh sách chứa phần tử không phải dict."""
    payload = {"ds_lich_thi": {"bat_thuong": True}, "data": {"bat_thuong": True}}

    with patch("sgu_mcp.modules.exams.tool_get_exam_schedule", new_callable=AsyncMock) as mock_exam:
        mock_exam.return_value = payload
        res = await tool_get_exam_countdown()
        assert res["tong_so_mon_thi"] == 0

        mock_exam.return_value = {
            "ds_lich_thi": ["khong-phai-dict", {"ten_mon": "Môn C", "ngay_thi": None}]
        }
        res_mixed = await tool_get_exam_countdown()

    assert res_mixed["tong_so_mon_thi"] == 1
    assert res_mixed["canh_bao_thi_don_dap"] == []


# ==================== SCHEDULE MODULE ====================


@pytest.mark.asyncio
async def test_tool_get_registered_courses_from_weekly_schedule():
    """Cổng ĐKMH đóng -> trích môn từ thời khóa biểu tuần, chống trùng buổi học."""
    weekly = {
        "data": {
            "ds_tuan_tkb": [
                {
                    "ds_thoi_khoa_bieu": [
                        {
                            "ma_mon": "A1",
                            "ma_nhom": "01",
                            "ten_mon": "Môn A",
                            "so_tin_chi": 3,
                            "day_phong_hk": "DCT1221",
                            "ten_giang_vien": "GV A",
                            "tiet_bat_dau": 1,
                            "so_tiet": 3,
                            "thu_kieu_so": 8,
                            "ma_phong": "C.A101",
                            "ngay_hoc": "2026-11-01T00:00:00",
                        },
                        {
                            "ma_mon": "A1",
                            "ma_nhom": "01",
                            "ten_mon": "Môn A",
                            "ten_giang_vien": "GV A",
                            "tiet_bat_dau": 1,
                            "so_tiet": 3,
                            "thu_kieu_so": 8,
                            "ma_phong": "C.A101",
                            "ngay_hoc": "2026-11-08T00:00:00",
                        },
                        {
                            "ma_mon": "B1",
                            "ma_nhom": "02",
                            "ten_mon": "Môn B",
                            "so_tin_chi": 2,
                            "ten_giang_vien": "GV B",
                            "tiet_bat_dau": 4,
                            "so_tiet": 2,
                            "thu_kieu_so": 2,
                            "ma_phong": "4.S_QP01",
                            "ngay_hoc": "2026-11-02T00:00:00",
                        },
                    ]
                }
            ]
        }
    }

    with (
        patch(
            "sgu_mcp.modules.schedule.sgu_client.get_registered_courses",
            new_callable=AsyncMock,
            return_value={"data": {"ds_kqdkmh": []}},
        ),
        patch(
            "sgu_mcp.modules.schedule.sgu_client.get_weekly_schedule",
            new_callable=AsyncMock,
            return_value=weekly,
        ),
    ):
        res = await tool_get_registered_courses()

    assert res["tong_so_mon"] == 2
    by_code = {c["ma_mon"]: c for c in res["danh_sach_mon_dang_ky"]}
    assert len(by_code["A1"]["cac_buoi_hoc"]) == 1
    assert by_code["A1"]["cac_buoi_hoc"][0]["thu_chu"] == "Chủ Nhật"
    assert by_code["A1"]["trang_thai"] == "Đã đăng ký (Chính thức)"
    assert by_code["B1"]["cac_buoi_hoc"][0]["co_so"].startswith("Trường Phổ thông")


@pytest.mark.asyncio
async def test_tool_get_registered_courses_empty_weekly_schedule():
    """Cả hai nguồn đều rỗng -> trả danh sách rỗng."""
    with (
        patch(
            "sgu_mcp.modules.schedule.sgu_client.get_registered_courses",
            new_callable=AsyncMock,
            return_value={"data": {"ds_kqdkmh": []}},
        ),
        patch(
            "sgu_mcp.modules.schedule.sgu_client.get_weekly_schedule",
            new_callable=AsyncMock,
            return_value={"data": {"ds_tuan_tkb": []}},
        ),
    ):
        res = await tool_get_registered_courses()

    assert res == {"tong_so_mon": 0, "danh_sach_mon_dang_ky": []}


@pytest.mark.asyncio
async def test_tool_get_weekly_schedule_from_api():
    """Nhánh chính: đọc ds_tuan_tkb thật từ API và chọn tuần đang diễn ra."""
    today_text = datetime.now(VN_TZ).date().strftime("%d/%m/%Y")
    api_data = {
        "code": 200,
        "data": {
            "loai_thoi_gian": {"NHHK": "20261"},
            "ds_tuan_tkb": [
                {
                    "tuan_hoc_ky": 1,
                    "ngay_bat_dau": "01/01/2020",
                    "ngay_ket_thuc": "07/01/2020",
                    "thong_tin_tuan": "Tuần 1",
                    "ds_thoi_khoa_bieu": [],
                },
                {
                    "tuan_hoc_ky": 9,
                    "ngay_bat_dau": today_text,
                    "ngay_ket_thuc": today_text,
                    "thong_tin_tuan": "Tuần 9",
                    "ds_thoi_khoa_bieu": [
                        {
                            "thu_kieu_so": 3,
                            "tiet_bat_dau": 1,
                            "so_tiet": 3,
                            "ma_phong": "C.A101",
                            "ten_mon": "Môn A",
                            "ma_mon": "A1",
                            "so_tin_chi": 3,
                            "ma_nhom": "01",
                            "ten_giang_vien": "GV A",
                            "ngay_hoc": "2026-11-03T00:00:00",
                        },
                        {
                            "thu_kieu_so": 3,
                            "tiet_bat_dau": 6,
                            "so_tiet": 1,
                            "ma_phong": "C.B202",
                            "ten_mon": "Môn B",
                            "ma_mon": "B1",
                            "so_tin_chi": 2,
                            "ma_nhom": "02",
                            "ten_giang_vien": "GV B",
                            "ngay_hoc": "2026-11-03T00:00:00",
                        },
                        {"thu_kieu_so": 99, "tiet_bat_dau": 1, "so_tiet": 1},
                    ],
                },
            ],
        },
    }

    with patch(
        "sgu_mcp.modules.schedule.sgu_client.get_weekly_schedule",
        new_callable=AsyncMock,
        return_value=api_data,
    ):
        res = await tool_get_weekly_schedule()

    assert res["hoc_ky"] == "20261"
    assert res["tuan_dang_xem"] == 9
    assert res["tuan_hien_tai"] == 9
    assert res["tong_so_tuan"] == 2
    thu_ba = next(d for d in res["thoi_khoa_bieu_tuan"] if d["thu"] == "Thứ Ba")
    assert [c["tiet"] for c in thu_ba["cac_mon"]] == ["tiết 1->3", "tiết 6"]


@pytest.mark.asyncio
async def test_tool_get_weekly_schedule_invalid_dates_and_week_selector():
    """Ngày tuần không hợp lệ, chọn tuần theo số và fallback học kỳ."""
    api_data = {
        "code": 200,
        "data": {
            "ds_tuan_tkb": [
                {
                    "tuan_hoc_ky": 1,
                    "ngay_bat_dau": "khong-hop-le",
                    "ngay_ket_thuc": "khong-hop-le",
                    "ds_thoi_khoa_bieu": [],
                },
                {
                    "tuan_hoc_ky": 2,
                    "ngay_bat_dau": "01/01/2020",
                    "ngay_ket_thuc": "07/01/2020",
                    "ds_thoi_khoa_bieu": [],
                },
            ]
        },
    }

    with patch(
        "sgu_mcp.modules.schedule.sgu_client.get_weekly_schedule",
        new_callable=AsyncMock,
        return_value=api_data,
    ):
        res = await tool_get_weekly_schedule(semester_id="20241", week_number=2)
        assert res["hoc_ky"] == "20241"
        assert res["tuan_dang_xem"] == 2

        res_default = await tool_get_weekly_schedule()
        assert res_default["hoc_ky"] == 20261

        res_missing = await tool_get_weekly_schedule(week_number=99)
        assert res_missing["tuan_dang_xem"] == 1


@pytest.mark.asyncio
async def test_tool_get_weekly_schedule_fallback_to_registered_courses():
    """API không có ds_tuan_tkb -> dựng thời khóa biểu từ môn đã đăng ký."""
    courses = {
        "danh_sach_mon_dang_ky": [
            {
                "ten_mon": "Môn C",
                "ma_mon": "C1",
                "so_tc": 3,
                "cac_buoi_hoc": [
                    {
                        "thu_so": 2,
                        "tiet_chu": "tiết 1->2",
                        "tiet_bat_dau": 1,
                        "tiet_ket_thuc": 2,
                        "phong": "A.101",
                        "giang_vien": "GV",
                        "thoi_gian": "2026",
                        "co_so": "Cơ sở chính (273 An Dương Vương, Q.5)",
                    },
                    {
                        "thu_so": 3,
                        "tiet_chu": "tiết 3",
                        "tiet_bat_dau": 3,
                        "tiet_ket_thuc": 3,
                        "phong": "4.S_QP01",
                        "giang_vien": "GV",
                        "thoi_gian": "2026",
                        "co_so": None,
                    },
                    {
                        "thu_so": 99,
                        "tiet_chu": "tiết 9",
                        "tiet_bat_dau": 9,
                        "tiet_ket_thuc": 9,
                        "phong": "",
                        "giang_vien": "",
                        "thoi_gian": "",
                        "co_so": None,
                    },
                ],
            }
        ]
    }

    async def fake_registered():
        return courses

    with (
        patch(
            "sgu_mcp.modules.schedule.sgu_client.get_weekly_schedule",
            new_callable=AsyncMock,
            return_value={"code": 200, "data": {"ds_tuan_tkb": []}},
        ),
        patch("sgu_mcp.modules.schedule.tool_get_registered_courses", fake_registered),
    ):
        res = await tool_get_weekly_schedule()

    thu_hai = next(d for d in res["thoi_khoa_bieu_tuan"] if d["thu"] == "Thứ Hai")
    thu_ba = next(d for d in res["thoi_khoa_bieu_tuan"] if d["thu"] == "Thứ Ba")
    assert len(thu_hai["cac_mon"]) == 1
    assert thu_ba["cac_mon"][0]["co_so"].startswith("Trường Phổ thông")


@pytest.mark.asyncio
async def test_tool_get_weekly_schedule_datetime_failure():
    """datetime.now(VN_TZ) lỗi -> dùng giờ hệ thống để xác định tuần hiện tại."""
    today_text = datetime.now(VN_TZ).date().strftime("%d/%m/%Y")
    api_data = {
        "code": 200,
        "data": {
            "ds_tuan_tkb": [
                {
                    "tuan_hoc_ky": 9,
                    "ngay_bat_dau": today_text,
                    "ngay_ket_thuc": today_text,
                    "ds_thoi_khoa_bieu": [],
                }
            ]
        },
    }

    class FlakyDatetime(datetime):
        calls = 0

        @classmethod
        def now(cls, tz=None):
            cls.calls += 1
            if cls.calls == 1:
                raise RuntimeError("tz unavailable")
            return datetime.now(tz)

    with (
        patch("sgu_mcp.modules.schedule.datetime", FlakyDatetime),
        patch(
            "sgu_mcp.modules.schedule.sgu_client.get_weekly_schedule",
            new_callable=AsyncMock,
            return_value=api_data,
        ),
    ):
        res = await tool_get_weekly_schedule()

    assert res["tuan_dang_xem"] == 9
    assert res["tuan_hien_tai"] == 9


@pytest.mark.asyncio
async def test_tool_get_today_schedule_datetime_failure_and_week_label():
    """datetime lỗi múi giờ -> fallback giờ hệ thống, kèm nhãn tuần học kỳ."""
    weekly = {
        "thoi_khoa_bieu_tuan": [{"thu": "Thứ Ba", "cac_mon": []}],
        "tuan_hien_tai": 9,
    }
    fake_now = MagicMock()
    fake_now.weekday.return_value = 0
    mock_datetime = MagicMock()
    mock_datetime.now.side_effect = [RuntimeError("tz unavailable"), fake_now]

    with (
        patch("sgu_mcp.modules.schedule.datetime", mock_datetime),
        patch(
            "sgu_mcp.modules.schedule.tool_get_weekly_schedule",
            new_callable=AsyncMock,
            return_value=weekly,
        ),
    ):
        res = await tool_get_today_schedule()

    assert res["hom_nay"] == "Thứ Hai"
    assert res["tuan_hoc_ky"] == 9
    assert res["lich_ngay_mai"]["ngay_mai"] == "Thứ Ba"
