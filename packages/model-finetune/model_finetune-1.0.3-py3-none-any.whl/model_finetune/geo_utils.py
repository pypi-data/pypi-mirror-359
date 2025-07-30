"""
地理工具模块
提供地理坐标处理功能
"""
import math
import logging
from typing import Tuple, Union

logger = logging.getLogger(__name__)

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """计算两点之间的距离（封装 haversine 函数）
    
    Args:
        lat1: 第一个点的纬度
        lon1: 第一个点的经度
        lat2: 第二个点的纬度
        lon2: 第二个点的经度
        
    Returns:
        两点之间的距离（单位：米）
    """
    return haversine(lat1, lon1, lat2, lon2)

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    使用 Haversine 公式计算两个坐标点之间的距离
    
    Args:
        lat1: 第一个点的纬度
        lon1: 第一个点的经度
        lat2: 第二个点的纬度
        lon2: 第二个点的经度
        
    Returns:
        两点之间的距离（单位：米）
    """
    # 地球半径（米）
    R = 6371000
    
    # 将经纬度转换为弧度
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # 计算差值
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine 公式
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance

def convert_to_decimal_degrees(coordinates: str) -> Tuple[float, float]:
    """
    将度分秒格式或度分格式的坐标转换为十进制度数
    
    Args:
        coordinates: 坐标字符串，格式如 "N40°45'30.5" W73°59'45.6"" 或 "40°45.5'N 73°59.8'W"
        
    Returns:
        (纬度, 经度) 元组，单位为十进制度数
    """
    try:
        # 实现坐标转换逻辑
        # 这里只是一个简单的示例，实际实现需要根据具体需求调整
        return (0.0, 0.0)
    except Exception as e:
        logger.error(f"坐标转换失败: {str(e)}")
        return (0.0, 0.0)