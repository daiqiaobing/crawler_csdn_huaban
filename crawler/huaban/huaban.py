# -*- coding: utf-8 -*-
import os
import requests
import time

from blog_log import SysLog
from crawler.huaban.lib import get, search, json_parse, post, recreate
from utils import ACCOUNT, PASSWORD, COOKIES_FILENAME, BASE_IMG_PATH, MONTH_BORD

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/55.0.2883.87 Safari/537.36'}


class Auth(SysLog):
    def __init__(self):
        SysLog.__init__(self)
        self.cookies = {"cookies_are": ''}

    def get_cookie(self, account, password):
        url = "https://huaban.com/auth/"
        data = {"email": account, "password": password, "_ref": "frame"}
        # 查看有无cacert证书
        verify = './cacert.pem'
        if not os.path.exists(verify) or not os.path.isfile(verify):
            verify = True
        res = requests.post(url, data=data, headers=headers, verify=verify)
        if u'{"error":["用户不存在"]}' in res.text:
            self.error_msg(u'登录失败，账号不存在')
            return ''
        if u'{"error":["用户密码错误"]}' in res.text:
            msg = u'登录失败，密码错误'
            self.error_msg(msg)
            return ''
        if u'登录频率过快' in res.text:
            msg = u'登录频率过快，登录被阻断。请在浏览器中登录一次后再尝试'
            self.error_msg(msg)
            return ''
        if 'Set-Cookie' in res.headers:
            cookies = res.headers['Set-Cookie']
        elif 'set-cookie' in res.headers:
            cookies = res.headers['set-cookie']
        else:
            msg = u'登录失败，未知原因'
            self.error_msg(msg)
            cookies = ''
        return cookies

    def get_user(self, cookies):
        """获取用户画板"""
        url = "http://huaban.com/"
        res = get(url, cookies=cookies, headers=headers)  # 获取主页
        user_json = search('app\["req"\] = ({.+?});', res.text)
        if user_json:
            req = json_parse(user_json)
            if req["user"] == "null":
                self.error_msg(u"未成功获取用户主页信息")
                exit()
            req_user = req["user"]
            url = url + req_user["urlname"]
            res = get(url, cookies=cookies, headers=headers)  # 获取画板页
            user_json = search('app.page\["user"\] = ({.+?});', res.text)
            if user_json:
                user = json_parse(user_json)
                return user
        return json_parse(user_json)

    def login_set_cookies(self, account=ACCOUNT, password=PASSWORD):
        cur_cookies = self.get_cookie(account, password)
        if not cur_cookies:
            raise Exception
        with open(COOKIES_FILENAME, 'a+') as f:
            f.write(cur_cookies + '\n')
        self.cookies = {"cookies_are": cur_cookies}

    def set_cookies(self, fresh_cookies=False):
        try:
            cookies_str = open(COOKIES_FILENAME).readlines()[-1]
        except Exception as e:
            cookies_str = ''
        if not cookies_str or fresh_cookies:
            self.login_set_cookies()
        else:
            self.cookies = {"cookies_are": cookies_str.replace('\n', '')}


class HuaBan(Auth):
    def __init__(self):
        Auth.__init__(self)
        self.set_cookies()

    def get_user_board(self, cookies):
        """获取用户画板"""
        url = "http://huaban.com/"
        res = get(url, cookies=cookies, headers=headers)  # 获取主页
        req_json = search('app\["req"\] = ({.+?});', res.text)
        return json_parse(req_json)

    def upload(self, file_path, board_title, pinname=None, tname=None):
        filename = os.path.basename(file_path)
        pinname = pinname if pinname else filename
        url = "http://huaban.com/upload/"
        image = open(file_path, 'rb')
        files = {'Content-Disposition: form-data; name="title"': '',
                 'Content-Disposition: form-data; name="upload1"; filename="' + filename + '" Content-Type: image/jpeg': image
                 }
        res = post(url, files=files, cookies=self.cookies, headers=headers)  # 上传图片到花瓣服务器
        file_data = json_parse(res.text)
        if not file_data:
            msg = u' 上传失败: "{}" 上传请求未返回id, 存储的日至的文件名为：{}'.format(filename)
            self.error_msg(msg)
            return False
        file_id = file_data["id"]
        user = self.get_user(self.cookies)
        board_titles = []
        for dic in user["boards"]:
            board_titles.append(dic["title"])
        if board_title in board_titles:
            board_id = user["boards"][board_titles.index(board_title)]["board_id"]
        else:
            msg = u'[{}] 上传失败: 画板名 "{}" 不存在，请先建立画板'.format(time.asctime()[11:19], board_title)
            self.error_msg(msg)
            return False
        data = {"board_id": board_id, "text": pinname, "copy": "true", "file_id": file_id, "via": 1, "share_button": 0}
        url = "http://huaban.com/pins/"
        res = post(url, data=data, cookies=self.cookies, headers=headers)  # 添加图片文件到画板

        if '<i class="error">' in res.text:
            msg = u'[{}] 上传失败: 图片 "{}" 已经被采集超过5次，准备处理图片后重试...'.format(time.asctime()[11:19], filename)
            self.error_msg(msg)
            recreate(file_path)
            return self.upload(file_path, board_title, pinname, tname)
        elif json_parse(res.text) is not None:
            data = json_parse(res.text)
            pin = data.get('pin') if data.get('pin') else dict()
            img_url = url + str(pin.get('pin_id'))
            msg = '%s \'%s\' %s \'%s\'' % (
                str(pin.get('user_id')), url + str(pin.get('pin_id')), pin.get('board_id'), pin.get('raw_meta'))
            self.msg(msg)
            msg = u'上传成功: 图片 "{}" 到画板 "{}" 返回的数据是"{}"'.format(filename, board_title, data)
            self.msg(msg)
            self.email_msg(msg)
            # notice_result(img_url=img_url)
            return True
        else:
            msg = u'[{}] 上传失败: 图片 "{}", 原因不明'.format(time.asctime()[11:19], filename)
            self.error_msg(msg)
            return False


if __name__ == '__main__':
    HuaBan().upload(BASE_IMG_PATH + 'statistic20180125232528.png', 'ok', MONTH_BORD)