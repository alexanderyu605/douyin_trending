"""DeepSeek API总结模块"""
import logging
import os
import time
from typing import Optional

logger = logging.getLogger(__name__)

# 尝试导入 openai 库（DeepSeek 使用 OpenAI 兼容接口）
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("openai 库未安装，DeepSeek 功能将不可用。请运行: pip install openai")


class DeepSeekSummarizer:
    """DeepSeek总结器"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化DeepSeek总结器
        
        Args:
            api_key: DeepSeek API密钥，如果为None则从环境变量获取
            base_url: API基础URL，默认为DeepSeek官方API地址
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("openai 库未安装。请运行: pip install openai")
        
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DeepSeek API密钥未设置，请设置DEEPSEEK_API_KEY环境变量")
        
        # DeepSeek API 基础URL
        self.base_url = base_url or os.getenv("DEEPSEEK_API_BASE_URL", "https://api.deepseek.com")
        
        # 使用 OpenAI 兼容接口创建客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        # 使用的模型名称
        self.model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        
        # 重试配置
        self.max_retries = 3
        self.retry_delay = 2  # 秒
        
        # Reddit新闻总结提示词模板
        self.summary_prompt_template = """请对以下Reddit热门新闻帖子进行总结，要求：

1. 生成结构化的Markdown格式总结
2. 包含以下部分：
   - **今日热点概览**：简要概述今天的主要新闻话题
   - **重点新闻**：列出3-5个最重要的新闻（使用列表格式，包含标题和简要说明）
   - **热门讨论**：提取评分最高或讨论最热烈的话题
   - **总结**：一句话总结今日新闻的主要趋势

3. 使用中文输出
4. 保持客观、准确
5. 如果内容较长，可以适当精简但不要遗漏关键信息
6. 对于英文内容，请理解后用中文总结

Reddit热门帖子内容：
{content}

请开始总结："""
    
    def summarize(self, content: str, context: str = "") -> Optional[str]:
        """
        总结内容
        
        Args:
            content: 要总结的文本内容
            context: 额外的上下文信息（可选）
            
        Returns:
            Markdown格式的总结，如果失败返回None
        """
        if not content or len(content.strip()) == 0:
            logger.warning("内容为空，无法总结")
            return None
        
        logger.info(f"开始总结内容，长度: {len(content)} 字符")
        
        # 构建提示词
        prompt = self.summary_prompt_template.format(content=content)
        
        # 如果有额外上下文，添加到提示词中
        if context:
            prompt = f"上下文：{context}\n\n" + prompt
        
        # 重试机制
        last_error = None
        for attempt in range(self.max_retries):
            try:
                # 使用 OpenAI 兼容接口调用 DeepSeek API
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                
                # 检查响应
                if not response:
                    logger.error("DeepSeek API返回空响应对象")
                    continue
                
                # 获取响应文本
                if hasattr(response, 'choices') and response.choices:
                    choice = response.choices[0]
                    if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                        summary_text = choice.message.content
                    elif hasattr(choice, 'text'):
                        summary_text = choice.text
                    else:
                        logger.error("无法从响应中提取文本内容")
                        continue
                else:
                    logger.error("响应中没有 choices")
                    continue
                
                if not summary_text:
                    logger.warning("总结内容为空")
                    continue
                
                summary = summary_text.strip()
                
                if not summary:
                    logger.warning("总结内容为空（去除空白后）")
                    continue
                
                logger.info(f"总结完成，长度: {len(summary)} 字符")
                return summary
                
            except Exception as e:
                last_error = e
                error_msg = str(e)
                
                # 记录详细错误信息
                logger.warning(f"第 {attempt + 1} 次尝试失败: {error_msg}")
                
                # 检查是否是配额错误（429）
                if "429" in error_msg or "rate limit" in error_msg.lower() or "quota" in error_msg.lower():
                    wait_time = self.retry_delay * (attempt + 1) * 2
                    logger.info(f"遇到配额限制，等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                # 检查是否是临时错误（500, 503）
                elif "500" in error_msg or "503" in error_msg or "service unavailable" in error_msg.lower():
                    wait_time = self.retry_delay * (attempt + 1)
                    logger.info(f"遇到服务器错误，等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                # 其他错误通常不应该重试
                elif "400" in error_msg or "401" in error_msg or "403" in error_msg or "404" in error_msg:
                    logger.error(f"请求错误，不重试: {error_msg}")
                    return None
                # 网络错误可以重试
                else:
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay * (attempt + 1)
                        logger.info(f"等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
        
        # 所有重试都失败
        logger.error(f"总结内容失败，已重试 {self.max_retries} 次。最后错误: {last_error}")
        return None
