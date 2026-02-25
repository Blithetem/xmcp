
import os
import sys
import time
import hmac
import hashlib
import requests
import re
import traceback
import json
import datetime
import logging
from typing import Union, Optional, Dict, Any, List
from functools import lru_cache

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkDayConfig:
    """工作日配置类，管理环境配置和敏感信息"""
    
    def __init__(self, env: int = 1):
        self.env = env
        if env == 1:
            # 正式环境
            self.open_plat = "http://open-plat.tpo.xzoa.com"
            self.center_url = "http://auth-center.tpo.xzoa.com"
            self.app_id = os.getenv('WORKDAY_APP_ID', '9026db1c-1b2a-11f0-a718-0ae143bd4647')
            self.app_secret = os.getenv('WORKDAY_APP_SECRET', 'b61ff81c36869b8ddb93dc31772268d2')
        else:
            # 测试环境
            self.open_plat = "http://open-plat-dev.tpo.xzoa.com"
            self.center_url = "http://auth-center-dev.tpo.xzoa.com"
            self.app_id = os.getenv('WORKDAY_APP_ID', '0e048a400706441898a8acf96bb60253')
            self.app_secret = os.getenv('WORKDAY_APP_SECRET', 'xYkdARUQyDeIvCNZjuMRUv3dkw6q56tPS7KANc3MjumLI4xl')
    
    @property
    def is_production(self) -> str:
        return "正式环境" if self.env == 1 else "测试环境"

# 创建默认配置实例
config = WorkDayConfig(ENV if 'ENV' in globals() else 1)


def http_post_json(post_url: str, json_data: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Optional[str]:
    """
    发送HTTP POST请求并返回响应文本
    
    Args:
        post_url: 请求URL
        json_data: 要发送的JSON数据
        headers: 请求头
        
    Returns:
        响应文本，失败时返回None
    """
    try:
        response = requests.post(post_url, json=json_data, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP POST请求失败 [{post_url}]: {str(e)}")
        return None

@lru_cache(maxsize=1)
def get_access_token(center_url: str, app_id: str, app_secret: str) -> Optional[str]:
    """
    获取机器人访问令牌（带缓存）
    
    Args:
        center_url: 认证中心URL
        app_id: 应用ID
        app_secret: 应用密钥
        
    Returns:
        访问令牌，失败时返回None
    """
    if not app_id:
        logger.error("应用ID为空")
        return None
        
    url = f"{center_url}/api/auth/v1/robot/GetRobotAccessToken"
    payload = {
        "robot_guid": app_id,
        "robot_secret": app_secret
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    response = http_post_json(url, json_data=payload, headers=headers)
    if not response:
        return None

    try:
        token_data = json.loads(response)
        if "data" not in token_data or "access_token" not in token_data["data"]:
            logger.error("访问令牌响应格式不正确")
            return None
        return token_data["data"]["access_token"]
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"解析访问令牌失败: {str(e)}")
        return None


@lru_cache(maxsize=10)
def get_holiday_data(year: int, base_url: str, center_url: str, app_id: str, app_secret: str) -> Optional[List[Dict[str, Any]]]:
    """
    获取指定年份的假期数据（带缓存）
    
    Args:
        year: 年份
        base_url: 基础URL
        center_url: 认证中心URL
        app_id: 应用ID
        app_secret: 应用密钥
        
    Returns:
        假期数据列表，失败时返回None
    """
    query = {"start_year": year, "end_year": year}
    api_url = f"{base_url}/api/cal/holiday/list"

    access_token = get_access_token(center_url, app_id, app_secret)
    if not access_token:
        logger.error("获取访问令牌失败")
        return None

    try:
        response = requests.get(api_url, params=query, headers={"Authorization": access_token}, timeout=10)
        response.raise_for_status()
        data = json.loads(response.text)
        
        if "data" not in data or "business_holiday" not in data["data"]:
            logger.error("假期数据响应格式不正确")
            return None
            
        return data["data"]["business_holiday"]
    except (requests.exceptions.RequestException, json.JSONDecodeError, KeyError) as e:
        logger.error(f"获取假期数据失败: {str(e)}")
        return None

def get_work_day(year: int, timestamp: int, base_url: Optional[str] = None, tag: Optional[str] = None) -> Union[bool, List[Dict[str, Any]], None]:
    """
    获取指定日期是否为工作日

    Args:
        year: 年份
        timestamp: 时间戳（秒）
        base_url: 基础URL（可选，默认使用配置中的URL）
        tag: 如果为"list"，返回完整的工作日列表

    Returns:
        bool: 如果是工作日返回True，否则返回False
        list: 如果tag为"list"，返回工作日列表
        None: 如果获取失败

    注意：
        - 假期日历记录的是不符合默认规则的日期（如调休、特殊假期）
        - 周一到周五默认是工作日，除非在假期列表中标记为休息
        - 周六周日默认是休息日，除非在假期列表中标记为工作日（调休）
    """
    if base_url is None:
        base_url = config.open_plat
    
    holiday_data = get_holiday_data(year, base_url, config.center_url, config.app_id, config.app_secret)
    
    if holiday_data is None:
        logger.error("获取假期数据失败")
        return None
    
    if tag == "list":
        return holiday_data
    
    # 将假期列表转换为字典以提高查找效率
    holiday_dict = {item["date"]: item["is_work_day"] for item in holiday_data}
    
    # 检查是否在假期列表中（记录的是例外日期）
    if timestamp in holiday_dict:
        return holiday_dict[timestamp]

    # 如果不在列表中，根据星期几判断默认规则
    dt = datetime.datetime.fromtimestamp(timestamp)
    weekday = dt.weekday()  # 0=周一, 6=周日
    return weekday < 5  # 周一到周五是工作日
def is_workday(date: Union[datetime.date, datetime.datetime]) -> bool:
    """
    检查指定日期是否为工作日

    Args:
        date: 可以是 datetime.date 或 datetime.datetime 对象

    Returns:
        bool: 如果是工作日返回True，否则返回False
    """
    # 记录调试信息
    logger.info(f"网址: {config.open_plat}")
    logger.info(f"appid: {config.app_id}")
    logger.info(f"date: {date}")
    logger.info(f"环境: {config.is_production}")
    
    try:
        # 处理不同的日期类型
        if isinstance(date, datetime.datetime):
            date_datetime = date
        elif isinstance(date, datetime.date):
            date_datetime = datetime.datetime.combine(date, datetime.datetime.min.time())
        else:
            logger.error(f"不支持的日期类型: {type(date)}")
            return False

        # 获取年份和时间戳
        year = date_datetime.year
        timestamp = int(date_datetime.timestamp())

        # 调用API检查是否为工作日
        result = get_work_day(year, timestamp)

        # 处理获取失败的情况
        if result is None:
            logger.warning("获取工作日信息失败，根据星期几判断")
            weekday = date_datetime.weekday()
            return weekday < 5  # 周一到周五默认是工作日

        return bool(result)

    except Exception as e:
        logger.error(f"检查工作日时发生错误: {str(e)}")
        logger.debug(f"错误详情: {traceback.format_exc()}")
        return False

# 为了向后兼容，保留原有的全局变量访问方式
ENV = config.env
open_plat = config.open_plat
center_url = config.center_url
CAUTOTEST = config.app_id
CAUTOTEST_secret = config.app_secret

if __name__ == "__main__":
    date = datetime.datetime.now()
    date = datetime.datetime(2026, 2, 18)
    is_workdays = is_workday(date)
    print(f"is_workdays:{is_workdays}")