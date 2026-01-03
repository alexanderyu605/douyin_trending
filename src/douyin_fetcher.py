"""抖音热搜抓取模块"""
import requests
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class DouyinFetcher:
    """抖音热搜抓取器"""
    
    def __init__(self, api_key: str):
        """
        初始化抖音热搜抓取器
        
        Args:
            api_key: 天聚数行 API Key
        """
        self.api_key = api_key
        self.api_url = "https://apis.tianapi.com/douyinhot/index"
        logger.info("抖音热搜抓取器初始化成功")
    
    def fetch_trending(self) -> List[Dict]:
        """
        抓取抖音热搜榜单
        
        Returns:
            热搜话题列表
        """
        try:
            logger.info("开始抓取抖音热搜榜单")
            
            # 构造请求参数
            params = {
                "key": self.api_key
            }
            
            # 发送请求
            response = requests.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            
            # 解析响应
            data = response.json()
            
            if data.get("code") != 200:
                error_msg = data.get("msg", "未知错误")
                logger.error(f"API 返回错误: {error_msg}")
                return []
            
            # 提取热搜列表
            topics = data.get("result", {}).get("list", [])
            
            if not topics:
                logger.warning("未获取到热搜数据")
                return []
            
            logger.info(f"成功获取 {len(topics)} 个热搜话题")
            return topics
            
        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求失败: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"抓取失败: {str(e)}")
            return []
    
    def format_topics(self, topics: List[Dict]) -> str:
        """
        格式化热搜话题列表
        
        Args:
            topics: 热搜话题列表
        
        Returns:
            格式化后的文本
        """
        if not topics:
            return "暂无数据"
        
        # 标签映射
        label_map = {
            0: "",
            1: "[新]",
            2: "[荐]",
            3: "[热]"
        }
        
        lines = []
        for i, topic in enumerate(topics, 1):
            word = topic.get("word", "")
            label = topic.get("label", 0)
            hotindex = topic.get("hotindex", 0)
            
            label_text = label_map.get(label, "")
            lines.append(f"{i}. {label_text} {word} (热度: {hotindex:,})")
        
        return "\n".join(lines)
