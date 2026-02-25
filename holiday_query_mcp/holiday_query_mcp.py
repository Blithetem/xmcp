#!/usr/bin/env python3
import asyncio
import logging
import sys
from typing import Any, Sequence
from datetime import datetime, date, timedelta
import requests
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("holiday-query-server")

# 导入工作日查询模块
HAS_API = False
api_is_workday = None
api_get_holiday_data = None
workday_config = None

try:
    import workday
    api_is_workday = workday.is_workday
    api_get_holiday_data = workday.get_holiday_data
    workday_config = workday.config
    HAS_API = True
    logger.info("成功导入workday模块")
except ImportError as e:
    logger.warning(f"无法导入workday模块: {e}")
except AttributeError as e:
    logger.warning(f"workday模块缺少必要的属性: {e}")
except Exception as e:
    logger.warning(f"导入workday模块时发生未知错误: {e}")

# 创建服务器实例
server = Server("holiday-query")

# 基础节假日数据结构
class HolidayData:
    def __init__(self):
        # 法定节假日（包括调休）
        # 格式：{year: {date_str: is_holiday}}
        # is_holiday=True 表示是节假日，is_holiday=False 表示是调休（需要上班）
        self.holidays = {}
        # 初始化2026年数据
        self._init_2026_holidays()
    
    def _init_2026_holidays(self):
        """初始化2026年节假日数据"""
        self.holidays[2026] = {
            # 元旦
            "2026-01-01": True,
            # 春节
            "2026-02-02": True,
            "2026-02-03": True,
            "2026-02-04": True,
            "2026-02-05": True,
            "2026-02-06": True,
            "2026-02-07": True,
            "2026-02-08": True,
            # 春节调休（假设需要上班的日期）
            # "2026-02-01": False,  # 周六调休
            # "2026-02-15": False,  # 周日调休
            "2026-02-28": False,  # 周六调休（春节调休）
            # 清明节
            "2026-04-04": True,
            "2026-04-05": True,
            "2026-04-06": True,
            # 清明节调休
            # "2026-04-05": False,  # 周六调休
            # 劳动节
            "2026-05-01": True,
            "2026-05-02": True,
            "2026-05-03": True,
            "2026-05-04": True,
            "2026-05-05": True,
            # 劳动节调休
            # "2026-04-26": False,  # 周六调休
            # "2026-05-10": False,  # 周日调休
            # 端午节
            "2026-06-20": True,
            "2026-06-21": True,
            "2026-06-22": True,
            # 端午节调休
            # "2026-06-21": False,  # 周六调休
            # 中秋节
            "2026-09-26": True,
            "2026-09-27": True,
            "2026-09-28": True,
            # 中秋节调休
            # "2026-09-27": False,  # 周六调休
            # 国庆节
            "2026-10-01": True,
            "2026-10-02": True,
            "2026-10-03": True,
            "2026-10-04": True,
            "2026-10-05": True,
            "2026-10-06": True,
            "2026-10-07": True,
            # 国庆节调休
            # "2026-09-26": False,  # 周六调休
            # "2026-10-11": False,  # 周日调休
        }
    
    def is_holiday(self, date_obj: date) -> tuple[bool, str]:
        """判断指定日期是否为节假日
        
        Args:
            date_obj: 日期对象
            
        Returns:
            tuple[bool, str]: (是否为节假日, 节假日类型)
        """
        date_str = date_obj.strftime("%Y-%m-%d")
        year = date_obj.year
        
        # 优先使用联网查询
        if HAS_API:
            try:
                # 调用API检查是否为工作日
                is_work_day = api_is_workday(date_obj)
                weekday = date_obj.weekday()
                
                if is_work_day:
                    # 是工作日
                    if weekday in [5, 6]:  # 周六=5, 周日=6
                        return False, "调休（需上班）"
                    return False, "工作日"
                else:
                    # 不是工作日（休息日）
                    if weekday in [5, 6]:  # 周六=5, 周日=6
                        return True, "周末"
                    # 平日但不是工作日，是特殊假期
                    return True, "休息日"
            except Exception as e:
                logger.warning(f"联网查询失败，回退到本地数据: {e}")
        
        # 回退到本地数据
        # 检查是否在法定节假日列表中
        if year in self.holidays and date_str in self.holidays[year]:
            is_holiday = self.holidays[year][date_str]
            if is_holiday:
                return True, "法定节假日"
            else:
                return False, "调休（需上班）"
        
        # 检查是否为周末
        weekday = date_obj.weekday()
        if weekday in [5, 6]:  # 周六=5, 周日=6
            return True, "周末"
        
        # 默认为工作日
        return False, "工作日"
    
    def get_holidays(self, year: int) -> list[str]:
        """获取指定年份的节假日列表
        
        Args:
            year: 年份
            
        Returns:
            list[str]: 节假日日期列表（YYYY-MM-DD格式）
        """
        holidays = []
        
        # 优先使用联网查询
        if HAS_API:
            try:
                # 调用API获取假期数据
                holiday_data = api_get_holiday_data(year, workday_config.open_plat, workday_config.center_url, workday_config.app_id, workday_config.app_secret)
                
                if holiday_data:
                    # 生成全年日期并检查每个日期
                    start_date = date(year, 1, 1)
                    end_date = date(year, 12, 31)
                    current_date = start_date
                    
                    while current_date <= end_date:
                        is_holiday, _ = self.is_holiday(current_date)
                        if is_holiday:
                            holidays.append(current_date.strftime("%Y-%m-%d"))
                        current_date += timedelta(days=1)
                    return holidays
            except Exception as e:
                logger.warning(f"联网获取节假日列表失败，回退到本地数据: {e}")
        
        # 回退到本地数据
        # 生成全年日期
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        current_date = start_date
        
        while current_date <= end_date:
            is_holiday, _ = self.is_holiday(current_date)
            if is_holiday:
                holidays.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)
        
        return holidays

