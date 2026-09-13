"""
Kiểm thử kết nối trực tiếp client MCP vào SGU Academic MCP Server qua Stdio
"""

import asyncio
import sys

# Đảm bảo UTF-8 cho Windows console
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run_mcp_client():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "sgu_mcp.server", "--transport", "stdio"],
        cwd="D:/CCNLTHD",
        env={"PYTHONIOENCODING": "utf-8"}
    )

    print("Đang khởi động kết nối MCP Client tới SGU Academic Server...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 1. Liệt kê toàn bộ Tools
            tools = await session.list_tools()
            print(f"\n✅ KẾT NỐI THÀNH CÔNG! Số lượng Tools: {len(tools.tools)}")
            for idx, t in enumerate(tools.tools[:5], 1):
                print(f"   [{idx}] Tool: {t.name} -> {t.description}")
            print(f"   ... và {len(tools.tools) - 5} công cụ khác.")

            # 2. Gọi Tool: check_prerequisites
            print("\n" + "=" * 50)
            print("🚀 THỬ NGHIỆM GỌI TOOL: check_prerequisites")
            print("=" * 50)
            res1 = await session.call_tool("check_prerequisites", {"course_name": "Lập trình mạng"})
            for c in res1.content:
                print("Kết quả trả về cho AI:")
                print(c.text)

            # 3. Gọi Tool: simulate_target_gpa
            print("\n" + "=" * 50)
            print("🚀 THỬ NGHIỆM GỌI TOOL: simulate_target_gpa")
            print("=" * 50)
            res2 = await session.call_tool("simulate_target_gpa", {
                "current_gpa": 3.1,
                "current_credits": 80,
                "target_gpa": 3.2,
                "remaining_credits": 40
            })
            for c in res2.content:
                print("Kết quả trả về cho AI:")
                print(c.text)

            # 4. Đọc Resource: sgu://graduation/standards
            print("\n" + "=" * 50)
            print("📖 THỬ NGHIỆM ĐỌC RESOURCE: sgu://graduation/standards")
            print("=" * 50)
            res_content = await session.read_resource("sgu://graduation/standards")
            for c in res_content.contents:
                print(c.text[:250] + "\n...")

            # 5. Đọc Prompt: graduation_audit
            print("\n" + "=" * 50)
            print("💬 THỬ NGHIỆM ĐỌC PROMPT: graduation_audit")
            print("=" * 50)
            prompt_res = await session.get_prompt("graduation_audit")
            for msg in prompt_res.messages:
                print("Template Prompt gửi vào Context của AI:")
                print(msg.content.text[:200] + "\n...")


if __name__ == "__main__":
    asyncio.run(run_mcp_client())
