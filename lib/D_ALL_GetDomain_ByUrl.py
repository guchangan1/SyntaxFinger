# -*- coding: utf-8 -*-

"""
@Time : 2023/10/26
@Author : guchangan1
"""
import re
import socket

import requests
from tldextract import tldextract
from lxml import etree

from lib.proxy import proxies

requests.packages.urllib3.disable_warnings()

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
    "Connection": "close",
}


class find_domain_by_ip():

    def __init__(self, ip):
        self.ip = ip

    ##调用138接口
    def getDomain_138(self, replayNun=0):
        allData = []  # 爬取反查域名信息
        domainList = []  # 最终反查域名信息
        argIsDoamin = False  # 参数默认非domain
        try:
            req1 = requests.get(url=f"https://site.ip138.com/{self.ip}/", headers=headers, timeout=20, verify=False, proxies=proxies())
            if req1.status_code != 200 and replayNun < 2:
                replayNun += 1
                return self.getDomain_138(self.ip, replayNun)
            if req1.status_code != 200 and replayNun == 2:
                domainList.append(f"NtError c:{req1.status_code}")
                return domainList
            html = etree.HTML(req1.text, etree.HTMLParser())
            if re.match(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
                        self.ip):
                allData = html.xpath(
                    '//ul[@id="list"]/li/a[@target="_blank"]/text()')  # 获取a节点下的内容,获取到ip曾解析到的domain   存在老旧数据
            else:
                argIsDoamin = True
                # histryIp = html.xpath('//div[@id="J_ip_history"]/p/a[@target="_blank"]/text()') #获取a节点下的内容,获取到域名解析到的ip   存在老旧数据
                allData.append(self.ip)
            for domin in allData:
                # 确保反查到的域名可解析到当前ip   剔除老旧数据
                if argIsDoamin or (self.ip in self.getIpList(domin)):
                    # 剔除相同域名
                    domainObj = tldextract.extract(domin)
                    domainData = f"{domainObj.domain}.{domainObj.suffix}"
                    if domainData not in domainList:
                        domainList.append(domainData)
            # ipPosition=html.xpath('//div[@class="result result2"]/h3/text()')  #获取ip位置信息
        except Exception as e:
            #         print(f"\033[31m[Error] url:https://site.ip138.com/{ip}/ {e}\033[0m")
            domainList.append("NtError")
        return domainList


    # 获取域名解析出的IP列表(确保反查到的域名可解析到当前ip)
    def getIpList(self, domain):
        ip_list = []
        try:
            addrs = socket.getaddrinfo(domain, None)
            for item in addrs:
                if item[4][0] not in ip_list:
                    ip_list.append(item[4][0])
        except Exception as e:
            pass
        return ip_list


def GetDomain_ByUrl(url):
    tld = tldextract.extract(url)
    # print(tld)
    if tld.suffix != '':
        domain = tld.domain + '.' + tld.suffix
        return domain
    else:
        ip = tld.domain
        domain = find_domain_by_ip(ip).getDomain_138()
        if not domain:
            return
        else:
            return domain[0]


if __name__ == '__main__':
    domainList = GetDomain_ByUrl("221.122.179.142")
    print(domainList)