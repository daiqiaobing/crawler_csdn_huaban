# -*- coding: utf-8 -*-
import smtplib
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from crawler.huaban.lib import write_log
from utils import SUBJECT, SENDER, RECEIVERS, USERNAME, PASSWORD, PROJECT_PATH, BASE_IMG_PATH, \
    SMT_SERVER, From, TEST_URL, ADMIN_RECEIVERS


def get_html(img_url, message):
    if img_url:
        msg = """<div><div><p>您好：<br>&nbsp;&nbsp;点击CSDN博客的日流量统计图： <a href='{img_url}'>点击查看</a></p></div></div>""".format(
            img_url=img_url)
    else:
        msg = """<div><h4>您好</h4>：<br>&nbsp;&nbsp;{msg}</div>""".format(msg=message)
    # msg = '<img src="https://tva2.sinaimg.cn/crop.0.1.635.635.50/62d8efadgw1ej30downrsj20hs0hq0ws.jpg">'
    return msg


def send_msg(img_url, receivers, msg):
    html = get_html(img_url, msg)
    msg = MIMEText(html, 'html', 'utf-8')
    msg['Subject'] = Header(SUBJECT, 'utf-8')
    msg['From'] = From
    msg['To'] = u'admin <%s>' % ','.join(receivers)
    try:
        smtp = smtplib.SMTP()
        smtp.connect(SMT_SERVER)
        smtp.login(USERNAME, PASSWORD)
        smtp.sendmail(SENDER, receivers, msg.as_string())
        smtp.quit()
    except BaseException as e:
        write_log(u'邮件发送错误\n')


def notice_admin(msg):
    """通知管理员"""
    send_msg(None, ADMIN_RECEIVERS, msg)


def notice_result(img_url):
    """发送结果"""
    send_msg(img_url=img_url, receivers=RECEIVERS, msg=None)


if __name__ == '__main__':
    notice_result('错误消息')
