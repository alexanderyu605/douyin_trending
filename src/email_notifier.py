"""SMTP邮件发送模块"""
import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from typing import List, Dict, Optional
from datetime import datetime
import markdown

logger = logging.getLogger(__name__)


class EmailNotifier:
    """邮件通知器"""
    
    def __init__(self,
                 smtp_host: Optional[str] = None,
                 smtp_port: Optional[int] = None,
                 smtp_user: Optional[str] = None,
                 smtp_password: Optional[str] = None,
                 smtp_from: Optional[str] = None,
                 smtp_to: Optional[str] = None,
                 use_tls: bool = True,
                 use_ssl: bool = False):
        """
        初始化邮件通知器
        
        Args:
            smtp_host: SMTP服务器地址
            smtp_port: SMTP服务器端口
            smtp_user: SMTP用户名
            smtp_password: SMTP密码
            smtp_from: 发件人邮箱
            smtp_to: 收件人邮箱（多个用逗号分隔）
            use_tls: 是否使用TLS
            use_ssl: 是否使用SSL
        """
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST")
        self.smtp_port = int(smtp_port or os.getenv("SMTP_PORT", "587"))
        self.smtp_user = smtp_user or os.getenv("SMTP_USER")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")
        self.smtp_from = smtp_from or os.getenv("SMTP_FROM")
        
        # 解析收件人列表
        smtp_to_env = smtp_to or os.getenv("SMTP_TO", "")
        self.smtp_to_list = [
            email.strip() for email in smtp_to_env.split(",")
            if email.strip()
        ]
        
        # 根据端口自动判断使用SSL还是TLS
        if self.smtp_port == 465:
            self.use_ssl = True
            self.use_tls = False
            logger.debug(f"端口465，自动使用SSL")
        elif self.smtp_port == 587:
            self.use_tls = use_tls if use_tls is not None else (
                os.getenv("SMTP_USE_TLS", "true").lower() == "true"
            )
            self.use_ssl = False
            logger.debug(f"端口587，使用TLS: {self.use_tls}")
        else:
            self.use_tls = use_tls if use_tls is not None else (
                os.getenv("SMTP_USE_TLS", "true").lower() == "true"
            )
            self.use_ssl = use_ssl if use_ssl is not None else (
                os.getenv("SMTP_USE_SSL", "false").lower() == "true"
            )
            logger.debug(f"端口{self.smtp_port}，使用TLS: {self.use_tls}, SSL: {self.use_ssl}")
        
        # 验证必要参数
        if not all([self.smtp_host, self.smtp_port, self.smtp_user,
                   self.smtp_password, self.smtp_from]):
            raise ValueError("SMTP配置不完整，请检查环境变量")
        
        if not self.smtp_to_list:
            raise ValueError("收件人邮箱未设置")
    
    def _create_email(self, subject: str, html_content: str,
                     text_content: Optional[str] = None) -> MIMEMultipart:
        """
        创建邮件消息
        
        Args:
            subject: 邮件主题
            html_content: HTML内容
            text_content: 纯文本内容（可选）
            
        Returns:
            MIMEMultipart邮件对象
        """
        msg = MIMEMultipart('alternative')
        msg['From'] = Header(self.smtp_from, 'utf-8')
        msg['To'] = Header(','.join(self.smtp_to_list), 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        
        # 添加纯文本版本（如果有）
        if text_content:
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            msg.attach(text_part)
        
        # 添加HTML版本
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        return msg
    
    def _markdown_to_html(self, markdown_text: str) -> str:
        """
        将Markdown转换为HTML
        
        Args:
            markdown_text: Markdown文本
            
        Returns:
            HTML文本
        """
        html = markdown.markdown(
            markdown_text,
            extensions=['extra', 'codehilite', 'nl2br']
        )
        return html
    
    def _create_reddit_email_html(self, summary: str, posts: List[Dict]) -> str:
        """
        创建Reddit新闻邮件HTML内容
        
        Args:
            summary: DeepSeek生成的总结
            posts: Reddit帖子列表
            
        Returns:
            HTML内容
        """
        html_parts = [
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            '<meta charset="utf-8">',
            '<style>',
            'body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }',
            'h1 { color: #FF4500; border-bottom: 3px solid #FF4500; padding-bottom: 10px; }',
            'h2 { color: #34495e; margin-top: 20px; }',
            'a { color: #0079D3; text-decoration: none; }',
            'a:hover { text-decoration: underline; }',
            '.summary-section { margin: 20px 0; padding: 20px; background-color: #f8f9fa; border-left: 4px solid #FF4500; border-radius: 5px; }',
            '.post-item { margin: 15px 0; padding: 15px; background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 5px; }',
            '.post-title { font-size: 16px; font-weight: bold; margin-bottom: 8px; }',
            '.post-meta { color: #7f8c8d; font-size: 14px; margin-bottom: 8px; }',
            '.post-link { color: #0079D3; font-size: 14px; }',
            'code { background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px; }',
            'pre { background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }',
            'ul, ol { margin: 10px 0; padding-left: 25px; }',
            'li { margin: 5px 0; }',
            '.footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #e0e0e0; color: #7f8c8d; font-size: 12px; text-align: center; }',
            '</style>',
            '</head>',
            '<body>',
            f'<h1>🔥 Reddit 今日热点新闻</h1>',
            f'<p style="color: #7f8c8d;">日期：{datetime.now().strftime("%Y年%m月%d日 %H:%M")}</p>',
        ]
        
        # 添加AI总结部分
        if summary:
            summary_html = self._markdown_to_html(summary)
            html_parts.extend([
                '<div class="summary-section">',
                '<h2>📊 AI 智能总结</h2>',
                summary_html,
                '</div>'
            ])
        
        # 添加原始帖子列表
        html_parts.extend([
            '<h2>📰 热门帖子详情</h2>',
            f'<p>共 {len(posts)} 个热门帖子</p>'
        ])
        
        for idx, post in enumerate(posts, 1):
            post_title = post.get('title', '未知标题')
            post_link = post.get('permalink', '#')
            post_score = post.get('score', 0)
            post_comments = post.get('num_comments', 0)
            post_author = post.get('author', 'unknown')
            
            html_parts.extend([
                f'<div class="post-item">',
                f'<div class="post-title">{idx}. {post_title}</div>',
                f'<div class="post-meta">👤 u/{post_author} | ⬆️ {post_score} 分 | 💬 {post_comments} 评论</div>',
                f'<div><a href="{post_link}" class="post-link">查看讨论 →</a></div>',
                '</div>'
            ])
        
        html_parts.extend([
            '<div class="footer">',
            '<p>此邮件由 Reddit 新闻自动总结系统生成</p>',
            '<p>数据来源：Reddit r/news | AI 总结：DeepSeek</p>',
            '</div>',
            '</body>',
            '</html>'
        ])
        
        return '\n'.join(html_parts)
    
    def send_reddit_news_email(self, summary: str, posts: List[Dict],
                               max_retries: int = 3) -> bool:
        """
        发送Reddit新闻邮件
        
        Args:
            summary: AI生成的总结
            posts: Reddit帖子列表
            max_retries: 最大重试次数
            
        Returns:
            是否发送成功
        """
        if not posts:
            logger.warning("没有帖子需要发送")
            return False
        
        # 创建邮件内容
        date_str = datetime.now().strftime("%Y-%m-%d")
        subject = f"Reddit 今日热点新闻 - {date_str}"
        html_content = self._create_reddit_email_html(summary, posts)
        
        # 创建纯文本版本（简化版）
        text_content = f"Reddit 今日热点新闻\n"
        text_content += f"日期：{date_str}\n"
        text_content += f"共 {len(posts)} 个热门帖子\n\n"
        if summary:
            text_content += f"AI 总结：\n{summary}\n\n"
        text_content += "热门帖子：\n"
        for idx, post in enumerate(posts, 1):
            text_content += f"{idx}. {post.get('title', '未知标题')}\n"
            text_content += f"   链接：{post.get('permalink', '#')}\n"
            text_content += f"   评分：{post.get('score', 0)} | 评论：{post.get('num_comments', 0)}\n\n"
        
        # 创建邮件消息
        msg = self._create_email(subject, html_content, text_content)
        
        # 发送邮件（带重试）
        for attempt in range(max_retries):
            try:
                logger.info(f"尝试发送邮件（第 {attempt + 1} 次）")
                
                if self.use_ssl:
                    server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=30)
                    logger.debug(f"使用SSL连接到 {self.smtp_host}:{self.smtp_port}")
                else:
                    server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30)
                    logger.debug(f"使用SMTP连接到 {self.smtp_host}:{self.smtp_port}")
                
                if self.use_tls and not self.use_ssl:
                    server.starttls()
                    logger.debug("已启动TLS加密")
                
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_from, self.smtp_to_list, msg.as_string())
                server.quit()
                
                logger.info(f"邮件发送成功：{subject}")
                return True
                
            except Exception as e:
                logger.error(f"发送邮件失败（第 {attempt + 1} 次）: {e}")
                if attempt < max_retries - 1:
                    logger.info("等待重试...")
                else:
                    logger.error("邮件发送失败，已达到最大重试次数")
        
        return False
