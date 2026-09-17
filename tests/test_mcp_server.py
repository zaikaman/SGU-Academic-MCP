"""
Unit tests cho toàn bộ MCP Server: Tools, Resources, Prompts & CLI main
Kiểm tra khả năng tương thích với giao thức Model Context Protocol và đạt 100% coverage
"""

import runpy
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from sgu_mcp.server import create_server, main


@pytest.mark.asyncio
async def test_server_tools_registration():
    server = create_server()
    tools = await server.list_tools()
    tool_names = [t.name for t in tools]

    expected_tools = [
        "sgu_login",
        "get_registered_courses",
        "get_weekly_schedule",
        "get_today_schedule",
        "check_schedule_conflict",
        "get_exam_schedule",
        "get_exam_countdown",
        "get_student_profile",
        "get_semester_grades",
        "calculate_gpa_summary",
        "simulate_target_gpa",
        "get_tuition_fees",
        "get_sgu_notifications",
        "get_course_offerings",
        "check_prerequisites",
    ]

    for expected in expected_tools:
        assert expected in tool_names, f"Tool '{expected}' chưa được đăng ký trong MCP Server!"

    assert len(tools) >= 15


@pytest.mark.asyncio
async def test_server_resources_registration():
    server = create_server()
    resources = await server.list_resources()
    resource_uris = [str(r.uri) for r in resources]

    expected_resources = [
        "sgu://curriculum/it-roadmap",
        "sgu://regulations/academic-warning",
        "sgu://graduation/standards",
        "sgu://campuses/directory",
    ]

    for expected_uri in expected_resources:
        assert expected_uri in resource_uris, f"Resource '{expected_uri}' chưa được đăng ký!"

    # Đọc nội dung cả 4 resources để đảm bảo 100% callbacks được gọi
    for uri in expected_resources:
        content = await server.read_resource(uri)
        assert content is not None
        assert len(str(content)) > 0


@pytest.mark.asyncio
async def test_server_prompts_registration():
    server = create_server()
    prompts = await server.list_prompts()
    prompt_names = [p.name for p in prompts]

    expected_prompts = ["plan_weekly_routine", "exam_cramming_strategy", "graduation_audit"]

    for expected in expected_prompts:
        assert expected in prompt_names, f"Prompt '{expected}' chưa được đăng ký!"

    # Gọi prompt plan_weekly_routine có và không có target_hours_per_day
    p1_with_arg = await server.get_prompt("plan_weekly_routine", {"target_hours_per_day": "3"})
    assert p1_with_arg is not None

    p1_no_arg = await server.get_prompt("plan_weekly_routine", {})
    assert p1_no_arg is not None

    # Gọi prompt exam_cramming_strategy có và không có priority_courses
    p2_with_arg = await server.get_prompt(
        "exam_cramming_strategy", {"priority_courses": "Web, CSDL"}
    )
    assert p2_with_arg is not None

    p2_no_arg = await server.get_prompt("exam_cramming_strategy", {})
    assert p2_no_arg is not None

    # Gọi prompt graduation_audit
    p3 = await server.get_prompt("graduation_audit", {})
    assert p3 is not None


