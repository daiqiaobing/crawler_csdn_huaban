# -*- coding: utf-8 -*-
import random
import threading
import urllib
import urllib.request

from queue import Queue
import time
from bs4 import BeautifulSoup

from blog_log import TimeLog
from utils import CSDN_BASE, CSDN_URL, COUNT_FILENAME, WRITE_CSDN_LOG


class BlogQueue:
    __url_queue = None

    def __init__(self, max_size=20):
        self.__url_queue = Queue(maxsize=max_size)

    def add_url(self, url):
        self.__url_queue.put(url)

    def get_url(self):
        return self.__url_queue.get()

    def empty(self):
        return self.__url_queue.empty()


class BlogBase(TimeLog):
    """

    """

    def __init__(self):
        super(BlogBase, self).__init__()

    def get_header(self):
        return {'User-Agent': r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              r'Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3',
                'Referer': r'http://www.lagou.com/zhaopin/Python/?labelWords=label',
                'Connection': 'keep-alive'}

    def get_html(self, url, decode='utf-8'):
        req = urllib.request.Request(url=url, headers=self.get_header())
        html_bytes = urllib.request.urlopen(req).read()
        return html_bytes.decode(decode)

    def get_page_urls(self, url, blog_base):
        """
        :param url: example: 'http://blog.csdn.net/qq_21178933/article/list/2'
        :param blog_base: example: 'http://blog.csdn.net'
        :return:
        """
        html_bytes = self.get_html(url)
        blog_urls = list()
        try:
            soup = BeautifulSoup(html_bytes, "html.parser")
            main = soup.find('main')
            blog_detail = main.select('.blog-detail')[0]
            blog_units = blog_detail.select('.blog-units-box')[0].select('.blog-unit')

            for unit in blog_units:
                a = unit.a['href']
                if blog_base in a:
                    blog_urls.append(a)
                else:
                    blog_urls.append(blog_base + a)
        except Exception as e:
            self.error_msg(e)
        return blog_urls

    def get_pages_urls(self, blog_base, page_url):
        """
        :param blog_base: blog  example: 'http://blog.csdn.net'
        :param page_url: example: 'http://blog.csdn.net/qq_21178933/article/list/'
        :return:
        """
        html_bytes = self.get_html(page_url)
        try:
            soup = BeautifulSoup(html_bytes, "html.parser")
            main = soup.find('main')
            page_links = main.select('.pagination-wrapper')[0].select('.page-link')
            page_link = page_links[len(page_links) - 2]
            num = page_link.string if page_link else 1
            blog_uls = list()
            for i in range(1, int(num) + 1):
                blog_uls.extend(self.get_page_urls(page_url + str(i), blog_base))
        except Exception as e:
            self.error_msg(e)
        return blog_uls

    def last_blog_info(self):
        """
        上次刷博客的信息
        :return:
        """
        blog_id = 1
        total = 0
        with open(COUNT_FILENAME)as f:
            try:
                lines = f.readlines()  # 读取所有行
                last_line = lines[-1]
                total = int(last_line.split('-')[1])
                blog_id = int(last_line.split('-')[0])
            except Exception as e:
                self.error_msg(e)
        return blog_id, total

    def blog_article_info(self, html):
        """获取数据"""
        title = ''
        number = 0
        try:
            soup = BeautifulSoup(html, "html.parser")
            main = soup.find('main')
            title = main.select('.csdn_top')
            title = title[0].string if title else ''
            number = main.find('article').select('.article_bar')[0].select('.right_bar')[0].find('li').find(
                'span').string
        except Exception as e:
            self.error_msg(e)
        return title, number


class Blog(BlogBase):
    """
    blog
    """
    # 利用该队列判断是否已经结束
    __is_finish = False
    __sleep_time = 10
    __url_queue = None
    __blog_urls = list()
    __blog_num = list()
    __lock = threading.Lock()

    def __init__(self, queue, sleep_time=10, blog_num=1000):
        self.__url_queue = queue
        self.__sleep_time = sleep_time
        self.__blog_urls = self.get_pages_urls(CSDN_BASE, CSDN_URL)
        self.__blog_num = blog_num
        super(Blog, self).__init__()

    def add_url_task(self):
        """
        :return:
        """
        num = len(self.__blog_urls)
        while not self.__is_finish:
            try:
                self.__url_queue.add_url(self.__blog_urls[random.randint(0, num - 1)])
            except Exception as e:
                self.error_msg(e)

    def compare_number_task(self, page_url):
        """
        比较blog的浏览量是否达到标准
        :param page_url:
        :return:
        """
        blog_id, total = self.last_blog_info()
        while not self.__is_finish:
            time.sleep(self.__sleep_time)
            try:
                html_bytes = self.get_html(page_url)
                soup = BeautifulSoup(html_bytes, "html.parser")
                grades = soup.find('aside').select('.interflow ')[0].select('.gradeAndbadge')
                num = int(str(grades[2].attrs.get('title', 0)).replace(',', ''))
                rank = int(str(grades[3].attrs.get('title', 0)).replace(',', ''))
                points = int(str(grades[4].attrs.get('title', 0)).replace(',', ''))
                if total == 0:
                    total = num
                if num - total > self.__blog_num:
                    values = '%s - %s - %s - %s' % (blog_id + 1, num, rank, points)
                    self.count_msg(values)
                    self.__lock.acquire()
                    self.__is_finish = True
                    self.__lock.release()
            except Exception as e:
                self.__lock.acquire()
                self.__is_finish = True
                self.__lock.release()
                self.error_msg(e)

    def blog_refresh_task(self):
        """获取数据"""
        while not self.__is_finish or not self.__url_queue.empty():
            url = self.__url_queue.get_url()
            html_doc = self.get_html(url)
            if WRITE_CSDN_LOG:
                title, number = self.blog_article_info(html_doc)
                values = '\'%s\' %s \'%s\'' % (title, number, url)
                self.csdn_msg(values)

    def exe_task(self, task_num):
        """"""
        url_task = threading.Thread(target=self.add_url_task, name=u'添加url的链接')
        url_task.start()
        for i in range(task_num):
            refresh_task = threading.Thread(target=self.blog_refresh_task, name=u'刷新博客%s' % i)
            refresh_task.start()
        compare_task = threading.Thread(target=self.compare_number_task, name=u'刷新博客', args=(CSDN_URL,))
        compare_task.start()


if __name__ == '__main__':
    queue = BlogQueue()
    blog = Blog(queue=queue, blog_num=2, sleep_time=2, )
    blog.exe_task(5)
