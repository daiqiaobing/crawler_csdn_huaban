# -*- coding: utf-8 -*-
import logging.config
import logging.handlers
import time

from utils import PROJECT_PATH, BASE_LOG_PATH


def get_logger(name='root'):
    log_path = PROJECT_PATH + '/log.conf'
    logging.config.fileConfig(log_path)
    return logging.getLogger(name=name)


rq = time.strftime('%Y%m%d', time.localtime(time.time()))


class TimeLog(object):
    """
    日志类
    """
    def __init__(self, name='log'):
        self.path = BASE_LOG_PATH  # 定义日志存放路径
        self.filename = self.path + '/csdn_' + rq + '.log'  # 日志文件名称
        self.name = name  # 为%(name)s赋值
        self.logger = logging.getLogger(self.name)
        # 控制日志文件中记录级别
        self.logger.setLevel(logging.INFO)
        # 控制输出到控制台日志格式、级别
        # self.ch = logging.StreamHandler()
        # gs = logging.Formatter('%(asctime)s - %(message)s')
        # self.ch.setFormatter(gs)
        # self.ch.setLevel(logging.NOTSET)    写这个的目的是为了能控制控制台的日志输出级别，但是实际中不生效，不知道为啥，留着待解决
        # 日志保留10天,一天保存一个文件
        self.fh = logging.handlers.RotatingFileHandler(self.filename, 'a')
        # 定义日志文件中格式
        self.formatter = logging.Formatter('%(asctime)s - %(message)s')
        self.fh.setFormatter(self.formatter)
        self.logger.addHandler(self.fh)
        # self.logger.addHandler(self.ch)

    def get_logger(self):
        return self.logger


if __name__ == '__main__':
    log = TimeLog('ok')
    log.get_logger().info('---------------')