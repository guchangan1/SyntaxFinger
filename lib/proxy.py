import requests

from config.data import logging
from  lib.cmdline import cmdline

# 代理
def proxies():
    arg = cmdline()
    # if 1==1:
    proxies = None
    if arg.proxy == "2":

        proxies = {
            "http": "http://127.0.0.1:8080",
            "https": "http://127.0.0.1:8080"
        }
        logging.info("正在使用burp进行代理：%s" % proxies)
    if arg.proxy == "1":
        # 隧道域名:端口号
        tunnel = "xxxx.kdltps.com:15818"

        # 用户名密码方式
        username = "xxxxx"
        password = "xxxxxx"
        proxies = {
            "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel},
            "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel}
        }
        # proxies = {
        #     "http": arg.proxy,
        #     "https": arg.proxy
        # }
        logging.info("正在测试代理池连通性：%s" % proxies)
        # 测试页面
        target_url = "https://dev.kdlapi.com/testproxy"

        # 使用隧道域名发送请求
        response = requests.get(target_url, proxies=proxies)

        # 获取页面内容
        if response.status_code == 200:
            logging.success("代理池已稳定加载：%s" % proxies)

    return proxies
