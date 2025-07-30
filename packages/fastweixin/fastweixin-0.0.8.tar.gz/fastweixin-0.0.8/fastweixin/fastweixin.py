#!/usr/bin/env python3
# coding = utf8
"""
@ Author : ZeroSeeker
@ e-mail : zeroseeker@foxmail.com
@ GitHub : https://github.com/ZeroSeeker
@ Gitee : https://gitee.com/ZeroSeeker
"""
from lazysdk import lazyrequests
from lxml import etree
import requests
import hashlib
import json
import copy


default_headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "zh-CN,zh;q=0.9",
        "referer": "https://mp.weixin.qq.com/",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
        "x-requested-with": "XMLHttpRequest"
    }


def login_info(
        username: str,
        password: str,
        img_code: str = None,  # 验证码
        cookie: str = None
) -> json:
    """
    :param username: 登录账号名
    :param password: 登录密码
    :param img_code: 验证码
    :param cookie: 小饼干
    尝试使用帐号密码登录，返回尝试的结果，可能会有如下结果：
    正常
    有限封
    迁移完成
    迁移中
    迁移需重新提交
    永封
    诱导关注
    低俗色情
    """
    return_json = {}
    psw = hashlib.md5(password.encode("utf8")).hexdigest()
    url = 'https://mp.weixin.qq.com/cgi-bin/bizlogin?action=startlogin'
    values = {
        'username': username,
        'pwd': psw,
        'imgcode': img_code,
        'f': 'json',
        'userlang': 'userlang',
        'token': None,
        'lang': 'zh_CN',
        'ajax': 1
    }
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": "mp.weixin.qq.com",
        "Origin": "https://mp.weixin.qq.com",
        "Referer": "https://mp.weixin.qq.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
        "X-Requested-With": "XMLHttpRequest",
        "Cookie": cookie
    }
    temp_session = requests.session()
    response = temp_session.request(
        method='POST',
        url=url,
        headers=headers,
        data=values,
        timeout=5
    )
    response_json = response.json()
    return_json['response1'] = copy.deepcopy(response_json)
    base_resp = response_json.get('base_resp')
    if base_resp is not None:
        ret = base_resp.get('ret')
        err_msg = base_resp.get('err_msg')
        if ret == 200008:  # 需要输入验证码
            return_json.update({
                "account_password_correct": -1,
                "account_state": -1,
                "login_info": err_msg,
                "msg": "需要输入验证码"
            })

        if ret == 200023:  # 帐号/密码错误
            return_json.update({
                "account_password_correct": 0,
                "account_state": -1,
                "login_info": err_msg,
                "msg": "帐号/密码错误"
            })
        elif ret == 0:  # 帐号/密码正确
            return_json['password_correct'] = True
            redirect_url = "%s%s" % ('https://mp.weixin.qq.com', response_json.get('redirect_url'))
            redirect_url_json = "%s%s" % (redirect_url, '&f=json')
            response2 = temp_session.request(
                method='GET',
                url=redirect_url_json
            )
            response2_json = response2.json()
            return_json['response2'] = copy.deepcopy(response2_json)

            base_resp = response2_json.get('base_resp')
            ret2 = base_resp.get('ret')
            err_msg2 = base_resp.get('err_msg')

            account = response2_json.get('account')
            punish_id = response2_json.get('punish_id')
            illegal_type = response2_json.get('illegal_type')
            acct_transfer = response2_json.get('acct_transfer')

            if ret2 == 200007:
                return_json['account_state'] = 4
                return_json['msg'] = "帐号注销"
            elif ret2 == 200003:
                return_json['account_state'] = -2
                return_json['msg'] = err_msg2
            elif account is not None:
                return_json['account_state'] = 0
                return_json['msg'] = "帐号正常"
                response2_json.pop('base_resp')
                return_json.update(response2_json)
            elif punish_id == 0 and illegal_type is None:
                return_json['account_state'] = 1
                return_json['msg'] = "迁移需重新提交"
                response2_json.pop('base_resp')
                return_json.update(response2_json.pop('base_resp'))
                user_info = response2_json.get('user_info')
                if user_info is not None:
                    return_json.update(user_info)
            elif acct_transfer is not None:
                return_json['account_state'] = 1
                return_json['msg'] = "帐号迁移"
                response2_json.pop('base_resp')
                return_json.update(response2_json)

                acct_transfer = response2_json.get('acct_transfer')
                if acct_transfer is not None:
                    transfer_status = acct_transfer.get('transfer_status')
                    if transfer_status is not None:
                        return_json.update({
                            "transfer_status": acct_transfer.get('transfer_status'),
                        })
                    order_detail = acct_transfer.get('order_detail')
                    if order_detail is not None:
                        return_json.update(json.loads(order_detail))

                    invoice = acct_transfer.get('invoice')
                    if invoice is not None:
                        return_json.update(json.loads(invoice))

                user_info = response2_json.get('user_info')
                if user_info is not None:
                    return_json.update(user_info)
            else:
                return_json['account_state'] = 2
                return_json['msg'] = "帐号永封"
                response2_json.pop('base_resp')
                return_json.update(response2_json)
                user_info = response2_json.get('user_info')
                if user_info is not None:
                    return_json.update(user_info)

                new_infraction = response2_json.get('new_infraction')
                if new_infraction is not None:
                    try:
                        return_json.update(new_infraction[0])
                    except:
                        pass
    return return_json


