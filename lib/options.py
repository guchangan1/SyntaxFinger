#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = guchangan1
import os

from tldextract import tldextract

from api.fofa import Fofa
from api.quake import Quake
from api.hunter import Hunter
from config.data import Urls, logging, Ips, Search, Webinfo, Urlerror


class initoptions:
    def __init__(self, args):
        self.key = ["\"", "“", "”", "\\", "'"]
        Urls.url = []
        Webinfo.result = []
        Urlerror.result = []
        Search.search = []
        self._finger = args.finger
        self._url = args.url
        self._file = args.file
        self.projectname = args.projectname
        self.method = args.method
        self.icp = args.icp
        self.search = args.search
        self.vest = args.vest
        self.proxies = args.proxy
        if self.icp:
            self.syntax = self.check_icp(self.icp)
        if self.search:
            self.syntax = self.search

    def api_data(self):
        res = []
        fofa_res = []
        quake_res = []
        hunter_res = []
        if "f" in self.method:
            fofa_init = Fofa(self.syntax)
            fofa_res = fofa_init.run()
            res.extend(fofa_res)
        if "q" in self.method:
            fofa_init = Quake(self.syntax)
            quake_res = fofa_init.run()
            res.extend(quake_res)
        if "h" in self.method:
            hunter_init = Hunter(self.syntax)
            hunter_res = hunter_init.run()
            res.extend(hunter_res)
        return res


    def check_icp(self, icp):
        if "/" in icp:
            syntax = f"(ip=\"{icp}\")"
        else:
            tld = tldextract.extract(icp)
            # print(tld)
            if tld.suffix != '':
                domain = tld.domain + '.' + tld.suffix
                syntax = f"(domain=\"{domain}\"||cert=\"{domain}\")"
            else:
                ip = tld.domain
                syntax = f"(ip=\"{ip}\")"
        return syntax

    def target(self):
        if self._url:
            self.check_url(self._url)
        elif self._file:
            if os.path.exists(self._file):
                with open(self._file, 'r') as f:
                    for i in f:
                        self.check_url(i.strip())
            else:
                errMsg = "File {0} is not find".format(self._file)
                logging.error(errMsg)
                exit(0)

    def check_url(self, url):
        for key in self.key:
            if key in url:
                url = url.replace(key, "")
        if not url.startswith('http') and url:
            # 若没有http头默认同时添加上http与https到目标上
            Urls.url.append("http://" + str(url))
            Urls.url.append("https://" + str(url))
        elif url:
            Urls.url.append(url)


    def get_ip(self):
        try:
            if self._ip:
                if "-" in self._ip:
                    start, end = [self.ip_num(x) for x in self._ip.split('-')]
                    iplist = [self.num_ip(num) for num in range(start, end + 1) if num & 0xff]
                    for ip in iplist:
                        Ips.ip.append(ip)
                else:
                    Ips.ip.append(self._ip)
            if Ips.ip:
                run = Fofa()
        except Exception as e:
            logging.error(e)
            logging.error("IP格式有误，正确格式为192.168.10.1,192.168.10.1/24 or 192.168.10.10-192.168.10.50")
            exit(0)

    def ip_num(self, ip):
        ip = [int(x) for x in ip.split('.')]
        return ip[0] << 24 | ip[1] << 16 | ip[2] << 8 | ip[3]

    def num_ip(self, num):
        return '%s.%s.%s.%s' % ((num & 0xff000000) >> 24,
                                (num & 0x00ff0000) >> 16,
                                (num & 0x0000ff00) >> 8,
                                num & 0x000000ff)
