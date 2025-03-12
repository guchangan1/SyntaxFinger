# -*- coding: utf-8 -*-

"""
@Time : 2023/10/27
@Author : guchangan1
"""
from tldextract import tldextract

from config.data import Webinfo, Urls, logging
from lib.C_ALL_GetCompany_ByDomain import find_icp_by_domain
from lib.D_ALL_GetDomain_ByUrl import GetDomain_ByUrl
from lib.proxy import proxies


class ICPAttributable:
    def __init__(self, ):
        logging.info(("正在查询ICP公司归属"))
        self.proxy = proxies()
    
    """
    取出指纹识别结果，进行icp查询
    """
    def getICPAttributable(self):
        try:
            for value in Webinfo.result:
                url = value["url"]
                domain = GetDomain_ByUrl(url)
                company_obj = find_icp_by_domain(domain,self.proxy)
                company_dict = company_obj.getICP_icplishi()
                Webinfo.result[Webinfo.result.index(value)]["icp"] = company_dict["unitName"]
        except Exception as e:
            pass
        logging.success("ICP公司归属查询完毕")

