# -*- coding: utf-8 -*-
import os

import datetime

AUTHOR = '何绣'

"""
common
"""
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
BASE_LOG_PATH = PROJECT_PATH + '/log/'
BASE_IMG_PATH = PROJECT_PATH + '/crawler/img/statistic/'
LOG_FILENAME = BASE_LOG_PATH + 'log.log'
DATE_FORMATE = '%Y-%m-%d %H:%M:%S'

LOG_IMG = BASE_LOG_PATH + 'img.log'
LOG_URL = BASE_LOG_PATH + 'url.log'
LOG_UPLOAD = BASE_LOG_PATH + 'upload.log'
# 日志输出目录   实际目录需要替换log.conf中的
LOG_OUTPUT = '/home/dlm/workspace/source/crawler_csdn_huaban/log/'

def get_now_file():
    return BASE_LOG_PATH + datetime.datetime.now().strftime("%Y%m%d")


"""
CSDN
"""
COUNT_FILENAME = BASE_LOG_PATH + 'blog_count.log'  # 存放计算的结果

CSDN_FILENAME = BASE_LOG_PATH + 'csdn_%s.log' % datetime.datetime.now().strftime("%Y%m%d")
CSDN_MONTH = BASE_LOG_PATH + 'month_count.log'
BLOG_NUM = 2000  # 最少刷的浏览量

COUNT_TIME = 10  # 每隔多少时间获取总的浏览量
MONTH_DAY = '17'

WRITE_CSDN_LOG = True

CSDN_URL = 'http://blog.csdn.net/qq_21178933/article/list/'
CSDN_BASE = 'http://blog.csdn.net'

"""
draw
"""
IMG_WIDTH = 120

IMG_HEIGHT = 60

DPI = 48  # 像素

COLUMN_WIDTH = 1

TITLE = u'CSDN博客详情'

X_TITLE = u'日期'

Y_TITLE = u'数量'

FONT_PATH = '%s/crawler/font/%s' % (PROJECT_PATH, 'JDJLS.TTF')

PV_LABEL = '浏览量'

RANK_LABEL = '排名'

POINTS_LABEL = '积分'

OPACITY = 0.3

BAR_WIDTH = 0.7
SHOW_TEXT = True
TEXT_TICK_DEFAULT_COLOR = False
X_TICK_DEFAULT_COLOR = False

MAX_SIZE = 20

"""
huaban
"""
ACCOUNT = "1192297699@qq.com"
PASSWORD = "**********"
COOKIES_FILENAME = BASE_LOG_PATH + 'cookies'  # 用户登陆的cookie
BOARD = 'statistic'
MONTH_BORD = 'statistic_month'

"""
E-mail 邮件通知模块
"""
EMAIL_ACTIVE = True
SENDER = '1192297699@qq.com'
From = '%s<%s>' % (AUTHOR, SENDER)
RECEIVERS = ['1903795237@qq.com']
ADMIN_RECEIVERS = ['1903795237@qq.com']
SUBJECT = 'CSDN邮件通知统计发送'
SMT_SERVER = 'smtp.qq.com'
USERNAME = '1192297699@qq.com'
PASSWORD='**********'
#PASSWORD = '**********'
TEST_URL = 'http://huaban.com/pins/1485863182/'
