"""抖音热搜邮件通知模块"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)


class DouyinEmailNotifier:
    """抖音邮件通知器"""
    
    def __init__(self, smtp_server: str, smtp_port: int, sender: str, password: str, recipient: str):
        """
        初始化邮件通知器
        
        Args:
            smtp_server: SMTP 服务器地址
            smtp_port: SMTP 服务器端口
            sender: 发件人邮箱
            password: 发件人邮箱密码/授权码
            recipient: 收件人邮箱
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender = sender
        self.password = password
        self.recipient = recipient
        logger.info("抖音热搜邮件通知器初始化成功")
    
    def send_email(self, summary: str, topics: List[Dict]) -> bool:
        """
        发送抖音热搜邮件
        
        Args:
            summary: AI 总结内容
            topics: 热搜话题列表
        
        Returns:
            是否发送成功
        """
        try:
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"抖音热搜榜 - {datetime.now().strftime('%Y-%m-%d')}"
            msg['From'] = self.sender
            msg['To'] = self.recipient
            
            # 生成 HTML 内容
            html_content = self._generate_html(summary, topics)
            
            # 添加 HTML 部分
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 发送邮件（最多重试 3 次）
            for attempt in range(3):
                try:
                    logger.info(f"尝试发送邮件（第 {attempt + 1} 次）")
                    
                    with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=30) as server:
                        server.login(self.sender, self.password)
                        server.send_message(msg)
                    
                    logger.info(f"邮件发送成功：{msg['Subject']}")
                    return True
                    
                except smtplib.SMTPException as e:
                    logger.warning(f"第 {attempt + 1} 次发送失败: {str(e)}")
                    if attempt == 2:
                        raise
            
            return False
            
        except Exception as e:
            logger.error(f"邮件发送失败: {str(e)}")
            return False
    
    def _generate_html(self, summary: str, topics: List[Dict]) -> str:
        """
        生成 HTML 邮件内容
        
        Args:
            summary: AI 总结
            topics: 热搜话题列表
        
        Returns:
            HTML 内容
        """
        # 标签映射
        label_map = {
            0: "",
            1: '<span style="background-color: #ff2d55; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px; margin-left: 5px;">新</span>',
            2: '<span style="background-color: #ff9500; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px; margin-left: 5px;">荐</span>',
            3: '<span style="background-color: #ff3b30; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px; margin-left: 5px;">热</span>'
        }
        
        # 生成热搜列表 HTML
        topics_html = ""
        for i, topic in enumerate(topics[:50], 1):
            word = topic.get("word", "")
            label = topic.get("label", 0)
            hotindex = topic.get("hotindex", 0)
            
            label_html = label_map.get(label, "")
            
            # 根据排名设置不同的样式
            if i <= 3:
                rank_style = "background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; font-weight: bold;"
            elif i <= 10:
                rank_style = "background-color: #ff2d55; color: white; font-weight: bold;"
            else:
                rank_style = "background-color: #f0f0f0; color: #333;"
            
            topics_html += f"""
            <div style="background-color: white; padding: 15px; margin-bottom: 10px; border-radius: 8px; border-left: 4px solid #000; display: flex; align-items: center;">
                <span style="{rank_style} padding: 8px 12px; border-radius: 6px; font-size: 16px; min-width: 40px; text-align: center; margin-right: 15px;">#{i}</span>
                <div style="flex: 1;">
                    <span style="color: #333; font-size: 15px; font-weight: 500;">{word}</span>
                    {label_html}
                    <div style="color: #999; font-size: 13px; margin-top: 5px;">🔥 热度: {hotindex:,}</div>
                </div>
            </div>
            """
        
        # 完整 HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f5f5f5;">
            <div style="background-color: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); overflow: hidden;">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #000000 0%, #434343 100%); padding: 40px 30px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 32px; font-weight: bold;">🎵 抖音热搜榜</h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 15px;">{datetime.now().strftime('%Y年%m月%d日')} | 实时热点</p>
                </div>
                
                <!-- AI Summary -->
                <div style="padding: 30px; background-color: #fafafa; border-bottom: 3px solid #000;">
                    <h2 style="color: #000; margin-top: 0; font-size: 22px; display: flex; align-items: center;">
                        <span style="margin-right: 10px;">🤖</span> AI 智能分析
                    </h2>
                    <div style="background-color: white; padding: 20px; border-radius: 8px; border-left: 4px solid #000; line-height: 1.8; white-space: pre-wrap;">{summary}</div>
                </div>
                
                <!-- Topics List -->
                <div style="padding: 30px; background-color: #f5f5f5;">
                    <h2 style="color: #333; margin-top: 0; font-size: 22px; display: flex; align-items: center;">
                        <span style="margin-right: 10px;">📊</span> 热搜榜单（Top 50）
                    </h2>
                    {topics_html}
                </div>
                
                <!-- Footer -->
                <div style="padding: 25px; text-align: center; background-color: #fafafa; border-top: 1px solid #eee;">
                    <p style="color: #999; font-size: 13px; margin: 0;">
                        数据来源：抖音 App | 由 AI 自动生成
                    </p>
                    <p style="color: #999; font-size: 13px; margin: 5px 0 0 0;">
                        更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
