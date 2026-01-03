"""抖音热搜自动推送主程序"""
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from douyin_fetcher import DouyinFetcher
from douyin_summarizer import DouyinSummarizer
from douyin_email_notifier import DouyinEmailNotifier

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('douyin_trending.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """主函数"""
    try:
        logger.info("="*80)
        logger.info("抖音热搜自动推送程序启动")
        logger.info(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*80)
        
        # 加载环境变量
        load_dotenv()
        
        # 获取配置
        tianapi_key = os.getenv("TIANAPI_KEY")
        deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        deepseek_base_url = os.getenv("DEEPSEEK_BASE_URL")
        email_sender = os.getenv("EMAIL_SENDER")
        email_password = os.getenv("EMAIL_PASSWORD")
        email_recipient = os.getenv("EMAIL_RECIPIENT")
        smtp_server = os.getenv("SMTP_SERVER", "smtp.163.com")
        smtp_port = int(os.getenv("SMTP_PORT", "465"))
        
        # 检查必要的配置
        if not tianapi_key:
            logger.error("TIANAPI_KEY 未设置")
            return False
        
        if not deepseek_api_key:
            logger.error("DEEPSEEK_API_KEY 未设置")
            return False
        
        if not all([email_sender, email_password, email_recipient]):
            logger.error("邮件配置不完整")
            return False
        
        # 步骤 1: 抓取抖音热搜
        logger.info("\n[步骤 1/4] 抓取抖音热搜...")
        fetcher = DouyinFetcher(tianapi_key)
        topics = fetcher.fetch_trending()
        
        if not topics:
            logger.error("未能获取抖音热搜数据")
            return False
        
        logger.info(f"成功获取 {len(topics)} 个热搜话题")
        
        # 保存原始数据
        with open('douyin_topics_raw.txt', 'w', encoding='utf-8') as f:
            f.write(fetcher.format_topics(topics))
        logger.info("原始热搜数据已保存到 douyin_topics_raw.txt")
        
        # 步骤 2: DeepSeek 总结
        logger.info("\n[步骤 2/4] 使用 DeepSeek 生成总结...")
        summarizer = DouyinSummarizer(deepseek_api_key, deepseek_base_url)
        summary = summarizer.summarize(topics)
        
        if not summary:
            logger.error("AI 总结失败")
            return False
        
        logger.info(f"总结生成成功，长度: {len(summary)} 字符")
        
        # 保存总结
        with open('douyin_summary.md', 'w', encoding='utf-8') as f:
            f.write(f"# 抖音热搜总结 - {datetime.now().strftime('%Y-%m-%d')}\n\n")
            f.write(summary)
            f.write("\n\n---\n\n")
            f.write("## 完整热搜榜单\n\n")
            f.write(fetcher.format_topics(topics))
        logger.info("总结内容已保存到 douyin_summary.md")
        
        # 步骤 3: 发送邮件
        logger.info("\n[步骤 3/4] 发送邮件通知...")
        notifier = DouyinEmailNotifier(
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            sender=email_sender,
            password=email_password,
            recipient=email_recipient
        )
        
        email_sent = notifier.send_email(summary, topics)
        
        if email_sent:
            logger.info("="*80)
            logger.info("✅ 邮件发送成功！")
            logger.info(f"收件人: {email_recipient}")
            logger.info(f"话题数量: {len(topics)}")
            logger.info("="*80)
            return True
        else:
            logger.error("邮件发送失败")
            return False
            
    except Exception as e:
        logger.error(f"程序执行失败: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
