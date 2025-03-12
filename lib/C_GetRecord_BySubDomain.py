# -*- coding: utf-8 -*-

"""
@Time : 2023/11/6
@Author : guchangan1
"""
import os
import socket
import time
import geoip2.database
from config.data import path, logging

import dns.resolver


class GetRecord:
    def __init__(self, domain):
        self.fast_nameservers = ["114.114.114.114", "8.8.8.8", "80.80.80.80", "223.5.5.5"]
        self.domain = domain
        self.local_Resolver = dns.resolver.Resolver(configure=False)
        self.local_Resolver.retry_servfail = True
        self.local_Resolver.timeout = 3
        GeoLite2ASN = os.path.join(path.library, "data", 'GeoLite2-ASN.mmdb')
        self.reader = geoip2.database.Reader(GeoLite2ASN)

    def getASN_ByIP(self,iplist):
        asn_list = []
        try:
            for singer_ip in iplist:
                asn_response = self.reader.asn(singer_ip)
                asn = "AS"+ str(asn_response.autonomous_system_number)
                asn_list.append(asn)
        except Exception as e:
            logging.error(f"IP {singer_ip} 处理时发生异常：{e}")
        return result_ASN


    def dns_resolve_A(self):
        result_list = []
        for name_server in self.fast_nameservers:
            # time.sleep(1)
            self.local_Resolver.nameservers = [name_server]
            if len(result_list) > 3:
                return result_list
            try:
                myAnswers = self.local_Resolver.resolve(self.domain, "A", lifetime=1)
                for rdata in myAnswers:
                    if rdata.address not in result_list and ":" not in rdata.address:  # and len(result_list) < 5:
                        result_list.append(rdata.address)
            except Exception as error:
                continue
        result_A = {"A": result_list}
        return result_A

    def dns_resolve_CNAME(self):
        result_list = []
        # time.sleep(1)
        self.local_Resolver.nameservers = ["223.5.5.5"]
        try:
            myAnswers = self.local_Resolver.resolve(self.domain, "CNAME", lifetime=1)
            for rdatas in myAnswers.response.answer:
                    for rdata in rdatas.items:
                        result_list.append(rdata.to_text())
        except Exception as error:
            pass
        result_CNAME = {"CNAME": result_list}
        return result_CNAME




if __name__ == '__main__':
    record = GetRecord("rk800.mdzzz.org")
    start = time.time()
    result_A = record.dns_resolve_A()
    result_ASN = record.getASN_ByIP(result_A.get("A"))
    print(result_ASN)


    # result_CNAME = record.dns_resolve_CNAME()
    # print(result_CNAME)
    #
    # result_A = record.dns_resolve_A()
    # print(result_A)


    end = time.time()
    print(end - start)

