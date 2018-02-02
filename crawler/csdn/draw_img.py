# -*- coding: utf-8 -*-
import datetime
import os
import matplotlib
import re

from blog_log import SysLog

matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties
from utils import COUNT_FILENAME, IMG_WIDTH, X_TITLE, FONT_PATH, RANK_LABEL, \
    PV_LABEL, POINTS_LABEL, OPACITY, BAR_WIDTH, SHOW_TEXT, IMG_HEIGHT, DPI, BASE_IMG_PATH, AUTHOR


class ImgBase(SysLog):
    def __init__(self, font_path=FONT_PATH, font_size=14):
        super(ImgBase, self)
        self.__font = FontProperties(fname=font_path, size=font_size)
        self.font_path = font_path

    def get_font(self, font_size=14):
        self.__font.set_size(font_size)
        return self.__font

    def set_font(self, size):
        self.__font.set_size(size)

    def date_tick(self, date_list, f_format='-', t_format='.\n'):
        return list(map(lambda x: str(x.replace(f_format, t_format)), date_list))

    def __draw_label(self, draws, ax, data, color='k', font_size=35):

        for i in range(len(draws)):
            h = draws[i].get_height()
            ax.text(draws[i].get_x() + draws[i].get_width() / 2., 1 * h, '%s' % data[i], ha='center', va='bottom',
                    color=color, fontsize=font_size)

    def draw_rect(self, ax, title, data_type, data, color='k', width=BAR_WIDTH, alpha=OPACITY, label=SHOW_TEXT,
                  x_label=X_TITLE):
        index = np.arange(len(data.get('date')))
        rect = ax.bar(index, data.get(data_type), linewidth=width, alpha=alpha, color=color)
        if label:
            self.__draw_label(rect, ax, data.get(data_type), color)
        self.set_font(80)
        plt.ylabel(title, fontproperties=self.__font)
        plt.xlabel(x_label, fontproperties=self.__font)
        plt.xticks(index - 0.4 + 0.5 * BAR_WIDTH, self.date_tick(data.get('date')), fontsize=35, color=color)
        plt.yticks(fontsize=30)

    def draw_line(self, title, data_type, data, color='k'):
        plt.plot(data.get('date'), data.get(data_type), marker='*', mec='r', mfc='w', color=color)
        self.set_font(80)
        plt.xlabel(X_TITLE, fontproperties=self.__font)
        plt.ylabel(title, fontproperties=self.__font)
        plt.title(title + '%s' % '统计', fontproperties=self.__font)
        index = np.arange(len(data.get(data_type)))
        plt.xticks(index - 0.4 + 0.5 * BAR_WIDTH, self.date_tick(data.get('date')), fontsize=35, color=color)
        plt.yticks(fontsize=30)


class DataDeal(SysLog):
    def __init__(self):
        super(DataDeal, self).__init__()
        self.data = {'num': list(), 'rank': list(), 'points': list(), 'date': list()}
        self.month_data = {'num': list(), 'rank': list(), 'points': list(), 'date': list()}

    def set_data(self, is_month=False, filename=COUNT_FILENAME, num_pos=1, rank_pos=2, points_pos=3, date_pos=4,
                 length=5, maxsize=20):
        with open(filename) as f:
            lines = f.readlines()[1:]
        for line in lines:
            data = line.split('-')
            if len(data) < length:
                self.error_msg('记录数据中的长度不匹配，错误在于%s文件中的数据，数据收集发生了错误' % filename)
                break
            blog_num = int(data[num_pos])
            rank = int(data[rank_pos])
            points = int(data[points_pos])
            m = re.search(r"(\d{4}[-|/|.]\d{1,2}[-|/|.]\d{1,2})", str(data[date_pos]))
            date = m.group(0)
            if is_month:
                self.insert_date(blog_num, rank, points, date, self.month_data)
                return
            else:
                self.insert_date(blog_num, rank, points, date, self.data)
        length = len(self.data.get('num', list()))
        if length > maxsize:
            self.data['num'] = self.data.get('num', list())[length - maxsize:]
            self.data['date'] = self.data.get('date', list())[length - maxsize:]
            self.data['rank'] = self.data.get('rank', list())[length - maxsize:]
            self.data['points'] = self.data.get('points', list())[length - maxsize:]

    def insert_date(self, blog_num, rank, points, date_time, data):
        """插入数据，根据日期排序，不插入重复日期的数据"""
        dates = data.get('date', list())
        date_format = '%Y-%m-%d'
        date = datetime.datetime.strptime(date_time.replace('/', '-'), date_format)

        for i in range(len(dates)):
            cur_date = datetime.datetime.strptime(dates[i], date_format)
            if cur_date > date:
                data.get('date').insert(i, date.strftime(date_format))
                data.get('num').insert(i, blog_num)
                data.get('rank').insert(i, rank)
                data.get('points').insert(i, points)
                return
            elif cur_date == date:
                return
        data.get('date').append(date.strftime(date_format))
        data.get('num').append(blog_num)
        data.get('rank').append(rank)
        data.get('points').append(points)

    def month_data(self, month_days=['01', '15']):
        cur_data = {'num': list(), 'rank': list(), 'points': list(), 'date': list()}
        date_format = '%Y-%m-%d'
        for data in self.month_data:
            dates = data.get('date', list())
            for i in dates:
                last_date = datetime.datetime.strptime(dates[i], date_format).strftime('%d')
                if last_date in month_days:
                    cur_data.get('date').append(self.month_data.get('date')[i])
                    cur_data.get('num').append(self.month_data.get('num')[i])
                    cur_data.get('rank').append(self.month_data.get('rank')[i])
                    cur_data.get('points').append(self.month_data.get('points')[i])
        self.month_data = cur_data


class DrawImg(ImgBase, DataDeal):
    """"""

    def __init__(self, month_day=['01', '15']):
        ImgBase.__init__(self)
        DataDeal.__init__(self)
        self.set_data(filename=COUNT_FILENAME)
        cur_day = datetime.datetime.today().strftime('%d')
        if cur_day in month_day:
            self.set_data(filename=COUNT_FILENAME, is_month=True)
            self.draw(self.month_data)

    def get_pic_name(self):
        """csdn图片"""
        img_name = 'statistic%s.png' % datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        if not os.path.exists(BASE_IMG_PATH):
            os.makedirs(BASE_IMG_PATH)
        file_desc = '%s创建的统计图片:%s' % (datetime.datetime.now().strftime('%Y年%m月%d日%H时%M分%S'), AUTHOR)
        return img_name, file_desc

    def draw(self, data=None):
        if not data:
            data = self.data
        fig = plt.figure(figsize=(IMG_WIDTH, IMG_HEIGHT), dpi=DPI)
        ax = fig.add_subplot(231)
        self.draw_rect(ax, PV_LABEL, 'num', data, color='r')
        ax = fig.add_subplot(232)
        self.draw_rect(ax, RANK_LABEL, 'rank', data, color='k')
        ax = fig.add_subplot(233)
        self.draw_rect(ax, POINTS_LABEL, 'points', data, color='m')
        ax = fig.add_subplot(234)
        self.draw_line(PV_LABEL, 'num', data, color='r')
        ax = fig.add_subplot(235)
        self.draw_line(RANK_LABEL, 'rank', data, color='k')
        ax = fig.add_subplot(236)
        self.draw_line(POINTS_LABEL, 'points', data, color='m')
        img_name, file_desc = self.get_pic_name()
        file_path = BASE_IMG_PATH + img_name
        plt.savefig(file_path)
        plt.close()
        return file_path


if __name__ == '__main__':
    draw = DrawImg()
    draw.draw()
