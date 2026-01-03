"""微博热搜 DeepSeek 总结模块"""
import logging
import os
from typing import Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class WeiboSummarizer:
    """微博热搜总结器"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化微博热搜总结器
        
        Args:
            api_key: DeepSeek API密钥
            base_url: API基础URL
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DeepSeek API密钥未设置")
        
        self.base_url = base_url or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        self.model_name = "deepseek-chat"
        logger.info("微博热搜总结器初始化成功")
    
    def summarize(self, topics: list) -> Optional[str]:
        """
        总结微博热搜话题
        
        Args:
            topics: 热搜列表
        
        Returns:
            总结文本
        """
        try:
            logger.info(f"开始总结 {len(topics)} 个热搜话题")
            
            # 构建内容
            content = "\n".join([
                f"{i+1}. [{t.get('hottag', '')}] {t.get('hotword', '')} (热度: {t.get('hotwordnum', '0')})"
                for i, t in enumerate(topics[:30])
            ])
            
            # 构建提示词
            prompt = f"""请对以下微博热搜话题进行智能总结和分析：

{content}

要求：
1. 用简洁的语言概括当前的热点话题和趋势
2. 突出最受关注的热搜内容（前5-10个）
3. 分析这些热搜背后反映的社会现象或热点事件
4. 如果有明显的主题分类（如娱乐、科技、社会等），可以分类说明
5. 总结字数控制在 300-500 字
6. 使用中文输出

请开始总结："""
            
            # 调用 API
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info(f"总结完成，长度: {len(summary)} 字符")
            
            return summary
            
        except Exception as e:
            logger.error(f"总结失败: {str(e)}")
            return None
