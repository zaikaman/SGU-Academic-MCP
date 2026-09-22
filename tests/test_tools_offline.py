"""
Unit tests cho logic xử lý của các MCP Tools (GPA Simulation, Prerequisites, Conflict check)
"""

import pytest

from sgu_mcp.modules.academic import tool_simulate_target_gpa
from sgu_mcp.modules.tuition import tool_check_prerequisites


@pytest.mark.asyncio
async def test_simulate_target_gpa_achievable():
    # Hiện tại GPA 3.0 (60 tín chỉ), muốn đạt GPA 3.2 (còn 30 tín chỉ)
    res = await tool_simulate_target_gpa(
        current_gpa=3.0, current_credits=60, target_gpa=3.2, remaining_credits=30
    )
    assert res["co_kha_thi_khong"] is True
    # (3.2 * 90 - 3.0 * 60) / 30 = (288 - 180) / 30 = 108 / 30 = 3.6
    assert res["diem_he_4_trung_binh_can_dat"] == 3.6
    assert res["xep_loai_muc_tieu"] == "Giỏi"


@pytest.mark.asyncio
async def test_simulate_target_gpa_impossible():
    # Hiện tại GPA 2.0 (100 tín chỉ), muốn đạt GPA 3.8 (còn 10 tín chỉ)
    res = await tool_simulate_target_gpa(
        current_gpa=2.0, current_credits=100, target_gpa=3.8, remaining_credits=10
    )
    assert res["co_kha_thi_khong"] is False
    assert res["diem_he_4_trung_binh_can_dat"] > 4.0


@pytest.mark.asyncio
async def test_check_prerequisites():
    # Môn Lập trình mạng cần Mạng máy tính
    res = await tool_check_prerequisites("Lập trình mạng")
    assert "Mạng máy tính" in res["mon_tien_quyet"]

    # Môn Công nghệ phần mềm cần Lập trình hướng đối tượng và Cơ sở dữ liệu
    res2 = await tool_check_prerequisites("Công nghệ phần mềm")
    assert "Lập trình hướng đối tượng" in res2["mon_tien_quyet"]
    assert "Cơ sở dữ liệu" in res2["mon_tien_quyet"]

    # Môn không có môn tiên quyết
    res3 = await tool_check_prerequisites("Môn Thể dục")
    assert len(res3["mon_tien_quyet"]) == 0
