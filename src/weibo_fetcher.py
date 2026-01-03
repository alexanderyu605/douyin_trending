"""微博热搜抓取模块"""
import requests
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class WeiboFetcher:
    """微博热搜抓取器"""
    
    def __init__(self, api_key: str):
        """
        初始化微博热搜抓取器
        
        Args:
            api_key: 天聚数行 API Key
        """
        self.api_key = api_key
        self.api_url = "https://apis.tianapi.com/weibohot/index"
        logger.info("微博热搜抓取器初始化成功")
    
    def fetch_hot_topics(self, limit: int = 50) -> List[Dict]:
        """
        抓取微博热搜榜单
        
        Args:
            limit: 返回的热搜数量，默认 50
        
        Returns:
            热搜列表，每个元素包含 hottag, hotword, hotwordnum
        """
        try:
            logger.info("开始抓取微博热搜榜单")
            
            # 发送请求
            params = {"key": self.api_key}
            response = requests.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            
            # 解析响应
            data = response.json()
            
            if data.get("code") != 200:
                error_msg = data.get("msg", "未知错误")
                logger.error(f"API 返回错误: {error_msg}")
                return []
            
            # 获取热搜列表
            hot_topics = data.get("result", {}).get("list", [])
            
            # 限制数量
            hot_topics = hot_topics[:limit]
            
            logger.info(f"成功获取 {len(hot_topics)} 个热搜话题")
            
            return hot_topics
            
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"抓取失败: {str(e)}")
            return []
    
    def format_topics(self, topics: List[Dict]) -> str:
        """
        格式化热搜话题为文本
        
        Args:
            topics: 热搜列表
        
        Returns:
            格式化后的文本
        """
        if not topics:
            return "暂无热搜数据"
        
        lines = []
        for i, topic in enumerate(topics, 1):
            hottag = topic.get("hottag", "")
            hotword = topic.get("hotword", "")
            hotwordnum = topic.get("hotwordnum", "0")
            
            # 格式化标签
            tag_str = f"[{hottag}]" if hottag else ""
            
            # 格式化热度
            try:
                heat = int(hotwordnum)
                if heat >= 10000:
                    heat_str = f"{heat/10000:.1f}万"
                else:
                    heat_str = str(heat)
            except:
                heat_str = hotwordnum
            
            lines.append(f"{i}. {tag_str} {hotword} (热度: {heat_str})")
        
        return "\n".join(lines)