def get_function_html_decode(
        url: str
):
    """
    获取文章页的 function htmlDecode(str) 脚本内容，以提取文章相关基础信息
    :param url:
    :return:

    user_name：公众号原始ID
    nickname： 公众号名称
    ct：发布时间
    msg_title：文章标题
    msg_source_url：原文链接地址
    """
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Connection": "keep-alive",
        "Host": "mp.weixin.qq.com",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/114.0"
    }
    response = requests.get(
        url=url,
        headers=headers
    )
    html = etree.HTML(response.content, etree.HTMLParser())
    scripts = html.xpath('/html/body/script/text()')
    data = dict()
    for script in scripts:
        if 'htmlDecode' in script:
            script_lines = script.split('\n')
            for script_line in script_lines:
                if script_line[:4] == 'var ':
                    this_line = script_line[4:-1]
                    if ' = ' in this_line:
                        this_line_split = this_line.split(' = ')
                        data_key = this_line_split[0]
                        data_value = this_line_split[1]
                        if data_value[:1] == '"' and data_value[-1:] == '"':
                            data_value = data_value[1:-1]
                        elif data_value[:1] == "'" and data_value[-1:] == "'":
                            data_value = data_value[1:-1]
                        else:
                            pass
                        data[data_key] = data_value
                    else:
                        pass
                else:
                    pass
        else:
            pass
    return data


def setting_page(
        token: str,
        cookie: str
):
    url = 'https://mp.weixin.qq.com/cgi-bin/settingpage?t=setting/index&action=index&lang=zh_CN&f=json&token=%s' % token
    headers = copy.deepcopy(default_headers)
    headers["cookie"] = cookie
    headers["referer"] = "https://mp.weixin.qq.com/cgi-bin/home?t=home/index&token=%s&lang=zh_CN" % token
    return lazyrequests.lazy_requests(
        method="GET",
        url=url,
        headers=headers
    )


def switch_acct(
        token: str,
        cookie: str,
        method: str = "GET",
        action: str = "get_acct_list",
):
    url = 'https://mp.weixin.qq.com/cgi-bin/switchacct'
    headers = copy.deepcopy(default_headers)
    headers["cookie"] = cookie
    params = {
        "action": action,
        "token": token,
        "lang": "zh_CN",
        "f": "json",
        "ajax": 1
    }
    return lazyrequests.lazy_requests(
        method=method,
        url=url,
        headers=headers,
        params=params
    )


def get_acct_list(
        token: str,
        cookie: str
):
    """
    获取可切换账号列表信息
    :param token:
    :param cookie:
    :return:
    """
    return switch_acct(
        token=token,
        cookie=cookie,
        method="GET",
        action="get_acct_list"
    )