# 创建节假日数据实例
holiday_data = HolidayData()

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """返回可用工具列表"""
    return [
        Tool(
            name="is_holiday",
            description="判断指定日期是否为节假日",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "日期，格式为 YYYY-MM-DD"
                    }
                },
                "required": ["date"]
            },
        ),
        Tool(
            name="get_holidays",
            description="获取指定年份的节假日列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "year": {
                        "type": "integer",
                        "description": "年份"
                    }
                },
                "required": ["year"]
            },
        ),
        Tool(
            name="validate_date_status",
            description="验证日期的工作日/休息日状态是否正确",
            inputSchema={
                "type": "object",
                "properties": {
                    "date_records": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "date": {
                                    "type": "string",
                                    "description": "日期，格式为 YYYY-MM-DD"
                                },
                                "status": {
                                    "type": "boolean",
                                    "description": "状态值，true 表示工作日，false 表示休息日"
                                }
                            },
                            "required": ["date", "status"]
                        }
                    }
                },
                "required": ["date_records"]
            },
        )
    ]

async def is_holiday(date_str: str) -> dict:
    """判断指定日期是否为节假日"""
    try:
        # 解析日期
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        # 使用 HolidayData 类判断是否为节假日
        is_holiday_flag, holiday_type = holiday_data.is_holiday(date_obj)
        
        return {
            "date": date_str,
            "is_holiday": is_holiday_flag,
            "holiday_type": holiday_type,
            "message": "查询成功"
        }
    except Exception as e:
        logger.error(f"判断节假日时发生错误: {str(e)}")
        return {
            "date": date_str,
            "is_holiday": False,
            "holiday_type": "",
            "message": f"判断节假日时发生错误: {str(e)}"
        }

async def get_holidays(year: int) -> dict:
    """获取指定年份的节假日列表"""
    try:
        # 使用 HolidayData 类获取节假日列表
        holidays = holiday_data.get_holidays(year)
        
        return {
            "year": year,
            "holidays": holidays,
            "count": len(holidays),
            "message": "查询成功"
        }
    except Exception as e:
        logger.error(f"获取节假日列表时发生错误: {str(e)}")
        return {
            "year": year,
            "holidays": [],
            "count": 0,
            "message": f"获取节假日列表时发生错误: {str(e)}"
        }

async def validate_date_status(date_records: list[dict]) -> dict:
    """验证日期的工作日/休息日状态是否正确
    
    Args:
        date_records: 日期记录列表，每个记录包含 date 和 status 字段
        
    Returns:
        dict: 验证结果，包含异常记录和统计信息
    """
    try:
        valid_records = []
        invalid_records = []
        
        for record in date_records:
            date_str = record.get("date")
            status = record.get("status")
            
            if not date_str or status is None:
                invalid_records.append({
                    "date": date_str,
                    "status": status,
                    "error": "缺少日期或状态字段"
                })
                continue
            
            try:
                # 解析日期
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                
                # 获取实际的节假日状态
                is_holiday_flag, holiday_type = holiday_data.is_holiday(date_obj)
                
                # 根据规则验证状态
                # 规则：工作日状态应为 true，休息日状态应为 false
                expected_status = not is_holiday_flag  # 工作日为 true，休息日为 false
                
                if status == expected_status:
                    # 状态正确
                    valid_records.append({
                        "date": date_str,
                        "status": status,
                        "expected_status": expected_status,
                        "actual_status": is_holiday_flag,
                        "holiday_type": holiday_type,
                        "valid": True
                    })
                else:
                    # 状态错误
                    invalid_records.append({
                        "date": date_str,
                        "status": status,
                        "expected_status": expected_status,
                        "actual_status": is_holiday_flag,
                        "holiday_type": holiday_type,
                        "error": f"状态异常：{date_str} 是{holiday_type}，状态应为 {expected_status}，实际为 {status}"
                    })
                    
            except ValueError as e:
                # 日期格式错误
                invalid_records.append({
                    "date": date_str,
                    "status": status,
                    "error": f"日期格式错误: {str(e)}"
                })
            except Exception as e:
                # 其他错误
                invalid_records.append({
                    "date": date_str,
                    "status": status,
                    "error": f"处理错误: {str(e)}"
                })
        
        # 生成验证结果
        result = {
            "total_records": len(date_records),
            "valid_records": len(valid_records),
            "invalid_records": len(invalid_records),
            "valid_records_detail": valid_records,
            "invalid_records_detail": invalid_records,
            "message": "验证完成"
        }
        
        return result
    except Exception as e:
        logger.error(f"验证日期状态时发生错误: {str(e)}")
        return {
            "error": f"验证日期状态时发生错误: {str(e)}"
        }

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
    """处理工具调用"""
    if name == "is_holiday":
        if not arguments or "date" not in arguments:
            return [TextContent(type="text", text=str({"error": "缺少 date 参数"}))]
        date_str = arguments["date"]
        result = await is_holiday(date_str)
        return [TextContent(type="text", text=str(result))]
    elif name == "get_holidays":
        if not arguments or "year" not in arguments:
            return [TextContent(type="text", text=str({"error": "缺少 year 参数"}))]
        year = arguments["year"]
        result = await get_holidays(year)
        return [TextContent(type="text", text=str(result))]
    elif name == "validate_date_status":
        if not arguments or "date_records" not in arguments:
            return [TextContent(type="text", text=str({"error": "缺少 date_records 参数"}))]
        date_records = arguments["date_records"]
        result = await validate_date_status(date_records)
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
    # 初始化节假日数据
    asyncio.run(main())