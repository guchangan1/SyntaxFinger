#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = guchangan1
import os
import re
import json
from config.data import path
from config.color import color
from urllib.parse import urlsplit
from config.data import logging, Webinfo
from urllib.parse import urlparse


class Identify:
    def __init__(self):
        filepath_old = os.path.join(path.library, 'finger_old.json')
        with open(filepath_old, 'r', encoding='utf-8') as file_old:
            self.all_fingerprint = json.load(file_old)
            logging.success(f"已成功加载互联网-Nday指纹{len(self.all_fingerprint)}条")

    def run(self, datas):
        self.datas = datas
        cms = self.which_app(self.datas["header"], self.datas["body"], self.datas["title"], self.datas["faviconhash"])
        if self.checkbackground():
            cms.append("后台")
        language = self.get_language(self.datas["header"])
        cms.extend(language)
        self.datas["cms"] = ' || '.join(set(cms))
        # _url = "://{0}".format(urlsplit(self.datas['url']).netloc)  # 添加://降低误报率
        _webinfo = str(Webinfo.result)
        if self.datas['url'] in _webinfo:
            pass
        else:
            results = {"url": self.datas["url"], "cms": self.datas["cms"], "title": self.datas["title"],
                       "status": self.datas["status"], "Server": self.datas['Server'],
                       "size": self.datas["size"], "iscdn": self.datas["iscdn"], "ip": self.datas["ip"],
                       "address": self.datas["address"], "isp": self.datas["isp"], "icp": self.datas["icp"]}
            if cms:
                Webinfo.result.insert(0, results)
            else:
                Webinfo.result.append(results)
            if self.datas['status'] == 200:
                msg_status = color.green(self.datas['status'])
            elif self.datas['status'] == 301 or self.datas['status'] == 302:
                msg_status = color.blue(self.datas['status'])
            else:
                msg_status = color.yellow(self.datas['status'])
            Msg = "{0} | 指纹:[{1}] | Status:[{2}] | 标题：\"{3}\" ".format(self.datas["url"],
                                                                           color.green(self.datas['cms']),
                                                                           msg_status,
                                                                           color.blue(self.datas['title'])
                                                                           )
            logging.success(Msg)

    # 指纹校验
    def check_fingerprint(self, finger, resp_header, resp_body, html_title, favicon_hash):
        allowed_method = ['keyword', 'faviconhash']
        allowed_keyword_position = ['title', 'body', 'header']
        method = finger.get('method', None)
        match_content = finger.get('match', None)
        if method not in allowed_method:
            print("指纹有误(method):", finger)
            return False
        if not match_content:
            print("指纹有误(match):", finger)
            return False
        if method == "keyword":
            position = finger.get('position', None)
            if position not in allowed_keyword_position:
                print("指纹有误(position):", finger)
                return False
            if position == "title":
                return match_content in html_title
            elif position == "body":
                return match_content in resp_body
            elif position == "header":
                return match_content in resp_header
        elif method == "faviconhash":
            return match_content == favicon_hash
        return False

    def relation_split(self, relation):
        relation_split_list = relation.split(" ")
        index = 0
        while index < len(relation_split_list):
            if relation_split_list[index].startswith("(") and relation_split_list[index] != "(":
                relation_split_list[index] = relation_split_list[index][1:]
                relation_split_list.insert(index, "(")
            if relation_split_list[index].endswith(")") and relation_split_list[index] != ")":
                relation_split_list[index] = relation_split_list[index][:-1]
                relation_split_list.insert(index + 1, ")")
            index = index + 1
        return relation_split_list

    def has_app(self, fingerprint, resp_header, resp_body, html_title, favicon_hash):
        fingers_result = {}
        fingers = fingerprint['finger']
        relations = fingerprint['relation']
        for k in fingers.keys():
            finger = fingers[k]
            fingers_result[k] = self.check_fingerprint(finger, resp_header, resp_body, html_title, favicon_hash)
        for relation in relations:
            # 拆开 index1 and index2  -> [index1,and,index1]
            relation_split_list = self.relation_split(relation)
            for i in range(len(relation_split_list)):
                if relation_split_list[i] not in ["and", "or", "(", ")"]:
                    #index1 存在则为True  index2不存在则为 False
                    relation_split_list[i] = str(fingers_result.get(relation_split_list[i], False))
            #把列表转成字符串   [index1,and,index1] - > True and False
            relation_replaced = " ".join(relation_split_list)
            #运算  成立则为True
            if eval(relation_replaced):
                return True, relation
        return False, None

    def which_app(self, resp_header, resp_body, html_title, favicon_hash=None):
        app_list = []
        if favicon_hash is None:
            favicon_hash = "x"
        for fingerprint in self.all_fingerprint:
            is_has_app, matched_relation = self.has_app(fingerprint, resp_header, resp_body, html_title, favicon_hash)
            if is_has_app:
                # fingerprint['matched_relation'] = matched_relation
                ## 判断指纹是否拥有0day
                if fingerprint["day_type"] == 0:
                    day_type = "0day!!!"
                if fingerprint["day_type"] == 1:
                    day_type = "1day!"
                if fingerprint["day_type"] == -1:
                    day_type = "通用"
                app_list.append(fingerprint["product"] + f"({day_type})" + "[" +fingerprint["team"] + "]")
        return app_list

    # 独立出的方法，专门检查后台
    def checkbackground(self):

        url = self.datas["url"].split("|")[0].strip()

        # 关键字匹配
        if "后台" in self.datas["title"] or "系统" in self.datas["title"] or "登陆" in self.datas["title"] or "管理" in \
                self.datas["title"]:
            return True

        elif ("管理员" in self.datas["body"] and "登陆" in self.datas["body"] or
              "登陆系统" in self.datas["body"]):
            return True

        try:
            path = urlparse(url).path.lower()
            bak_url_list = ("/login;jsessionid=", "/login.aspx?returnurl=", "/auth/login",
                            "/login/?next=", "wp-login.php", "/ui/#login", "/admin", "/login.html",
                            "/admin_login.asp")

            if path in bak_url_list:
                return True
        except:
            pass

        if (re.search(r"<input.*type=\"password\"", self.datas["body"]) or
                re.search(r"<input.*name=\"password\"", self.datas["body"])):
            return True

    # 独立出的方法，专门检查框架、语言
    def get_language(self, header):
        language = []

        if "rememberMe=deleteMe" in header.get("Set-Cookie", "x"):
            language.append("Shiro")
        if "ASPSESSIONID" in header.get("Set-Cookie", "x") or "X-AspNet-Version" in header:
            language.append("ASP.NET")
        if "JSESSIONID" in header.get("Set-Cookie", "x"):
            language.append("JSP")
        if "PHPSESSID" in header.get("Set-Cookie", "x"):
            language.append("PHP")
        if "laravel_session" in header.get("Set-Cookie", "x"):
            language.append("laravel")
        if "jeesite.session.id" in header.get("Set-Cookie", "x"):
            language.append("jeesite")
        if header.get("X-Powered-By",None):
            language.append(header.get("X-Powered-By"))

        return language
