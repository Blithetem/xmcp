#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel测试用例管理MCP服务
用于读取、写入、修改测试用例XLSX文件
"""

import asyncio
import logging
import sys
import os
from typing import Any, Sequence
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

from testcase_excel_manager import TestCaseExcelManager, TestCaseExcelCreator

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("excel-mcp-server")

# 创建服务器实例
server = Server("excel-testcase-manager")

async def read_excel_file(file_path: str) -> dict:
    """
    读取Excel文件
    
    Args:
        file_path: Excel文件路径
    
    Returns:
        读取结果
    """
    try:
        manager = TestCaseExcelManager(file_path)
        manager.open()
        
        testcases = manager.read_testcases()
        manager.close()
        
        return {
            "file_path": file_path,
            "testcases": testcases,
            "count": len(testcases),
            "message": "读取成功"
        }
    except Exception as e:
        logger.error(f"读取Excel文件时发生错误: {str(e)}")
        return {
            "file_path": file_path,
            "testcases": [],
            "count": 0,
            "message": f"读取Excel文件时发生错误: {str(e)}"
        }

async def write_excel_file(testcases: list[dict], output_path: str) -> dict:
    """
    写入Excel文件
    
    Args:
        testcases: 测试用例列表
        output_path: 输出文件路径
    
    Returns:
        写入结果
    """
    try:
        creator = TestCaseExcelCreator()
        success = creator.create_new_file(testcases, output_path)
        
        if success:
            return {
                "output_path": output_path,
                "count": len(testcases),
                "message": "写入成功"
            }
        else:
            return {
                "output_path": output_path,
                "count": 0,
                "message": "写入失败"
            }
    except Exception as e:
        logger.error(f"写入Excel文件时发生错误: {str(e)}")
        return {
            "output_path": output_path,
            "count": 0,
            "message": f"写入Excel文件时发生错误: {str(e)}"
        }

async def update_excel_file(file_path: str, row: int, testcase: dict) -> dict:
    """
    更新Excel文件中的测试用例
    
    Args:
        file_path: Excel文件路径
        row: 行号（从2开始）
        testcase: 测试用例数据
    
    Returns:
        更新结果
    """
    try:
        manager = TestCaseExcelManager(file_path)
        manager.open()
        manager.update_testcase(row, testcase)
        manager.save()
        manager.close()
        
        return {
            "file_path": file_path,
            "row": row,
            "testcase": testcase,
            "message": "更新成功"
        }
    except Exception as e:
        logger.error(f"更新Excel文件时发生错误: {str(e)}")
        return {
            "file_path": file_path,
            "row": row,
            "testcase": testcase,
            "message": f"更新Excel文件时发生错误: {str(e)}"
        }

async def add_excel_testcase(file_path: str, testcase: dict) -> dict:
    """
    向Excel文件添加测试用例
    
    Args:
        file_path: Excel文件路径
        testcase: 测试用例数据
    
    Returns:
        添加结果
    """
    try:
        manager = TestCaseExcelManager(file_path)
        manager.open()
        manager.add_testcase(testcase)
        manager.save()
        manager.close()
        
        return {
            "file_path": file_path,
            "testcase": testcase,
            "message": "添加成功"
        }
    except Exception as e:
        logger.error(f"添加测试用例时发生错误: {str(e)}")
        return {
            "file_path": file_path,
            "testcase": testcase,
            "message": f"添加测试用例时发生错误: {str(e)}"
        }

async def delete_excel_testcase(file_path: str, row: int) -> dict:
    """
    从Excel文件删除测试用例
    
    Args:
        file_path: Excel文件路径
        row: 行号（从2开始）
    
    Returns:
        删除结果
    """
    try:
        manager = TestCaseExcelManager(file_path)
        manager.open()
        manager.delete_testcase(row)
        manager.save()
        manager.close()
        
        return {
            "file_path": file_path,
            "row": row,
            "message": "删除成功"
        }
    except Exception as e:
        logger.error(f"删除测试用例时发生错误: {str(e)}")
        return {
            "file_path": file_path,
            "row": row,
            "message": f"删除测试用例时发生错误: {str(e)}"
        }

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """返回可用工具列表"""
    return [
        Tool(
            name="read_excel",
            description="读取Excel测试用例文件",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Excel文件路径"
                    }
                },
                "required": ["file_path"]
            },
        ),
        Tool(
            name="write_excel",
            description="写入Excel测试用例文件",
            inputSchema={
                "type": "object",
                "properties": {
                    "testcases": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "用例名称": {
                                    "type": "string"
                                },
                                "前置条件": {
                                    "type": "string"
                                },
                                "所属模块": {
                                    "type": "string"
                                },
                                "步骤描述": {
                                    "type": "string"
                                },
                                "预期结果": {
                                    "type": "string"
                                },
                                "备注": {
                                    "type": "string"
                                },
                                "用例等级": {
                                    "type": "string"
                                },
                                "编辑模式": {
                                    "type": "string"
                                }
                            },
                            "required": ["用例名称", "所属模块", "步骤描述", "预期结果", "用例等级"]
                        }
                    },
                    "output_path": {
                        "type": "string",
                        "description": "输出Excel文件路径"
                    }
                },
                "required": ["testcases", "output_path"]
            },
        ),
        Tool(
            name="update_excel",
            description="更新Excel测试用例文件中的测试用例",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Excel文件路径"
                    },
                    "row": {
                        "type": "integer",
                        "description": "行号（从2开始，第1行是表头）"
                    },
                    "testcase": {
                        "type": "object",
                        "properties": {
                            "用例名称": {
                                "type": "string"
                            },
                            "前置条件": {
                                "type": "string"
                            },
                            "所属模块": {
                                "type": "string"
                            },
                            "步骤描述": {
                                "type": "string"
                            },
                            "预期结果": {
                                "type": "string"
                            },
                            "备注": {
                                "type": "string"
                            },
                            "用例等级": {
                                "type": "string"
                            },
                            "编辑模式": {
                                "type": "string"
                            }
                        },
                        "required": ["用例名称", "所属模块", "步骤描述", "预期结果", "用例等级"]
                    }
                },
                "required": ["file_path", "row", "testcase"]
            },
        ),
        Tool(
            name="add_excel_testcase",
            description="向Excel测试用例文件添加新的测试用例",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Excel文件路径"
                    },
                    "testcase": {
                        "type": "object",
                        "properties": {
                            "用例名称": {
                                "type": "string"
                            },
                            "前置条件": {
                                "type": "string"
                            },
                            "所属模块": {
                                "type": "string"
                            },
                            "步骤描述": {
                                "type": "string"
                            },
                            "预期结果": {
                                "type": "string"
                            },
                            "备注": {
                                "type": "string"
                            },
                            "用例等级": {
                                "type": "string"
                            },
                            "编辑模式": {
                                "type": "string"
                            }
                        },
                        "required": ["用例名称", "所属模块", "步骤描述", "预期结果", "用例等级"]
                    }
                },
                "required": ["file_path", "testcase"]
            },
        ),
        Tool(
            name="delete_excel_testcase",
            description="从Excel测试用例文件删除测试用例",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Excel文件路径"
                    },
                    "row": {
                        "type": "integer",
                        "description": "行号（从2开始，第1行是表头）"
                    }
                },
                "required": ["file_path", "row"]
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
    """处理工具调用"""
    if name == "read_excel":
        if not arguments or "file_path" not in arguments:
            return [TextContent(type="text", text=str({"error": "缺少 file_path 参数"}))]
        file_path = arguments["file_path"]
        result = await read_excel_file(file_path)
        return [TextContent(type="text", text=str(result))]
    elif name == "write_excel":
        if not arguments or "testcases" not in arguments or "output_path" not in arguments:
            return [TextContent(type="text", text=str({"error": "缺少 testcases 或 output_path 参数"}))]
        testcases = arguments["testcases"]
        output_path = arguments["output_path"]
        result = await write_excel_file(testcases, output_path)
        return [TextContent(type="text", text=str(result))]
    elif name == "update_excel":
        if not arguments or "file_path" not in arguments or "row" not in arguments or "testcase" not in arguments:
            return [TextContent(type="text", text=str({"error": "缺少 file_path、row 或 testcase 参数"}))]
        file_path = arguments["file_path"]
        row = arguments["row"]
        testcase = arguments["testcase"]
        result = await update_excel_file(file_path, row, testcase)
        return [TextContent(type="text", text=str(result))]
    elif name == "add_excel_testcase":
        if not arguments or "file_path" not in arguments or "testcase" not in arguments:
            return [TextContent(type="text", text=str({"error": "缺少 file_path 或 testcase 参数"}))]
        file_path = arguments["file_path"]
        testcase = arguments["testcase"]
        result = await add_excel_testcase(file_path, testcase)
        return [TextContent(type="text", text=str(result))]
    elif name == "delete_excel_testcase":
        if not arguments or "file_path" not in arguments or "row" not in arguments:
            return [TextContent(type="text", text=str({"error": "缺少 file_path 或 row 参数"}))]
        file_path = arguments["file_path"]
        row = arguments["row"]
        result = await delete_excel_testcase(file_path, row)
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