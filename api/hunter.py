# -*- coding: utf-8 -*-

"""
@Time : 2023/9/11
@Author : guchangan1
"""
import base64
import json
import math
import random
import time

import requests

from config.config import Hunter_token, head, Fofa_Size
from config.data import logging, Urls


class Hunter:
    def __init__(self, syntax):
        # Urls.url = []
        self.headers = head
        if Hunter_token == "":
            logging.warning("请先在config/config.py文件中配置hunter的api")
            exit(0)
        self.old_syntax = syntax
        self.syntax = self.old_syntax.encode('utf-8')
        self.syntax = base64.urlsafe_b64encode(self.syntax)
        self.syntax = str(self.syntax, 'utf-8')
        self.size = 100
        # 查询的最大数据量
        self.MaxTotal = 2000
        self.Hunter_token = Hunter_token

    def run(self):
        qianxin_Results = []
        logging.info("Hunter开始查询")
        logging.info("查询关键词为:{0}，单次查询数据为:{1}".format(self.old_syntax, self.size))
        try:
            Hunter_api = "https://hunter.qianxin.com/openApi/search?&api-key={}&search={}&page=1&page_size={}&is_web=1&start_time=2023-08-21&end_time=2024-08-21". \
                format(self.Hunter_token, self.syntax, self.size)
            res = requests.get(Hunter_api, headers=self.headers, timeout=30)
            while (res.status_code != 200):
                logging.info(f'[*] 等待8秒后 将尝试重新获取数据')
                time.sleep(8)
                res = requests.get(Hunter_api, headers=self.headers, timeout=30)
            hunter_result = json.loads(res.text)
            total = hunter_result["data"]["total"]
            # # 消耗积分
            # consume_quota = hunter_result["data"]["consume_quota"]
            # 今日剩余积分
            rest_quota = hunter_result["data"]["rest_quota"]
            logging.info("Hunter共获取到{0}条记录| {2} | 将要消耗{1}个积分".format(total, total, rest_quota))
            total = self.MaxTotal if total > self.MaxTotal else total
            pages = total / self.size
            pages = math.ceil(pages)
            logging.info('[hunter] 限定查询的数量:{}'.format(total))
            logging.info('[hunter] 查询的页数:{}'.format(pages))
            if hunter_result['data']['arr']:
                qianxin_Results_tmp = self.data_clean(
                    hunter_result['data']['arr'])
                qianxin_Results = qianxin_Results_tmp
            else:
                logging.warning("没有获取到数据")
                pages = 1
            if pages != 1:
                for page in range(2, pages + 1):
                    logging.info("正在查询第{0}页".format(page))
                    time.sleep(8)
                    Hunter_api = "https://hunter.qianxin.com/openApi/search?&api-key={0}&search={1}&page={2}&page_size={3}&is_web=1&start_time=2023-08-21&end_time=2024-08-21".format(
                        self.Hunter_token, self.syntax, page, self.size)
                    res = requests.get(Hunter_api, headers=self.headers, timeout=30)
                    while (res.status_code != 200):
                        logging.info(f'[*] 等待8秒后 将尝试重新获取数据')
                        time.sleep(8)
                        res = requests.get(Hunter_api, headers=self.headers, timeout=30)
                    hunter_result = json.loads(res.text)
                    qianxin_Results_tmp = self.data_clean(
                        hunter_result.get("data",None).get("arr",None))
                    qianxin_Results.extend(qianxin_Results_tmp)
            logging.info("Hunter查询完毕\n")

        except KeyboardInterrupt:
            logging.warning("不想要hunter的结果，看下一个")
        except Exception as e:
            logging.error("Hunter获取失败" + e )
        return qianxin_Results

    def data_clean(self, hunter_result):
        qianxin_Results_tmp = []
        for singer_result in hunter_result:
            url = singer_result["url"]
            title = singer_result["web_title"]
            ip = singer_result["ip"]
            # subdomain = singer_result["domain"]
            port = singer_result["port"]
            server = str(singer_result["component"])
            protocol = singer_result["protocol"]
            address = singer_result["city"]
            company = singer_result["company"]
            isp = singer_result["isp"]
            # updated_at = singer_result["updated_at"]
            qianxin_Results_dict = {"api": "Hunter", "url": url, "title": title, "ip": ip, "port": port,
                                    "server": server,
                                    "region": address, "icp": "", "icp_name": company, "isp": isp,
                                    "syntax": self.old_syntax}
            # qianxin_Results_tmp.append([url, title, ip, port, server, address, company, isp])
            qianxin_Results_tmp.append(qianxin_Results_dict)
            self.check_url(url)
        return qianxin_Results_tmp

    def check_url(self, url):
        if not url.startswith('http') and url:
            # 若没有http头默认同时添加上http与https到目标上
            Urls.url.append("http://" + str(url))
            Urls.url.append("https://" + str(url))
        elif url:
            Urls.url.append(url)


if __name__ == '__main__':
    Hunter("domain=\"xxxx.gov.cn\"")