@pytest.mark.asyncio
async def test_call_all_tools_via_server():
    server = create_server()

    # Patches cho tất cả tool modules
    with (
        patch("sgu_mcp.server.tool_sgu_login", new_callable=AsyncMock) as m_login,
        patch("sgu_mcp.server.tool_get_registered_courses", new_callable=AsyncMock) as m_reg,
        patch("sgu_mcp.server.tool_get_weekly_schedule", new_callable=AsyncMock) as m_week,
        patch("sgu_mcp.server.tool_get_today_schedule", new_callable=AsyncMock) as m_today,
        patch("sgu_mcp.server.tool_check_schedule_conflict", new_callable=AsyncMock) as m_conf,
        patch("sgu_mcp.server.tool_get_exam_schedule", new_callable=AsyncMock) as m_exam,
        patch("sgu_mcp.server.tool_get_exam_countdown", new_callable=AsyncMock) as m_cnt,
        patch("sgu_mcp.server.tool_get_student_profile", new_callable=AsyncMock) as m_prof,
        patch("sgu_mcp.server.tool_get_semester_grades", new_callable=AsyncMock) as m_grd,
        patch("sgu_mcp.server.tool_calculate_gpa_summary", new_callable=AsyncMock) as m_gpa,
        patch("sgu_mcp.server.tool_simulate_target_gpa", new_callable=AsyncMock) as m_sim,
        patch("sgu_mcp.server.tool_get_tuition_fees", new_callable=AsyncMock) as m_tui,
        patch("sgu_mcp.server.tool_get_sgu_notifications", new_callable=AsyncMock) as m_not,
        patch("sgu_mcp.server.tool_get_course_offerings", new_callable=AsyncMock) as m_cat,
        patch("sgu_mcp.server.tool_check_prerequisites", new_callable=AsyncMock) as m_pre,
    ):
        m_login.return_value = {"success": True}
        m_reg.return_value = {"courses": []}
        m_week.return_value = {"schedule": []}
        m_today.return_value = {"today": []}
        m_conf.return_value = {"conflict": False}
        m_exam.return_value = {"exams": []}
        m_cnt.return_value = {"countdown": []}
        m_prof.return_value = {"profile": {}}
        m_grd.return_value = {"grades": []}
        m_gpa.return_value = {"gpa": 3.5}
        m_sim.return_value = {"achievable": True}
        m_tui.return_value = {"tuition": 0}
        m_not.return_value = {"notifications": []}
        m_cat.return_value = {"catalog": []}
        m_pre.return_value = {"prerequisites": []}

        # Call each tool
        await server.call_tool("sgu_login", {"student_id": "3122410001", "password": "pwd"})
        m_login.assert_called_once_with(student_id="3122410001", password="pwd")

        await server.call_tool("get_registered_courses", {})
        m_reg.assert_called_once()

        await server.call_tool("get_weekly_schedule", {"semester_id": "20241"})
        m_week.assert_called_once_with(semester_id="20241")

        await server.call_tool("get_today_schedule", {})
        m_today.assert_called_once()

        await server.call_tool(
            "check_schedule_conflict", {"target_thu": 2, "target_tiet_bd": 1, "target_so_tiet": 3}
        )
        m_conf.assert_called_once_with(target_thu=2, target_tiet_bd=1, target_so_tiet=3)

        await server.call_tool("get_exam_schedule", {"semester_id": "20241"})
        m_exam.assert_called_once_with(semester_id="20241")

        await server.call_tool("get_exam_countdown", {"semester_id": "20241"})
        m_cnt.assert_called_once_with(semester_id="20241")

        await server.call_tool("get_student_profile", {})
        m_prof.assert_called_once()

        await server.call_tool("get_semester_grades", {"semester_id": "20241"})
        m_grd.assert_called_once_with(semester_id="20241")

        await server.call_tool("calculate_gpa_summary", {"semester_id": "20241"})
        m_gpa.assert_called_once_with(semester_id="20241")

        await server.call_tool(
            "simulate_target_gpa",
            {"current_gpa": 3.2, "current_credits": 90, "target_gpa": 3.6, "remaining_credits": 30},
        )
        m_sim.assert_called_once_with(
            current_gpa=3.2, current_credits=90, target_gpa=3.6, remaining_credits=30
        )

        await server.call_tool("get_tuition_fees", {})
        m_tui.assert_called_once()

        await server.call_tool("get_sgu_notifications", {"limit": 5})
        m_not.assert_called_once_with(limit=5)

        await server.call_tool("get_course_offerings", {"page": 2, "limit": 15})
        m_cat.assert_called_once_with(page=2, limit=15)

        await server.call_tool("check_prerequisites", {"course_name": "Lập trình mạng"})
        m_pre.assert_called_once_with(course_name="Lập trình mạng")


def test_main_stdio(monkeypatch):
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(sys, "argv", ["server.py", "--transport", "stdio"])
    mock_stdin = MagicMock()
    mock_stdout = MagicMock()
    monkeypatch.setattr(sys, "stdin", mock_stdin)
    monkeypatch.setattr(sys, "stdout", mock_stdout)

    def fake_run(coro):
        coro.close()

    with patch("asyncio.run", side_effect=fake_run) as mock_run:
        main()
        assert mock_run.called
        mock_stdin.reconfigure.assert_called_with(encoding="utf-8")
        mock_stdout.reconfigure.assert_called_with(encoding="utf-8")


def test_main_sse(monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["server.py", "--transport", "sse", "--host", "0.0.0.0", "--port", "9999"]
    )

    def fake_run(coro):
        coro.close()

    with patch("asyncio.run", side_effect=fake_run) as mock_run:
        main()
        assert mock_run.called


def test_main_win32_reconfigure_exception(monkeypatch):
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(sys, "argv", ["server.py", "--transport", "stdio"])

    mock_stdin = MagicMock()
    mock_stdin.reconfigure.side_effect = RuntimeError("Cannot reconfigure")
    monkeypatch.setattr(sys, "stdin", mock_stdin)

    def fake_run(coro):
        coro.close()

    with patch("asyncio.run", side_effect=fake_run) as mock_run:
        main()
        assert mock_run.called


def test_main_win32_no_stdout_reconfigure(monkeypatch):
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(sys, "argv", ["server.py", "--transport", "stdio"])

    mock_stdin = MagicMock()
    mock_stdin.reconfigure = MagicMock()
    monkeypatch.setattr(sys, "stdin", mock_stdin)

    class DummyStdout:
        pass

    monkeypatch.setattr(sys, "stdout", DummyStdout())

    def fake_run(coro):
        coro.close()

    with patch("asyncio.run", side_effect=fake_run) as mock_run:
        main()
        assert mock_run.called


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_dunder_main(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["server.py", "--transport", "stdio"])

    def fake_run(coro):
        coro.close()

    with patch("asyncio.run", side_effect=fake_run) as mock_run:
        runpy.run_module("sgu_mcp.server", run_name="__main__")
        assert mock_run.called


def test_server_health_route():
    from starlette.testclient import TestClient

    server = create_server()
    app = server.sse_app(sse_path="/sse", message_path="/messages/", host="127.0.0.1")
    client = TestClient(app, base_url="http://127.0.0.1:8000")
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["server"] == "sgu_academic_server"


def test_main_non_win32(monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(sys, "argv", ["server.py", "--transport", "stdio"])

    def fake_run(coro):
        coro.close()

    with patch("asyncio.run", side_effect=fake_run) as mock_run:
        main()
        assert mock_run.called
