"""
Unit tests cho toàn bộ MCP Server: Tools, Resources, Prompts
Kiểm tra khả năng tương thích với giao thức Model Context Protocol
"""

import pytest
from sgu_mcp.server import create_server


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
        "check_prerequisites"
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
        "sgu://campuses/directory"
    ]

    for expected_uri in expected_resources:
        assert expected_uri in resource_uris, f"Resource '{expected_uri}' chưa được đăng ký!"

    # Kiểm tra đọc nội dung của một resource
    curriculum_content = await server.read_resource("sgu://curriculum/it-roadmap")
    assert curriculum_content is not None


@pytest.mark.asyncio
async def test_server_prompts_registration():
    server = create_server()
    prompts = await server.list_prompts()
    prompt_names = [p.name for p in prompts]

    expected_prompts = [
        "plan_weekly_routine",
        "exam_cramming_strategy",
        "graduation_audit"
    ]

    for expected in expected_prompts:
        assert expected in prompt_names, f"Prompt '{expected}' chưa được đăng ký!"


@pytest.mark.asyncio
async def test_call_prerequisites_tool_via_server():
    server = create_server()
    result = await server.call_tool("check_prerequisites", {"course_name": "Lập trình mạng"})
    assert result is not None
