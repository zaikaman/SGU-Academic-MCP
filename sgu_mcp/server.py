"""
Entrypoint SGU Academic MCP Server
Hiện thực theo chuẩn Model Context Protocol SDK 2.x
Hỗ trợ chạy stdio (cho Claude Desktop, Cursor) và SSE (cho Web Client, Microservices)
"""

import argparse
import asyncio
import sys
from typing import Any, Optional
from mcp.server.mcpserver import MCPServer
from sgu_mcp.config import settings
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
from sgu_mcp.prompts.templates import SGU_PROMPTS
from sgu_mcp.resources.content import SGU_RESOURCES


def create_server() -> MCPServer:
    """Khởi tạo và cấu hình MCP Server"""
    server = MCPServer(
        name="sgu_academic_server",
        version="1.0.0",
        description="SGU Academic MCP Server - Cầu nối thông tin đào tạo trường Đại học Sài Gòn cho Trợ lý AI"
    )

    # ==================== ĐĂNG KÝ 15 MCP TOOLS ====================

    @server.tool(name="sgu_login", description="Đăng nhập tài khoản sinh viên vào cổng thông tin đào tạo SGU")
    async def sgu_login(student_id: str, password: str) -> dict[str, Any]:
        return await tool_sgu_login(student_id=student_id, password=password)

    @server.tool(name="get_registered_courses", description="Lấy danh sách môn học đã đăng ký trong học kỳ hiện tại của sinh viên SGU")
    async def get_registered_courses() -> dict[str, Any]:
        return await tool_get_registered_courses()

    @server.tool(name="get_weekly_schedule", description="Lấy thời khóa biểu học kỳ chi tiết theo tuần của sinh viên SGU")
    async def get_weekly_schedule(semester_id: Optional[str] = None) -> dict[str, Any]:
        return await tool_get_weekly_schedule(semester_id=semester_id)

    @server.tool(name="get_today_schedule", description="Tra cứu nhanh lịch học hôm nay của sinh viên (phòng học, ca học, giảng viên)")
    async def get_today_schedule() -> dict[str, Any]:
        return await tool_get_today_schedule()

    @server.tool(name="check_schedule_conflict", description="Kiểm tra trùng lịch học khi định đăng ký thêm môn học mới")
    async def check_schedule_conflict(target_thu: int, target_tiet_bd: int, target_so_tiet: int) -> dict[str, Any]:
        return await tool_check_schedule_conflict(
            target_thu=target_thu,
            target_tiet_bd=target_tiet_bd,
            target_so_tiet=target_so_tiet
        )

    @server.tool(name="get_exam_schedule", description="Tra cứu lịch thi học kỳ chính thức từ SGU (ngày thi, phòng thi, ca thi, SBD)")
    async def get_exam_schedule(semester_id: Optional[str] = None) -> dict[str, Any]:
        return await tool_get_exam_schedule(semester_id=semester_id)

    @server.tool(name="get_exam_countdown", description="Đếm ngược số ngày đến từng môn thi và cảnh báo lịch thi dồn dập")
    async def get_exam_countdown(semester_id: Optional[str] = None) -> dict[str, Any]:
        return await tool_get_exam_countdown(semester_id=semester_id)

    @server.tool(name="get_student_profile", description="Lấy hồ sơ sinh viên chính thức từ SGU (họ tên, lớp, ngành, CVHT)")
    async def get_student_profile() -> dict[str, Any]:
        return await tool_get_student_profile()

    @server.tool(name="get_semester_grades", description="Lấy bảng điểm học tập chi tiết của từng học kỳ từ hệ thống SGU")
    async def get_semester_grades(semester_id: Optional[str] = None) -> dict[str, Any]:
        return await tool_get_semester_grades(semester_id=semester_id)

    @server.tool(name="calculate_gpa_summary", description="Tổng hợp điểm GPA tích lũy, số tín chỉ đạt và các môn còn nợ")
    async def calculate_gpa_summary(semester_id: Optional[str] = None) -> dict[str, Any]:
        return await tool_calculate_gpa_summary(semester_id=semester_id)

    @server.tool(name="simulate_target_gpa", description="Thuật toán mô phỏng điểm số cần đạt ở các môn còn lại để đạt bằng Giỏi/Khá")
    async def simulate_target_gpa(current_gpa: float, current_credits: int, target_gpa: float, remaining_credits: int) -> dict[str, Any]:
        return await tool_simulate_target_gpa(
            current_gpa=current_gpa,
            current_credits=current_credits,
            target_gpa=target_gpa,
            remaining_credits=remaining_credits
        )

    @server.tool(name="get_tuition_fees", description="Tra cứu học phí từng kỳ, số tiền đã nộp và số tiền còn nợ của sinh viên SGU")
    async def get_tuition_fees() -> dict[str, Any]:
        return await tool_get_tuition_fees()

    @server.tool(name="get_sgu_notifications", description="Lấy thông báo mới nhất từ Ban Giám hiệu và Phòng Đào tạo SGU")
    async def get_sgu_notifications(limit: int = 10) -> dict[str, Any]:
        return await tool_get_sgu_notifications(limit=limit)

    @server.tool(name="get_course_offerings", description="Tra cứu danh mục các lớp học phần đang mở kèm số lượng slot còn lại")
    async def get_course_offerings(page: int = 1, limit: int = 20) -> dict[str, Any]:
        return await tool_get_course_offerings(page=page, limit=limit)

    @server.tool(name="check_prerequisites", description="Kiểm tra điều kiện môn học tiên quyết ngành CNTT trường Đại học Sài Gòn")
    async def check_prerequisites(course_name: str) -> dict[str, Any]:
        return await tool_check_prerequisites(course_name=course_name)

    # ==================== ĐĂNG KÝ 4 MCP RESOURCES ====================

    @server.resource(uri="sgu://curriculum/it-roadmap", name="Chương trình đào tạo Kỹ sư CNTT SGU", mime_type="application/json")
    def resource_curriculum() -> str:
        return SGU_RESOURCES["sgu://curriculum/it-roadmap"]["content"]

    @server.resource(uri="sgu://regulations/academic-warning", name="Quy chế cảnh báo học vụ SGU", mime_type="text/plain")
    def resource_warning() -> str:
        return SGU_RESOURCES["sgu://regulations/academic-warning"]["content"]

    @server.resource(uri="sgu://graduation/standards", name="Chuẩn đầu ra tốt nghiệp SGU", mime_type="text/plain")
    def resource_graduation() -> str:
        return SGU_RESOURCES["sgu://graduation/standards"]["content"]

    @server.resource(uri="sgu://campuses/directory", name="Danh bạ các cơ sở SGU", mime_type="text/plain")
    def resource_campuses() -> str:
        return SGU_RESOURCES["sgu://campuses/directory"]["content"]

    # ==================== ĐĂNG KÝ 3 MCP PROMPTS ====================

    @server.prompt(name="plan_weekly_routine", description="Lập kế hoạch phân bổ thời gian tự học theo thời khóa biểu tuần")
    def prompt_weekly_routine(target_hours_per_day: Optional[str] = None) -> str:
        extra = f"\nMục tiêu tự học mỗi ngày: {target_hours_per_day} giờ." if target_hours_per_day else ""
        return SGU_PROMPTS["plan_weekly_routine"]["template"] + extra

    @server.prompt(name="exam_cramming_strategy", description="Chiến lược ôn thi nước rút theo lịch thi thực tế")
    def prompt_exam_strategy(priority_courses: Optional[str] = None) -> str:
        extra = f"\nƯu tiên các môn: {priority_courses}." if priority_courses else ""
        return SGU_PROMPTS["exam_cramming_strategy"]["template"] + extra

    @server.prompt(name="graduation_audit", description="Đối soát toàn diện điều kiện tốt nghiệp")
    def prompt_graduation_audit() -> str:
        return SGU_PROMPTS["graduation_audit"]["template"]

    return server


def main():
    if sys.platform == "win32":
        try:
            sys.stdin.reconfigure(encoding="utf-8")
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="SGU Academic MCP Server")
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio", help="Giao thức truyền tải (stdio hoặc sse)")
    parser.add_argument("--host", default=settings.mcp_host, help="Host cho chế độ SSE")
    parser.add_argument("--port", type=int, default=settings.mcp_port, help="Port cho chế độ SSE")
    args = parser.parse_args()

    server = create_server()

    if args.transport == "stdio":
        asyncio.run(server.run_stdio_async())
    else:
        asyncio.run(server.run_sse_async(host=args.host, port=args.port))


if __name__ == "__main__":
    main()
