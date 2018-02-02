# coding=u8
import os
import time

import datetime

from crawler.huaban.auth import get_user, login_set_cookies
from crawler.huaban.lib import get, search, json_parse, post, recreate, write_log, write_url_log
from emails.email_send import notice_admin, notice_result
from utils import COOKIES_FILENAME, get_now_file, BASE_IMG_PATH, MONTH_BORD

cookies = {}
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 '
                  'Safari/537.36'}


def set_cookies(cookies_str):
    if not cookies_str:
        cookies_str = login_set_cookies()
    global cookies
    cookies = {"cookies_are": cookies_str}


def upload(filepath, board_title, pinname=None, tname=None):
    filename = os.path.basename(filepath)
    pinname = pinname if pinname else filename
    url = "http://huaban.com/upload/"
    image = open(filepath, 'rb')
    files = {
        'Content-Disposition: form-data; name="title"': ''
        , 'Content-Disposition: form-data; name="upload1"; filename="' + filename + '" Content-Type: image/jpeg': image
    }
    msg = ''
    res = post(url, files=files, cookies=cookies, headers=headers)  # 上传图片到花瓣服务器
    file_data = json_parse(res.text)
    file_error_name = '%s.log' % get_now_file()
    if not file_data:
        msg = u'[{}] 上传失败: "{}" 上传请求未返回id, 存储的日至的文件名为：{}'.format(time.asctime()[11:19], filename, file_error_name)
        write_log(msg)
        write_log(u'{}'.format(res.text), filename=file_error_name)
        notice_admin(msg)
        return False
    file_id = file_data["id"]
    user = get_user(cookies)
    board_titles = []
    for dic in user["boards"]:
        board_titles.append(dic["title"])
    if board_title in board_titles:
        board_id = user["boards"][board_titles.index(board_title)]["board_id"]
    else:
        msg = u'[{}] 上传失败: 画板名 "{}" 不存在，请先建立画板'.format(time.asctime()[11:19], board_title)
        write_log(msg)
        notice_admin(msg)
        return False
    data = {
        "board_id": board_id
        , "text": pinname
        , "copy": "true"
        , "file_id": file_id
        , "via": 1
        , "share_button": 0
    }
    url = "http://huaban.com/pins/"
    res = post(url, data=data, cookies=cookies, headers=headers)  # 添加图片文件到画板

    if '<i class="error">' in res.text:
        msg = u'[{}] 上传失败: 图片 "{}" 已经被采集超过5次，准备处理图片后重试...'.format(time.asctime()[11:19], filename)
        write_log(msg)
        recreate(filepath)
        notice_admin(msg)
        return upload(filepath, board_title, pinname, tname)
    elif json_parse(res.text) is not None:
        data = json_parse(res.text)
        pin = data.get('pin') if data.get('pin') else dict()
        img_url = url + str(pin.get('pin_id'))
        write_url_log('%s \'%s\' %s \'%s\'' % (
        str(pin.get('user_id')), url + str(pin.get('pin_id')), pin.get('board_id'), pin.get('raw_meta')))
        msg = u'[{}] 上传成功: 图片 "{}" 到画板 "{}" 返回的数据是"{}"'.format(time.asctime()[11:19], filename, board_title, data)
        write_log(msg)
        notice_result(img_url=img_url)
        return True
    else:
        msg = u'[{}] 上传失败: 图片 "{}", 原因不明'.format(time.asctime()[11:19], filename)
        write_log(msg)
        notice_admin(msg)
        return False


def get_user_board():
    """获取用户画板"""
    url = "http://huaban.com/"
    res = get(url, cookies=cookies, headers=headers)  # 获取主页
    req_json = search('app\["req"\] = ({.+?});', res.text)
    return json_parse(req_json)


def upload_img(file_path, file_desc, board_title):
    """上传图片到花瓣中"""
    try:
        cookies_str = open(COOKIES_FILENAME).readlines()[-1]
    except Exception as e:
        cookies_str = ''
    cookies_str = str(cookies_str).replace('\n', '')
    set_cookies(cookies_str)
    upload(file_path, board_title, file_desc)


if __name__ == '__main__':
    upload_img(BASE_IMG_PATH + 'statistic20180125160623.png', 'ok', MONTH_BORD)
