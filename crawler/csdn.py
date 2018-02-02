# -*- coding: utf-8 -*-
import datetime
import http
import http.cookiejar
import os
import random
import threading
import time
import urllib.parse
import urllib.request
from queue import Queue

from bs4 import BeautifulSoup

from crawler.draw_img import draw_all, get_pic_name, get_day
from crawler.huaban.lib import write_pic_log, write_log
from crawler.huaban.upload import upload_img
from utils import COUNT_FILENAME, CSDN_FILENAME, BLOG_NUM, COUNT_TIME, DATE_FORMATE, BOARD, MONTH_DAY, \
    MONTH_BORD, BASE_IMG_PATH, WRITE_CSDN_LOG, CSDN_URL, CSDN_BASE

FLAG = True
queue = Queue(maxsize=10)
is_stop = False


def get_cur_request():
    """设置头部"""
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-Agent',
                          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/41.0.2272.101 Safari/537.36'),
                         ('Cookie', '4564564564564564565646540')]

    return urllib.request


def get_header():
    return {
        'User-Agent': r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      r'Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3',
        'Referer': r'http://www.lagou.com/zhaopin/Python/?labelWords=label',
        'Connection': 'keep-alive'
    }


def get_html(url):
    """获取url"""
    req = urllib.request.Request(url=url, headers=get_header())
    html_bytes = urllib.request.urlopen(req).read()
    return html_bytes.decode('utf-8')


def get_data(html):
    """获取数据"""
    try:
        soup = BeautifulSoup(html, "html.parser")
        main = soup.find('main')
        title = main.select('.csdn_top')
        title = title[0].string if title else ''
        number = main.find('article').select('.article_bar')[0].select('.right_bar')[0].find('li').find('span').string
        return title, number
    except Exception as e:
        return None


def get_article_urls(url, csdn_base):
    """"""
    html_bytes = get_html(url)
    blogs = list()
    try:
        soup = BeautifulSoup(html_bytes, "html.parser")
        main = soup.find('main')
        blog_detail = main.select('.blog-detail')[0]
        blog_units = blog_detail.select('.blog-units-box')[0].select('.blog-unit')

        for unit in blog_units:
            a = unit.a['href']
            if csdn_base in a:
                blogs.append(a)
            else:
                blogs.append(csdn_base + a)
        return blogs
    except Exception as e:
        return blogs


def get_page_urls(csdn_base, page_url, blog_urls):
    html_bytes = get_html(page_url)
    try:
        soup = BeautifulSoup(html_bytes, "html.parser")
        main = soup.find('main')
        page_links = main.select('.pagination-wrapper')[0].select('.page-link')
        page_link = page_links[len(page_links) - 2]
        num = page_link.string if page_link else 1
        blogs = list()
        for i in range(1, int(num) + 1):
            blogs.extend(get_article_urls(page_url + str(i), csdn_base))
    except Exception as e:
        pass
    blog_urls.extend(blogs)
    return blogs


def get_all_count(page_url):
    """page页面"""
    global FLAG
    first = False
    total_num = 0
    id = 0
    file = COUNT_FILENAME
    if not os.path.exists(file):
        first = True
        with open(file, 'a+')as f:
            f.write('id num rank points date\n')
    else:
        with open(file)as f:
            try:
                lines = f.readlines()  # 读取所有行
                last_line = lines[-1]
                if not last_line:
                    first = True
                total_num = int(last_line.split(' ')[1])
                id = int(last_line.split(' ')[0])
            except Exception as e:
                first = True

    while FLAG:
        time.sleep(COUNT_TIME)
        try:
            html_bytes = get_html(page_url)
            soup = BeautifulSoup(html_bytes, "html.parser")
            grades = soup.find('aside').select('.interflow ')[0].select('.gradeAndbadge')
            num = int(str(grades[0].select('.num')[0].string).replace(',', ''))
            rank = int(str(grades[2].select('.num')[0].string).replace(',' ''))
            points = int(str(grades[3].select('.num')[0].string).replace(',' ''))
            if first:
                total_num = num
                first = False
            if num - total_num > BLOG_NUM:
                FLAG = False
                with open(file, 'a+') as f:
                    f.write('%s %s %s %s \'%s\'\n' % (
                        id + 1, num, rank, points, datetime.datetime.now().strftime(DATE_FORMATE)))
        except Exception as e:
            FLAG = False


def get_cur_data():
    """获取数据"""
    file = CSDN_FILENAME
    first = False
    if not os.path.exists(file):
        first = True
    while FLAG or not queue.empty():
        url = queue.get()
        html_doc = get_html(url)
        title, number = get_data(html_doc)
        with open(file, 'a+') as f:
            if first:
                f.write('title number url date\n')
                first = False
            if WRITE_CSDN_LOG:
                f.write('\'%s\' %s \'%s\' \'%s\'\n' % (
                    title, number, url, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))


def add_url(urls):
    """添加链接"""
    num = len(urls)
    while FLAG:
        try:
            url = urls[random.randint(0, num)]
            queue.put(url)
        except Exception as e:
            pass


def multi_exe():
    blog_urls = list()
    get_page_urls(CSDN_BASE, CSDN_URL, blog_urls)
    t1 = threading.Thread(target=get_all_count, args=(CSDN_URL,))
    t3 = threading.Thread(target=add_url, args=(blog_urls,))
    t2 = threading.Thread(target=get_cur_data, args=( ))
    t1.start()
    t2.start()
    t3.start()
    while t1.is_alive() or t2.is_alive() or t3.is_alive():
        pass
    pic_name, file_desc = get_pic_name()
    try:
        draw_all(BASE_IMG_PATH + pic_name)
        if get_day() == MONTH_DAY:
            pic_name, file_desc = get_pic_name()
            draw_all(BASE_IMG_PATH + pic_name)
            write_pic_log('%s%s' % (BASE_IMG_PATH, pic_name))
            upload_img(BASE_IMG_PATH + pic_name, file_desc, MONTH_BORD)
        write_pic_log('%s%s' % (BASE_IMG_PATH, pic_name))
        upload_img(BASE_IMG_PATH + pic_name, file_desc, BOARD)
    except Exception as e:
        write_log(e)


if __name__ == '__main__':
    multi_exe()
