#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = guchangan1
import json
import math
import random
import re
import time

import requests

from config.data import Urls, logging
from config.config import QuakeKey, user_agents, Fofa_Size

requests.packages.urllib3.disable_warnings()


class Quake:
    def __init__(self, syntax):
        # Urls.url = []
        self.headers = {
            "User-Agent": random.choice(user_agents),
            "X-QuakeToken": QuakeKey,
            "Content-Type": "application/json"
        }
        if QuakeKey == "":
            logging.warning("请先在config/config.py文件中配置quake的api")
            exit(0)
        if "||" in syntax:
            syntax_new = syntax.replace("||", " or ")
        else:
            syntax_new = syntax
        self.old_syntax = syntax
        self.syntax = syntax_new
        self.size = 200
        self.MaxSize = 10000  ##暂时没想好这块怎么写

    def run(self):
        quake_Results_tmp = []
        logging.info("Quake开始查询")
        logging.info("查询关键词为:{0},单次查询数量为:{1}".format(self.syntax, self.size))
        self.data = {
            "query": self.syntax,
            "start": 0,
            "size": self.size
        }
        try:
            response = requests.post(url="https://quake.360.net/api/v3/search/quake_service", headers=self.headers,
                                     json=self.data, timeout=30, verify=False)
            while (response.status_code != 200):
                logging.info(f'[*] 等待8秒后 将尝试重新获取数据')
                time.sleep(8)
                response = requests.post(url="https://quake.360.net/api/v3/search/quake_service", headers=self.headers,
                                         json=self.data, timeout=30, verify=False)
            datas = json.loads(response.text)
            total = datas['meta']['pagination']['total']

            if len(datas['data']) >= 1 and datas['code'] == 0:
                logging.info("Quake共获取到{0}条记录".format(total))
                datas_res = datas['data']
                pages = math.ceil(total / self.size)
                if pages > 1:
                    for page in range(1, pages + 1):
                        logging.info("正在查询第{0}页".format(page + 1))
                        time.sleep(1)
                        data = {
                            "query": self.syntax,
                            "start": page * self.size,
                            "size": self.size
                        }
                        response = requests.post(url="https://quake.360.net/api/v3/search/quake_service",
                                                 headers=self.headers,
                                                 json=data, timeout=30, verify=False)
                        while (response.status_code != 200):
                            logging.info(f'[*] 等待8秒后 将尝试重新获取数据')
                            time.sleep(8)
                            response = requests.post(url="https://quake.360.net/api/v3/search/quake_service",
                                                     headers=self.headers,
                                                     json=data, timeout=30, verify=False)
                        datas = json.loads(response.text)
                        datas_res += datas['data']
                for singer_data in datas_res:
                    ip, port, host, name, title, path, product, province_cn, favicon, x_powered_by, cert = '', '', '', '', '', '', '', '', '', '', ''
                    ip = singer_data['ip']  # ip
                    port = singer_data['port']  # port
                    location = singer_data['location']  # 地址
                    service = singer_data['service']
                    province_cn = location['province_cn']  # 地址
                    name = service['name']  # 协议
                    product = ""  # 服务
                    # if 'cert' in service.keys():
                    #     cert = service['cert']  # 证书
                    #     cert = re.findall("DNS:(.*?)\n", cert)
                    # 这个地方别疑惑，就是找title，因为service的key不管你是https还是http，肯定都包含http嘛，对的
                    if 'http' in service.keys():
                        http = service['http']
                        host = http['host']  # 子域名
                        title = http.get('title', 'not exist')  # title
                        title = title.strip()
                        # x_powered_by = http['x_powered_by']
                        # favicon = http['favicon']
                        # path = http['path']  # 路径
                    port_tmp = "" if port == 80 or port == 443 else ":{}".format(str(port))
                    if 'http/ssl' == name:
                        url = 'https://' + host + port_tmp
                        # logging.info(url)
                    elif 'http' == name:
                        url = 'http://' + host + port_tmp
                        # logging.info(url)
                    else:
                        url = name + "://" +ip + port_tmp
                    url, title, ip, port, server, address = url, title, ip, port, product, province_cn
                    quake_Result = {"api": "Quake", "url": url, "title": title, "ip": ip, "port": port,
                                    "server": server,
                                    "region": address, "icp": "", "icp_name": "", "isp": "",
                                    "syntax": self.syntax}
                    quake_Results_tmp.append(quake_Result)
                    self.check_url(url)
            else:
                logging.info("没有查询到数据")
            logging.info("Quake查询完毕\n")

        except requests.exceptions.ReadTimeout:
            logging.error("请求超时")
        except requests.exceptions.ConnectionError:
            logging.error("网络超时")
        except json.decoder.JSONDecodeError:
            logging.error("获取失败，请重试")
        except KeyboardInterrupt:
            logging.warning("不想要quake的结果，看下一个")
        except Exception as e :
            logging.error("Quake获取失败，检查异常"+e)
            pass
        return quake_Results_tmp

    def check_url(self, url):
        if not url.startswith('http') and url:
            # 若没有http头默认同时添加上http与https到目标上
            Urls.url.append("http://" + str(url))
            Urls.url.append("https://" + str(url))
        elif url:
            Urls.url.append(url)


if __name__ == '__main__':
    Quake("domain=\"xxxx.gov.cn\"")
