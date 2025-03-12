#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = guchangan1
import os
import re
import json
import socket
import ipaddress
from lib.C_GetRecord_BySubDomain import GetRecord
from lib.B_CheckCDN import CheckCDN
from urllib.parse import urlsplit
from config.data import path



class IPFactory:
    def __init__(self):
        cdn_ip_cidr = os.path.join(path.library, 'cdn_ip_cidr.json')
        cdn_asn_list = os.path.join(path.library, 'cdn_asn_list.json')
        cdn_cname_keyword = os.path.join(path.library, 'cdn_cname_keywords.json')
        cdn_header_key = os.path.join(path.library, 'cdn_header_keys.json')
        nameservers_list = os.path.join(path.library, 'nameservers_list.json')
        with open(cdn_ip_cidr, 'r', encoding='utf-8') as file:
            self.cdn_ip_cidr_file = json.load(file)
        with open(cdn_asn_list, 'r', encoding='utf-8') as file:
            self.cdn_asn_list_file = json.load(file)
        with open(cdn_cname_keyword, 'r', encoding='utf-8') as file:
            self.cdn_cname_keyword_file = json.load(file)
        with open(cdn_header_key, 'r', encoding='utf-8') as file:
            self.cdn_header_key_file = json.load(file)
        with open(nameservers_list, 'r', encoding='utf-8') as file:
            self.nameservers_list_file = json.load(file)

    #获取host
    def parse_host(self,url):
        host = urlsplit(url).netloc
        if ':' in host:
            host = re.sub(r':\d+', '', host)
        return host


    #域名解析获取ip列表并排除CDN
    def factory(self, url, header):
        try:
            ip_list = []
            host = self.parse_host(url)
            pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
            if re.match(pattern, host):
                return 0, ip_list
            record = GetRecord(host)
            checkcdn = CheckCDN()
            ip_list = record.dns_resolve_A().get("A")
            asn_list = record.getASN_ByIP(ip_list).get("ASN")
            cname_list = record.dns_resolve_CNAME().get("CNAME")
            if ip_list:
                if checkcdn.check_cdn_cidr(ip_list) or checkcdn.check_cdn_asn(asn_list) or checkcdn.check_cname_keyword(cname_list) or checkcdn.check_header_key(header):
                    return "是", ip_list
                else:
                    return "否", ip_list
            else:
                return 0, ip_list

            # items = socket.getaddrinfo(host, None)
            # for ip in items:
            #     if ip[4][0] not in ip_list:
            #         ip_list.append(ip[4][0])
            # if len(ip_list) > 1:
            #     return 1, ip_list
            # else:
            #     for cdn in self.cdn_ip_cidr_file:
            #         if ipaddress.ip_address(ip_list[0]) in ipaddress.ip_network(cdn):
            #             return 1, ip_list
            # return 0, ip_list
        except Exception as e:
            return 0, ip_list

