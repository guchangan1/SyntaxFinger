#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = guchangan1
import os

from api.api_output import api_output
from config import config
from config.data import logging, Webinfo, Urls, path
from lib.cmdline import cmdline
from lib.checkenv import CheckEnv
from lib.req import Request
from lib.ipAttributable import IpAttributable
from lib.ICPAttributable import ICPAttributable
from colorama import init as wininit
from lib.options import initoptions

wininit(autoreset=True)

if __name__ == '__main__':
    # 打印logo
    print(config.Banner)
    # 检测环境
    CheckEnv()

    # 初始化参数
    finger = initoptions(cmdline())

    """
    获取url 全局 Urls.url
    """
    if finger.method and (finger.icp or finger.search):
        # 空间引擎获取资产,并且url自动存入Urls.url
        api_res = finger.api_data()
    elif finger._url or finger._file:
        # 直接导入url，存储到Urls.url
        finger.target()

    """
    指纹识别 全局 
    存活：Webinfo.result
    失败：Urlerror.result
    """
    if finger._finger:
        # 对Urls.url进行指纹识别，结果存储到Webinfo.result
        Request()

    if finger._finger:
        # 对解析的IP进行归属查询
        IpAttributable().getAttributable()
        # 对url进行icp归属识别
        if finger.vest:
            ICPAttributable().getICPAttributable()

    """
    导出结果，生成excel
    """
    # 导出空间引擎的url或者文件导入的url进行指纹识别的结果
    if finger.projectname:
        apioutput = api_output(finger.projectname)
        # 导出纯空间引擎资产
        if finger.method:
            apioutput.api_outXls(api_res)
        if finger._finger:
            apioutput.Succfinger_outXls()
            apioutput.Failfinger_outXls()
