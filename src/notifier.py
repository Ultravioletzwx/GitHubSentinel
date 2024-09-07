import smtplib
import markdown2
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from logger import LOG

class Notifier:
    def __init__(self, email_settings):
        self.email_settings = email_settings
    
    def notify(self, report, repo=None,source_type="github"):
        if self.email_settings:
            self.send_email(report,repo,source_type)
        else:
            LOG.warning("邮件设置未配置正确，无法发送通知")
    
    def send_email(self, report,repo,source_type):
        LOG.info("准备发送邮件")
        # 创建一个MIMEMultipart对象，用于构建邮件内容
        msg = MIMEMultipart()
        # 设置发件人地址
        msg['From'] = self.email_settings['from']
        # 设置收件人地址
        msg['To'] = self.email_settings['to']
        # 设置邮件主题
        if repo:
            msg['Subject'] = f"[{source_type}]{repo} 进展简报"
        else:
            msg['Subject'] = f"[{source_type}] 进展简报"
        # 将Markdown内容转换为HTML
        html_report = markdown2.markdown(report)
        # 将HTML内容添加到邮件中
        msg.attach(MIMEText(html_report, 'html'))
        try:
            # 使用smtplib库的SMTP_SSL方法连接到SMTP服务器
            with smtplib.SMTP_SSL(self.email_settings['smtp_server'], self.email_settings['smtp_port']) as server:
                LOG.debug("登录SMTP服务器")
                # 登录SMTP服务器
                server.login(msg['From'], self.email_settings['password'])
                # 发送邮件
                server.sendmail(msg['From'], msg['To'], msg.as_string())
                LOG.info("邮件发送成功！")
        except Exception as e:
            LOG.error(f"发送邮件失败：{str(e)}")


if __name__ == '__main__':
    from config import Config
    config = Config()
    notifier = Notifier(config.email)

    test_repo = "DjangoPeng/openai-quickstart"
    test_report = """
# DjangoPeng/openai-quickstart 项目进展

## 时间周期：2024-08-24

## 新增功能
- Assistants API 代码与文档

## 主要改进
- 适配 LangChain 新版本

## 修复问题
- 关闭了一些未解决的问题。

"""
    notifier.notify(test_repo, test_report)
