# -*- coding: utf-8 -*-

import os

import requests

from crawler.huaban.lib import get, search, json_parse, write_log
from emails.email_send import notice_admin
from utils import ACCOUNT, PASSWORD, COOKIES_FILENAME

headers = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}


def get_cookie(account, password):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/55.0.2883.87 Safari/537.36'}
    url = "https://huaban.com/auth/"
    data = {"email": account, "password": password, "_ref": "frame"}
    msg = ''
    # 查看有无cacert证书
    verify = './cacert.pem'
    if not os.path.exists(verify) or not os.path.isfile(verify):
        verify = True
    res = requests.post(url, data=data, headers=headers, verify=verify)
    if u'{"error":["用户不存在"]}' in res.text:
        msg = u'登录失败，账号不存在'
        write_log(msg)
        notice_admin(msg)
        return
    if u'{"error":["用户密码错误"]}' in res.text:
        msg = u'登录失败，密码错误'
        write_log(msg)
        notice_admin(msg)
        return
    if u'登录频率过快' in res.text:
        msg = u'登录频率过快，登录被阻断。请在浏览器中登录一次后再尝试'
        write_log(msg)
        notice_admin(msg)
        return
    if 'Set-Cookie' in res.headers:
        cookies = res.headers['Set-Cookie']
    elif 'set-cookie' in res.headers:
        cookies = res.headers['set-cookie']
    else:
        msg = u'登录失败，未知原因'
        write_log(msg)
        write_log(res.text)
        notice_admin(msg)
        cookies = ''
    return cookies


def get_user(cookies):
    """获取用户画板"""
    url = "http://huaban.com/"
    res = get(url, cookies=cookies, headers=headers)  # 获取主页
    user_json = search('app\["req"\] = ({.+?});', res.text)
    if user_json:
        req = json_parse(user_json)
        if req["user"] == "null":
            msg = u"未成功获取用户主页信息"
            write_log(msg)
            notice_admin(msg)
            exit()
        req_user = req["user"]
        url = url + req_user["urlname"]
        res = get(url, cookies=cookies, headers=headers)  # 获取画板页
        user_json = search('app.page\["user"\] = ({.+?});', res.text)
        # write_log(u"成功读取用户画板信息")
        if user_json:
            user = json_parse(user_json)
            return user
    return json_parse(user_json)


def login_set_cookies():
    cookies = get_cookie(ACCOUNT, PASSWORD)
    with open(COOKIES_FILENAME, 'a+') as f:
        f.write(cookies+'\n')
    return cookies

