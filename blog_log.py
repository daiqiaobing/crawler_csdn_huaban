# -*- coding: utf-8 -*-
import logging.config
import logging.handlers
import time

from utils import PROJECT_PATH, BASE_LOG_PATH


class SysLog(object):
    """
    系统日志
    """

    def __init__(self, count_name='countInfo', error_name='crawlerError', cookies_name='cookiesInfo',
                 info_name='crawlerInfo', email_name='emailInfo'):
        logging.config.fileConfig(PROJECT_PATH + '/log.conf')
        self.count_log = logging.getLogger(count_name)
        self.error_log = logging.getLogger(error_name)
        self.cookies_log = logging.getLogger(cookies_name)
        self.info_log = logging.getLogger(info_name)
        self.success_log = logging.getLogger(email_name)

    def count_msg(self, msg):
        self.count_log.info(msg)

    def error_msg(self, msg):
        self.error_log.error(msg)

    def cookies_msg(self, msg):
        self.cookies_log.info(msg=msg)

    def msg(self, msg):
        self.info_log.info(msg=msg)

    def email_msg(self, msg):
        self.success_log.info(msg)


rq = time.strftime('%Y%m%d', time.localtime(time.time()))


class TimeLog(SysLog):
    """
    日志类
    """

    def __init__(self, name='csdn'):
        super(TimeLog, self).__init__()
        self.path = BASE_LOG_PATH  # 定义日志存放路径
        self.filename = self.path + 'csdn_' + rq + '.log'  # 日志文件名称
        self.name = name  # 为%(name)s赋值
        self.logger = logging.getLogger(self.name)
        # 控制日志文件中记录级别
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s  %(message)s')
        file_handler = logging.FileHandler(self.filename)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def csdn_msg(self, msg):
        self.logger.info(msg=msg)


if __name__ == '__main__':
    timeLog = TimeLog()
    timeLog.cookies_msg('999999999')
