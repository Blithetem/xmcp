#!/usr/bin/env python3
import asyncio
import logging
import os
import subprocess
from typing import Any, Sequence

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cli-server")

# 创建服务器实例
server = Server("cli")

# PowerShell路径配置
POWERSHELL_7_PATH = "C:\\Program Files\\PowerShell\\7\\pwsh.exe"
DEFAULT_POWERSHELL_PATH = "powershell.exe"

async def run_command(command: str, timeout: int = 30) -> dict:
    """执行CLI命令
    
    Args:
        command: 要执行的命令字符串
        timeout: 命令执行超时时间（秒）
        
    Returns:
        dict: 命令执行结果
    """
    try:
        # 检测PowerShell 7是否存在
        if os.path.exists(POWERSHELL_7_PATH):
            powershell_path = POWERSHELL_7_PATH
            powershell_version = "PowerShell 7"
        else:
            powershell_path = DEFAULT_POWERSHELL_PATH
            powershell_version = "Windows Default PowerShell"
        
        logger.info(f"使用 {powershell_version} 执行命令: {command}")
        
        # 执行命令
        process = await asyncio.create_subprocess_exec(
            powershell_path,
            "-Command",
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        
        # 等待命令执行完成，设置超时
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            return {
                "stdout": "",
                "stderr": "命令执行超时",
                "returncode": -1,
                "message": "命令执行超时",
                "powershell_version": powershell_version
            }
        
        # 解码输出
        stdout_str = stdout.decode('utf-8', errors='replace').strip()
        stderr_str = stderr.decode('utf-8', errors='replace').strip()
        
        return {
            "stdout": stdout_str,
            "stderr": stderr_str,
            "returncode": process.returncode,
            "message": "命令执行成功" if process.returncode == 0 else "命令执行失败",
            "powershell_version": powershell_version
        }
    except Exception as e:
        logger.error(f"执行命令时发生错误: {str(e)}")
        return {
            "stdout": "",
            "stderr": str(e),
            "returncode": -1,
            "message": f"执行命令时发生错误: {str(e)}",
            "powershell_version": "未知"
        }

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """返回可用工具列表"""
    return [
        Tool(
            name="execute_system_command",
            description="执行系统命令，适用于需要在命令行中运行的各种操作，如文件管理、进程管理、网络操作等。默认使用PowerShell 7，如不存在则使用Windows默认PowerShell。",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "要执行的系统命令字符串，例如：dir（查看目录）、Get-Process（查看进程）、ping localhost（测试网络连接）等"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "命令执行超时时间（秒），默认30秒，超过此时间命令将被强制终止"
                    }
                },
                "required": ["command"]
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
    """处理工具调用"""
    if name == "execute_system_command":
        if not arguments or "command" not in arguments:
            return [TextContent(type="text", text=str({"error": "缺少 command 参数"}))]
        command = arguments["command"]
        timeout = arguments.get("timeout", 30)
        result = await run_command(command, timeout)
        return [TextContent(type="text", text=str(result))]
    else:
        raise ValueError(f"未知工具: {name}")

async def main():
    """主函数"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
