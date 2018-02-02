# -*- coding: utf-8 -*-
import datetime
import os

import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties
from utils import COUNT_FILENAME, IMG_WIDTH, X_TITLE, FONT_PATH, RANK_LABEL, \
    PV_LABEL, POINTS_LABEL, OPACITY, BAR_WIDTH, SHOW_TEXT, IMG_HEIGHT, DPI, X_TICK_DEFAULT_COLOR, \
    TEXT_TICK_DEFAULT_COLOR, AUTHOR, MONTH_DAY, MAX_SIZE, TEST_URL, PROJECT_PATH, BASE_IMG_PATH


def get_font(size=14):
    font = None
    try:
        font = FontProperties(fname=FONT_PATH, size=size)
    except Exception as e:
        pass
    return font


def get_date(filename):
    """获取文件中的数据"""
    with open(filename) as f:
        data_list = f.readlines()[1:]
    return data_list


def get_month_data(counts):
    """获取每年月初的日期"""
    this_counts = counts
    counts = get_detail_count(counts)
    dates = counts.get('date')
    index_list = list()
    for i in range(len(dates)):
        date = dates[i]
        day = datetime.datetime.strptime(str(date).replace('.', '-'), '%Y-%m-%d').day
        if str(day) == str(MONTH_DAY):
            index_list.append(i)
    cur_counts = list()
    for j in range(len(index_list)):
        cur_counts.append(this_counts[index_list[j]])
    return cur_counts


def get_detail_count(counts):
    """分别获取浏览量 积分 排名"""
    pv = list(map(lambda x: x.split(' ')[1], counts))
    rank = list(map(lambda x: x.split(' ')[2], counts))
    points = list(map(lambda x: x.split(' ')[3], counts))
    length = len(pv)
    date = list()
    for val in counts:
        date_str = val.split(' ')[4]
        date_str = str(date_str).replace('\'', '').replace('\n', '')
        cur_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y.%m.%d')
        date.append(cur_date)
    if length > MAX_SIZE:
        pv = pv[length - MAX_SIZE - 1: length - 1]
        rank = rank[length - MAX_SIZE - 1: length - 1]
        points = points[length - MAX_SIZE - 1: length - 1]
        date = date[length - MAX_SIZE - 1: length - 1]

    return {'pv': pv, 'rank': rank, 'points': points, 'date': date}


def x_tick(x_list):
    return list(map(lambda x: str(x.replace('.', '.\n')), x_list))


def draw_rect(detail, title, ax, font, type, color):
    """画条形图"""
    length = len(detail.get(type))
    index = np.arange(length)
    rect1 = ax.bar(index, detail.get(type), BAR_WIDTH, alpha=OPACITY, color=color)
    if SHOW_TEXT:
        auto_label(rect1, ax, detail.get(type), color=color)
    font.set_size(80)
    plt.xlabel(X_TITLE, fontproperties=font)
    plt.ylabel(title, fontproperties=font)
    plt.title(title + '%s' % '统计', fontproperties=font)
    if not X_TICK_DEFAULT_COLOR:
        color = 'k'
    plt.xticks(index - 0.4 + 0.5 * BAR_WIDTH, x_tick(detail.get('date')), fontsize=35, color=color)
    plt.yticks(fontsize=30)


def draw_line(detail, title, ax, font, type, color):
    x = detail.get('date')
    y = detail.get(type)
    plt.plot(x, y, marker='*', mec='r', mfc='w', color=color)
    font.set_size(80)
    plt.xlabel(X_TITLE, fontproperties=font)
    plt.ylabel(title, fontproperties=font)
    plt.title(title + '%s' % '统计', fontproperties=font)
    length = len(detail.get(type))
    index = np.arange(length)
    if not X_TICK_DEFAULT_COLOR:
        color = 'k'
    plt.xticks(index - 0.4 + 0.5 * BAR_WIDTH, x_tick(detail.get('date')), fontsize=35, color=color)
    plt.yticks(fontsize=30)


def get_day():
    return datetime.datetime.now().strftime('%d')


def draw_all(file_path):
    """
    画图
    color：  b: blue g: green  r: red c: cyan m: magenta  y: yellow k: black w: white
    """
    flag = False
    counts = get_date(COUNT_FILENAME)
    if get_day() == MONTH_DAY:
        counts = get_month_data(counts)
        flag = True
    detail = get_detail_count(counts)
    font = get_font(20)
    try:
        fig = plt.figure(figsize=(IMG_WIDTH, IMG_HEIGHT), dpi=DPI)
    except Exception as e:
        pass
    ax = fig.add_subplot(231)
    draw_rect(detail, PV_LABEL, ax, font, 'pv', 'r')
    ax = fig.add_subplot(232)
    draw_rect(detail, RANK_LABEL, ax, font, 'rank', 'k')
    ax = fig.add_subplot(233)
    draw_rect(detail, POINTS_LABEL, ax, font, 'points', 'm')
    ax = fig.add_subplot(234)
    draw_line(detail, PV_LABEL, ax, font, 'pv', 'r')
    ax = fig.add_subplot(235)
    draw_line(detail, RANK_LABEL, ax, font, 'rank', 'k')
    ax = fig.add_subplot(236)
    draw_line(detail, POINTS_LABEL, ax, font, 'points', 'm')
    plt.savefig(file_path)
    plt.close()
    return flag


def auto_label(rects, ax, msg, color):
    i = 0
    for rect in rects:
        h = rect.get_height()
        if not TEXT_TICK_DEFAULT_COLOR:
            color = 'k'
        ax.text(rect.get_x() + rect.get_width() / 2., 1 * h, '%s' % msg[i],
                ha='center', va='bottom', color=color, fontsize=35)
        i += 1


def get_pic_name():
    """csdn图片"""
    img_name = 'statistic%s.png' % datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    if not os.path.exists(BASE_IMG_PATH):
        os.makedirs(BASE_IMG_PATH)
    file_desc = '%s创建的统计图片:%s' % (datetime.datetime.now().strftime('%Y年%m月%d日%H时%M分%S'), AUTHOR)
    return img_name, file_desc


if __name__ == '__main__':
    file_name, desc = get_pic_name()
    draw_all(BASE_IMG_PATH + file_name)
# send_msg(file_name, TEST_URL)
