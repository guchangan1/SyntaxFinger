#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = guchangan1
import json
import base64
import random
import re

import requests
from urllib.parse import quote

from tldextract import tldextract

from config.data import logging, Urls
from config.config import Fofa_key, Fofa_email, head, Fofa_Size
from lib.cmdline import cmdline


class Fofa:
    def __init__(self, syntax):
        # Urls.url = []
        self.email = Fofa_email
        self.key = Fofa_key
        self.size = Fofa_Size
        self.old_syntax = syntax
        self.syntax = quote(str(base64.b64encode(syntax.encode()), encoding='utf-8'))
        self.headers = head
        if self.key == "":
            logging.error("请先在config/config.py文件中配置fofa的api")
            exit(0)

    def run(self):
        fofa_res_list = []
        logging.info("FoFa开始查询")
        logging.info("查询关键词为:{0},单次查询数量为:{1}".format(self.old_syntax, self.size))
        # 先看看有多少数据
        url = "https://fofa.info/api/v1/search/all?email={0}&key={1}&qbase64={2}&full=false&fields=host,ip,port,title,region,icp&size={3}".format(
            self.email, self.key, self.syntax, 10)
        try:
            response = requests.get(url, timeout=30, headers=self.headers)
            fofa_result = json.loads(response.text)
            if fofa_result["error"] == "true":
                logging.error(fofa_result["errmsg"])
            else:
                total = fofa_result["size"]
                total = int(total)
                if fofa_result["results"] == []:
                    logging.warning("唉，fofa啥也没查到，过下一个站吧")
                else:
                    logging.info("FOFA共获取到{0}条记录".format(total))
                    if total > self.size:
                        pages_total = total // self.size
                        pages_total += 1
                    else:
                        pages_total = 1
                    fofa_res = []
                    for page in range(1, pages_total + 1):
                        logging.warning("正在查询第{0}页".format(page))
                        api_request = "https://fofa.info/api/v1/search/all?email={0}&key={1}&qbase64={2}&fields=host,title,ip,port,server,region,icp&size={3}&page={4}".format(
                            self.email, self.key, self.syntax, self.size, page)
                        json_result = requests.get(api_request, timeout=30, headers=self.headers)
                        fofa_result = json.loads(json_result.text)
                        if fofa_result["error"] == "true":
                            logging.error(fofa_result["errmsg"])
                        if fofa_result["error"] == "true":
                            logging.error(fofa_result["errmsg"])
                        fofa_res += fofa_result["results"]
                    for singer_res in fofa_res:

                        if cmdline().search or self.check_dirty(singer_res[0]):
                            self.check_url(singer_res[0])
                            fofa_singer_res_dict = {"api": "Fofa", "url": singer_res[0], "title": singer_res[1],
                                                    "ip": singer_res[2], "port": singer_res[3], "server": singer_res[4],
                                                    "region":
                                                        singer_res[5], "icp": singer_res[6], "icp_name": "", "isp": "",
                                                    "syntax": self.old_syntax}
                            fofa_res_list.append(fofa_singer_res_dict)
                        else:
                            fofa_res.remove(singer_res)
            logging.info("Fofa查询完毕\n")

        except requests.exceptions.ReadTimeout:
            logging.error("请求超时")
        except requests.exceptions.ConnectionError:
            logging.error("网络超时")
        except json.decoder.JSONDecodeError:
            logging.error("获取失败，请重试")
        except KeyboardInterrupt:
            logging.warning("不想要fofa的结果，看下一个")
        except Exception as e:
            logging.error("获取失败，请检测异常"+e)
        return fofa_res_list

    def check(self):
        try:
            if self.email and self.key:
                auth_url = "https://fofa.info/api/v1/info/my?email={0}&key={1}".format(self.email, self.key)
                response = requests.get(auth_url, timeout=10, headers=self.headers)
                if self.email in response.text:
                    return True
                else:
                    return False
            else:
                return False
        except:
            return False

    def check_url(self, url):
        if not url.startswith('http') and url:
            # 若没有http头默认同时添加上http与https到目标上
            Urls.url.append("http://" + str(url))
            Urls.url.append("https://" + str(url))
        elif url:
            Urls.url.append(url)

    ###去除脏数据（目前仅去除掉cert！=domain的数据）
    def check_dirty(self, host):
        tld = tldextract.extract(host)
        # print(tld)
        if tld.suffix:
            domain = tld.domain + '.' + tld.suffix
            pattern = r'(?:domain|cert|ip)="([^"]*)"'
            matches = re.findall(pattern, self.old_syntax)
            if domain == str(matches[0]):
                return True
            else:
                return False
        else:
            return True


if __name__ == '__main__':
    a = Fofa("domain=\"nmg.gov.cn\"")
