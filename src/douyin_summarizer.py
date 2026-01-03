"""抖音热搜 DeepSeek 总结模块"""
import logging
from typing import List, Dict
from openai import OpenAI

logger = logging.getLogger(__name__)


class DouyinSummarizer:
    """抖音热搜总结器"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com"):
        """
        初始化总结器
        
        Args:
            api_key: DeepSeek API Key
            base_url: API 基础 URL
        """
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        logger.info("抖音热搜总结器初始化成功")
    
    def summarize(self, topics: List[Dict]) -> str:
        """
        使用 DeepSeek 总结抖音热搜
        
        Args:
            topics: 热搜话题列表
        
        Returns:
            总结文本
        """
        try:
            logger.info(f"开始总结 {len(topics)} 个热搜话题")
            
            # 构造提示词
            prompt = self._build_prompt(topics)
            
            # 调用 DeepSeek API
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个专业的短视频内容分析师，擅长分析抖音热搜趋势和用户兴趣。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info(f"总结完成，长度: {len(summary)} 字符")
            
            return summary
            
        except Exception as e:
            logger.error(f"总结失败: {str(e)}")
            return ""
    
    def _build_prompt(self, topics: List[Dict]) -> str:
        """
        构造提示词
        
        Args:
            topics: 热搜话题列表
        
        Returns:
            提示词文本
        """
        # 标签映射
        label_map = {
            0: "",
            1: "🆕",
            2: "👍",
            3: "🔥"
        }
        
        # 格式化热搜列表
        topics_text = []
        for i, topic in enumerate(topics[:30], 1):  # 只取前 30 个
            word = topic.get("word", "")
            label = topic.get("label", 0)
            hotindex = topic.get("hotindex", 0)
            
            label_icon = label_map.get(label, "")
            topics_text.append(f"{i}. {label_icon} {word} (热度: {hotindex:,})")
        
        topics_str = "\n".join(topics_text)
        
        prompt = f"""请分析以下抖音热搜榜单，生成一份专业的热点分析报告：

{topics_str}

请按以下结构输出：

1. **整体趋势概述**（2-3句话概括当前热搜的主要特点和趋势）

2. **热点分类分析**（将热搜分为 3-4 个主要类别，如娱乐明星、社会民生、科技数码、生活方式等，每个类别列举 2-3 个代表性话题）

3. **现象洞察**（分析 2-3 个有趣的现象或趋势，如用户兴趣变化、内容类型偏好等）

4. **总结**（1-2句话总结今日抖音热搜的核心特点）

要求：
- 语言简洁专业，避免冗长
- 突出短视频平台的特点（如视觉冲击、娱乐性、传播速度等）
- 关注用户兴趣和内容趋势
- 字数控制在 500-800 字
"""
        
        return prompt
