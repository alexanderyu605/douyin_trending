"""微博热搜邮件通知模块"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)


class WeiboEmailNotifier:
    """微博热搜邮件通知器"""
    
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
        logger.info("微博热搜邮件通知器初始化成功")
    
    def send_email(self, summary: str, topics: List[Dict]) -> bool:
        """
        发送微博热搜邮件
        
        Args:
            summary: AI 总结内容
            topics: 热搜列表
        
        Returns:
            是否发送成功
        """
        try:
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"微博热搜榜 - {datetime.now().strftime('%Y-%m-%d')}"
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
            topics: 热搜列表
        
        Returns:
            HTML 内容
        """
        # 生成热搜列表 HTML
        topics_html = ""
        for i, topic in enumerate(topics[:30], 1):  # 只显示前 30 个
            hottag = topic.get("hottag", "")
            hotword = topic.get("hotword", "")
            hotwordnum = topic.get("hotwordnum", "0")
            
            # 格式化热度
            try:
                heat = int(hotwordnum)
                if heat >= 10000:
                    heat_str = f"{heat/10000:.1f}万"
                else:
                    heat_str = str(heat)
            except:
                heat_str = hotwordnum
            
            # 标签颜色
            tag_color = "#ff6b6b" if hottag == "热" else "#4ecdc4" if hottag == "新" else "#95e1d3"
            tag_html = f'<span style="background-color: {tag_color}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 12px; margin-right: 8px;">{hottag}</span>' if hottag else ""
            
            # 微博链接
            weibo_url = f"https://s.weibo.com/weibo?q={hotword}"
            
            topics_html += f"""
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 12px 8px; text-align: center; color: #999; width: 40px;">{i}</td>
                <td style="padding: 12px 8px;">
                    {tag_html}
                    <a href="{weibo_url}" style="color: #333; text-decoration: none; font-size: 14px;">{hotword}</a>
                </td>
                <td style="padding: 12px 8px; text-align: right; color: #ff6b6b; font-weight: bold; width: 100px;">{heat_str}</td>
            </tr>
            """
        
        # 完整 HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f5f5f5;">
            <div style="background-color: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden;">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 28px;">📱 微博热搜榜</h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 14px;">{datetime.now().strftime('%Y年%m月%d日')}</p>
                </div>
                
                <!-- AI Summary -->
                <div style="padding: 30px; background-color: #f8f9fa; border-bottom: 3px solid #667eea;">
                    <h2 style="color: #667eea; margin-top: 0; font-size: 20px; display: flex; align-items: center;">
                        <span style="margin-right: 10px;">🤖</span> AI 智能总结
                    </h2>
                    <div style="background-color: white; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea; line-height: 1.8; white-space: pre-wrap;">{summary}</div>
                </div>
                
                <!-- Hot Topics List -->
                <div style="padding: 30px;">
                    <h2 style="color: #333; margin-top: 0; font-size: 20px; display: flex; align-items: center;">
                        <span style="margin-right: 10px;">🔥</span> 热搜榜单（Top 30）
                    </h2>
                    <table style="width: 100%; border-collapse: collapse; background-color: white; border-radius: 8px; overflow: hidden;">
                        {topics_html}
                    </table>
                </div>
                
                <!-- Footer -->
                <div style="padding: 20px; text-align: center; background-color: #f8f9fa; border-top: 1px solid #eee;">
                    <p style="color: #999; font-size: 12px; margin: 0;">
                        数据来源：微博热搜榜 | 由 AI 自动生成
                    </p>
                    <p style="color: #999; font-size: 12px; margin: 5px 0 0 0;">
                        更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
