# -*- coding: utf-8 -*-

"""
@Time : 2023/11/6
@Author : guchangan1
"""
import ipaddress
import json
import os
import dns.resolver
from config.data import path


class CheckCDN:
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


    def check_cname_keyword(self, cnames):
        if not cnames:
            return False
        for name in cnames:
            for keyword in self.cdn_cname_keyword_file.keys():
                if keyword in name:
                    return True


    def check_header_key(self, header):
        if isinstance(header, str):
            header = json.loads(header)
        if isinstance(header, dict):
            header = set(map(lambda x: x.lower(), header.keys()))
            for key in self.cdn_header_key_file:
                if key in header:
                    return True
        else:
            return False


    def check_cdn_cidr(self, ips):
        for ip in ips:
            try:
                ip = ipaddress.ip_address(ip)
            except Exception as e:
                return False
            for cidr in self.cdn_ip_cidr_file:
                if ip in ipaddress.ip_network(cidr):
                    return True


    def check_cdn_asn(self, asns):
        for asn in asns:
            if isinstance(asn, str):
                if asn in self.cdn_asn_list_file:
                    return True
            return False

    def check_cdn_dns_resolve(self, domain):
        local_Resolver = dns.resolver.Resolver(configure=False)
        local_Resolver.retry_servfail = True
        local_Resolver.timeout = 3
        result_list = []

        for name_server in self.nameservers_list_file:
            # time.sleep(1)
            local_Resolver.nameservers = [name_server]
            if len(result_list) > 3:
                return True
            try:
                myAnswers = local_Resolver.resolve(domain, "A", lifetime=1)
                for rdata in myAnswers:
                    if rdata.address not in result_list and ":" not in rdata.address:  # and len(result_list) < 5:
                        result_list.append(rdata.address)
            except Exception as error:
                continue
        if len(result_list) < 4:
            return False



if __name__ == '__main__':
    host  = "rk800.mdzzz.org"
    header = ""
    record = GetRecord(host)
    result_CNAME = record.dns_resolve_CNAME().get("CNAME")
    result_A = record.dns_resolve_A().get("A")
    result_ASN = record.getASN_ByIP(result_A).get("ASN")

    cdncheck = CheckCDN()
    # cdncheck.check_cname_keyword(result_CNAME)
    # cdncheck.check_cdn_cidr(result_A)
    # cdncheck.check_header_key(header)
    print(cdncheck.check_cdn_asn(result_ASN))
