#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = guchangan1
import os
import random

from fake_useragent import UserAgent

Version = "V3.0"
Author = "guchangan1"
Github = "https://github.com/guchangan1"
Banner = '''   ____                    _                    _____   _                               
 / ___|   _   _   _ __   | |_    __ _  __  __ |  ___| (_)  _ __     __ _    ___   _ __ 
 \___ \  | | | | | '_ \  | __|  / _` | \ \/ / | |_    | | | '_ \   / _` |  / _ \ | '__|
  ___) | | |_| | | | | | | |_  | (_| |  >  <  |  _|   | | | | | | | (_| | |  __/ | |   
 |____/   \__, | |_| |_|  \__|  \__,_| /_/\_\ |_|     |_| |_| |_|  \__, |  \___| |_|   
          |___/                                                    |___/               --by guchangan1'''

# 设置线程数，默认30
threads = 5
#注意，此处的Size指的是每页的大小，并不是最大限制。
Fofa_Size= 1000

# 设置Fofa key信息  普通会员API查询数据是前100，高级会员是前10000条根据自已的实际情况进行调整。
Fofa_email = ""
Fofa_key = ""

# 设置360quake key信息，每月能免费查询3000条记录

QuakeKey = ""

# 设置qax hunter key信息
Hunter_token = ""

# 是否选择在线跟新指纹库，默认为True每次程序都会检查一遍指纹库是否是最新
FingerPrint_Update = False


user_agents = UserAgent().random
head = {
    'Accept': '*',
    'Accept-Language': '*',
    'Connection': 'close',
    'User-Agent': user_agents
}