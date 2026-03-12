"""邮件发送服务 - SMTP"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM_NAME, SMTP_USE_TLS
from utils.logger import auth_logger


def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """发送邮件"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = SMTP_USER
        msg["To"] = to_email

        # 添加 HTML 内容
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        # 连接 SMTP 服务器
        if SMTP_USE_TLS:
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
        else:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)

        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, [to_email], msg.as_string())
        server.quit()

        auth_logger.info(f"邮件发送成功，to: {to_email}, subject: {subject}")
        return True
    except Exception as e:
        auth_logger.error(f"邮件发送失败，to: {to_email}, error: {e}")
        return False


def send_otp_email(to_email: str, code: str, expire_minutes: int = 5, subject_prefix: str = "验证码") -> bool:
    """发送验证码邮件"""
    subject = f"【好学生 AI 题库】{subject_prefix}"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .code {{ background: white; border: 2px dashed #667eea; padding: 15px; text-align: center; font-size: 32px; font-weight: bold; color: #667eea; letter-spacing: 5px; border-radius: 8px; margin: 20px 0; }}
            .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 20px; }}
            .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📚 题小宝</h1>
                <p>验证码邮件</p>
            </div>
            <div class="content">
                <p>您好！</p>
                <p>您正在登录题小宝，请使用以下验证码完成登录：</p>
                <div class="code">{code}</div>
                <p>验证码有效期为 <strong>{expire_minutes} 分钟</strong>，请尽快使用。</p>
                <div class="warning">
                    <strong>⚠️ 安全提示：</strong>
                    <ul style="margin: 10px 0;">
                        <li>如非本人操作，请忽略此邮件</li>
                        <li>请勿将验证码泄露给他人</li>
                        <li>工作人员不会向您索取验证码</li>
                    </ul>
                </div>
                <div class="footer">
                    <p>此邮件由系统自动发送，请勿回复</p>
                    <p>&copy; 2026 题小宝</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return send_email(to_email, subject, html_content)
