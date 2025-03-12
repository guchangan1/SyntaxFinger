#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = guchangan1
import argparse

from config.color import color
from config.data import logging


def cmdline():
    parser = argparse.ArgumentParser(description=color.green("\n[*] 常用方法1（如下即为资产测绘+指纹识别）：\n"
                                                              "      [*] 功能：fscan就是仅fofa，fqscan就是fofa+quake。只有加上-finger之后才可以进行指纹识别，加上-vest进行归属公司查询\n"
                                                              "      [*] 输出: xx公司.xlsx 包含资产测绘原结果及经过指纹识别后的新结果\n"
                                                              "      [*] 以下为针对单一域名或者IP、IP段进行资产测绘"
                                                              "      python3 SyntaxFinger.py -d example.com -m fscan -o xx公司\n"
                                                              "      python3 SyntaxFinger.py -d example.com -m fqscan -o xx公司 -finger\n"
                                                              "      python3 SyntaxFinger.py -d 192.168.1.1 -m fqhscan -o xx公司\n"
                                                              "      python3 SyntaxFinger.py -d 192.168.1.1 -m fqhscan -o xx公司 -finger\n"
                                                              "      python3 SyntaxFinger.py -d 192.168.1.1/24 -m fscan -o xx公司 \n"
                                                              "      python3 SyntaxFinger.py -d 192.168.1.1/24 -m fscan -o xx公司 -finger\n\n"
                                                              "      [*] 以下为使用自定义命令进行资产测绘(考虑到格式不兼容，自己去看格式是什么)\n"
                                                              "      python3 SyntaxFinger.py -search (body=\"mdc-section\") -m fscan -o xx公司 -finger\n"
                                                             "       python3 SyntaxFinger.py -search (body=\"mdc-section\") -m fscan -o xx公司 -finger -vest\n\n"
                                                              "[*] 常用方法2（如下即为导入资产+指纹识别）：\n"
                                                              "     [*] 功能：-u导入单个url，-f导入url文件\n"
                                                              "     [*] 输出: xx公司.xlsx 经过指纹识别后的结果\n"
                                                              "     python3 SyntaxFinger.py -u http://www.example.com -finger -vest\n"
                                                              "     python3 SyntaxFinger.py -f 1.txt -finger -vest\n"
                                                              ""), formatter_class=argparse.RawTextHelpFormatter)

    api = parser.add_argument_group("资产测绘API+指纹识别")
    api.add_argument("-d", dest='icp', type=str,
                     help="1、支持输入根域名、单个IP，自动使用空间引擎对domain||cert或者IP进行查询\n"
                          "2、支持输入ip段，但是输入ip段时建议-m fscan（仅fofa搜索），不然hunter积分顶不住，quake也比较卡")
    api.add_argument("-search", dest='search', type=str,
                     help="自定义语法输入，仅可输入各资产测绘拥有的语法")
    api.add_argument("-m", dest='method', type=str,
                     help="fscan qscan hscan fqscan qhscan fqhscan，选择其一即可，代表fofa、quake、hunter或者联合查询")

    finger = parser.add_argument_group("手动导入资产+指纹识别")
    finger.add_argument('-u', dest='url', type=str, help="输入单个url，然后输入-finger进行单个指纹识别")
    finger.add_argument('-f', dest='file', type=str, help="输入url文件，然后输入-finger进行指纹识别")

    api = parser.add_argument_group("通用方法")
    api.add_argument("-finger", action="store_true", default=False, help="输入-finger则进行指纹识别")
    api.add_argument("-proxy", dest='proxy', type=str, help="增加代理")
    api.add_argument("-vest", action="store_true", default=False, help="输入-vest进行资产归属识别（定位icp）")
    api.add_argument("-o", dest='projectname', type=str,
                     help="输出excel，名称最好是公司全称，不需要加后缀", default=False)
    args = parser.parse_args()
    return args
