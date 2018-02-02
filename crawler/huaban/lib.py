# coding=u8
import datetime
import json
import random
import re

import os
import threading

import requests

from utils import DATE_FORMATE, LOG_IMG, LOG_UPLOAD, LOG_URL

lock = threading.Lock()

def search(pattern, text):
    # a better regex searcher
    results = re.search(pattern, text)
    i = 0
    result = None
    while True:
        try:
            result = results.group(i)
        except:
            break
        i = i + 1
    return result


def json_parse(string):
    # a better json parser
    string = re.sub('undefined', '"undefined"', string)  # json库不能识别undefined类型
    string = re.sub('null', '"null"', string)  # json库不能识别null类型
    try:
        data = json.loads(string)
        return data
    except ValueError:
        return None


def get(url, params="", cookies="", headers="", timeout=3, max_try=5):
    # GET with timeout & retry
    while max_try - 1 > 0:
        try:
            res = requests.get(url, params=params, cookies=cookies, headers=headers, timeout=timeout)
            return res
        except:
            max_try = max_try - 1
            write_log("HTTP/GET failed, Now retry ...\n")
            continue
    return requests.get(url, params=params, cookies=cookies, headers=headers, timeout=timeout)


def post(url, data="", files="", cookies="", headers="", timeout=3, max_try=5):
    # POST with timeout & retry
    while max_try - 1 > 0:
        try:
            res = requests.post(url, data=data, files=files, cookies=cookies, headers=headers)
            return res
        except Exception as e:
            max_try = max_try - 1
            write_log("HTTP/POST failed, Now retry ...\n")
            continue
    return requests.post(url, data=data, files=files, cookies=cookies, headers=headers)


def get_headers():
    return {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/55.0.2883.87 Safari/537.36'}


def decode(str):
    try:
        uni = str.decode('utf-8')
    except:
        uni = str.decode('gbk')
    return uni


def split_str(cookies_str):
    """将字符串分割为dict"""
    cookies = {}
    for line in cookies_str.split(';'):
        try:
            name, value = line.strip().split('=', 1)
            cookies[name] = value
        except Exception as e:
            cookies[line] = True
    return cookies


def recreate(img_path):
    with open(img_path, 'rb') as f1:
        bin = f1.read()
    bin = bytearray(bin)
    bin = bin[:-2] + str(random.randint(0, 9)) + str(random.randint(0, 9))
    with open(img_path, 'wb') as f2:
        f2.write(bin)


def write_log(str, filename=None):
    """log"""
    log = LOG_UPLOAD
    if filename:
        log = filename
    with open(log, 'a+') as f:
        cur_time = datetime.datetime.now().strftime(DATE_FORMATE)
        f.write(str+' \'%s\'\n' % cur_time)


def write_url_log(str):
    """log"""
    log = LOG_URL
    with open(log, 'a+') as f:
        cur_time = datetime.datetime.now().strftime(DATE_FORMATE)
        f.write(str + ' \'%s\'\n' % cur_time)


def write_pic_log(str):
    """log"""
    log = LOG_IMG
    with open(log, 'a+') as f:
        cur_time = datetime.datetime.now().strftime(DATE_FORMATE)
        f.write(str + ' \'%s\'\n' % cur_time)


def write_data(filename, title=None, values=None):
    """"""
    txt = values if values else ''
    if title is not None:
        txt = title + txt
    with open(filename, 'a+') as f:
        lines = f.readlines()  # 读取所有行
        if len(lines) == 0:
            f.write(txt)

