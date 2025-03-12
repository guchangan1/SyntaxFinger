#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = guchangan1
import re
import ssl

import requests
import random
import codecs
import mmh3
from fake_useragent import UserAgent
from lib.IpFactory import IPFactory
from urllib.parse import urlsplit, urljoin
from config.data import Urls, Webinfo,Urlerror,logging
from config import config
from lib.identify import Identify
from bs4 import BeautifulSoup
from lib.proxy import proxies
import urllib3
import warnings
from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings()
warnings.filterwarnings('ignore', category=InsecureRequestWarning)
from concurrent.futures import ThreadPoolExecutor


class Request:
    def __init__(self):
        #加载指纹至列表 初始化指纹库
        self.checkcms = Identify()
        #加载ip2region、cdn至列表  初始化IP库
        self.ipFactory = IPFactory()
        self.proxies = proxies()
        #线程池 多线程进行指纹识别
        logging.info(f"开始进行0-1-Nday指纹识别,去重后共对{len(set(Urls.url))}条URL进行指纹识别")
        with ThreadPoolExecutor(config.threads) as pool:
            run = pool.map(self.apply, set(Urls.url))
        logging.info(f"指纹识别完毕，存活url共计{len(Webinfo.result)}条，请求失败url共计{len(Urlerror.result)}条")


    #发送HTTP请求，获取响应
    def apply(self, url):
        try:
            with requests.get(url, timeout=15, headers=self.get_headers(), cookies=self.get_cookies(), verify=False,
                              allow_redirects=False, proxies=self.proxies, stream=True) as response:
                if int(response.headers.get("content-length", default=1000)) > 100000:
                    self.response(url, response, True)
                else:
                    self.response(url, response)
                if response.status_code == 302:
                    if 'http' in response.headers.get('Location','') :
                        redirect_url = response.headers.get('Location')
                    else:
                        redirect_url = urljoin(response.url, response.headers.get('Location'))
                    if redirect_url:
                        with requests.get(redirect_url, timeout=5, headers=self.get_headers(),
                                          cookies=self.get_cookies(), verify=False,
                                          allow_redirects=False, proxies=self.proxies, stream=True) as response2:
                            if int(response2.headers.get("content-length", default=1000)) > 100000:
                                self.response(redirect_url, response2, True)
                            else:
                                self.response(redirect_url, response2)
        except KeyboardInterrupt:
            logging.error("用户强制程序，系统中止!")
        except requests.exceptions.RequestException as e:
            results = {"url": str(url), "cms": "需要自己看原因", "title": str(e),
                       "status": "-", "Server": "-",
                       "size": "-", "iscdn": "-", "ip": "-",
                       "address": "-", "isp": "-", "icp": "-"}
            Urlerror.result.append(results)

        except ConnectionError as e:
            results = {"url": str(url), "cms": "响应超时", "title": str(e),
                       "status": "-", "Server": "-",
                       "size": "-", "iscdn": "-", "ip": "-",
                       "address": "-", "isp": "-", "icp": "-"}
            Urlerror.result.append(results)

        except Exception as e:
            results = {"url": str(url), "cms": "-", "title": str(e),
                       "status": "-", "Server": "-",
                       "size": "-", "iscdn": "-", "ip": "-",
                       "address": "-", "isp": "-", "icp": "-"}

            Urlerror.result.append(results)

    #对响应进行处理，封装好要准备进行识别的内容为datas
    def response(self, url, response, ignore=False):
        if ignore:
            html = ""
            size = response.headers.get("content-length", default=1000)
        else:
            response.encoding = response.apparent_encoding if response.encoding == 'ISO-8859-1' else response.encoding
            response.encoding = "utf-8" if response.encoding is None else response.encoding
            html = response.content.decode(response.encoding,"ignore")
            if response.text != None:
                size = len(response.text)
            else:
                size = 1000



        title = self.get_title(html).strip().replace('\r', '').replace('\n', '')
        status = response.status_code
        header = response.headers
        server = header.get("Server", "")
        server = "" if len(server) > 50 else server
        faviconhash = self.get_faviconhash(url, html)
        iscdn, iplist = self.ipFactory.factory(url, header)
        iplist = ','.join(set(iplist))
        datas = {"url": url, "title": title, "cms": "", "body": html, "status": status, "Server": server, "size": size,
                 "header": header, "faviconhash": faviconhash, "iscdn": iscdn, "ip": iplist,
                 "address": "", "isp": "", "icp": ""}
        self.checkcms.run(datas)

    def get_faviconhash(self, url, body):
        faviconpaths = re.findall(r'href="(.*?favicon....)"', body)
        faviconpath = ""
        try:
            parsed = urlsplit(url)
            turl = parsed.scheme + "://" + parsed.netloc
            if faviconpaths:
                fav = faviconpaths[0]
                if fav.startswith("//"):
                    faviconpath = "http:" + fav
                elif fav.startswith("http"):
                    faviconpath = fav
                else:
                    faviconpath = urljoin(turl, fav)
            else:
                faviconpath = urljoin(turl, "favicon.ico")
            response = requests.get(faviconpath, headers=self.get_headers(), timeout=4, verify=False)
            favicon = codecs.encode(response.content, "base64")
            hash = mmh3.hash(favicon)
            return hash
        except:
            return 0

    def get_title(self, html):
        soup = BeautifulSoup(html, 'lxml')
        title = soup.title
        if title and title.text:
            return title.text
        if soup.h1:
            return soup.h1.text
        if soup.h2:
            return soup.h2.text
        if soup.h3:
            return soup.h3.text
        desc = soup.find('meta', attrs={'name': 'description'})
        if desc:
            return desc['content']

        word = soup.find('meta', attrs={'name': 'keywords'})
        if word:
            return word['content']

        text = soup.text
        if text !=None:
            if len(text) <= 200:
                return text
        return ''

    def get_headers(self):
        """
        生成伪造请求头
        """
        # ua = random.choice(config.user_agents)
        headers = config.head
        return headers

    def get_cookies(self):
        cookies = {'rememberMe ': 'xxx'}
        # cookies = {'xxx': 'xxx'}
        return cookies




