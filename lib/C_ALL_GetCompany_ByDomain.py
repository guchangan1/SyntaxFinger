import requests
from bs4 import BeautifulSoup
from lxml import etree

requests.urllib3.disable_warnings()
requests.warnings.filterwarnings("ignore")

class find_icp_by_domain():

    """
    通过域名查找icp
    """
    def __init__(self, domain, proxy=None):
        self.domain = domain
        self.proxy = proxy
        self.resultDict = {"domain": self.domain, "unitName": "-", "unitICP": "-"}

    result = []
    header1 = {
        "Host":"www.beianx.cn",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",        
    }
    header2 = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie': 'allSites=baidu.com%2C0; _csrf=acbe3685c56e8c51a17b499298dad6c19d2313d4d924001f5afdf44db886270ba%3A2%3A%7Bi%3A0%3Bs%3A5%3A%22_csrf%22%3Bi%3A1%3Bs%3A32%3A%22gonHG5mJdHz-E-sukWk5KT792jxOmQle%22%3B%7D; Hm_lvt_b37205f3f69d03924c5447d020c09192=1695301492,1695346451; Hm_lvt_de25093e6a5cdf8483c90fc9a2e2c61b=1695353426; Hm_lpvt_de25093e6a5cdf8483c90fc9a2e2c61b=1695353426; PHPSESSID=vuuel7fg33joirp3qlvue7up26; Hm_lpvt_b37205f3f69d03924c5447d020c09192=1695366436',
        'Host': 'icp.aizhan.com',
        'Pragma': 'no-cache',
        'Referer': 'https://icp.aizhan.com/',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.36',
        'sec-ch-ua': '"Microsoft Edge";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }
    header3 = {
        "Host":"icplishi.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",        
    }

    msg1 = "网络出现问题!"
    msg2 = "ip被ban啦！"
    msg3 = "未查询到相关结果！"
    msg4 = "网站结构发生改变，请联系开发处理！"


    
    def get_request(self,url,header):
        try:
            res = requests.get(url,headers=header,verify=False,timeout=1,proxies=self.proxy)
            return res
        except:
            print(self.msg1)
            return self.resultDict


    def get_ba1(self):
        """
        调用www.beianx.cn进行查询
        """
        resultDict = self.resultDict
        res = self.get_request(f"https://www.beianx.cn/search/{self.domain}",header=self.header1)
        if res == None:
            print(self.msg1)
            return resultDict
        html = res.text
        soup = BeautifulSoup(html, 'html.parser')
        ip_baned = soup.find('div', class_='text-center')
        if ip_baned:
            if ip_baned.text[0:6] == "您的IP地址":
                print(self.msg2)
                return resultDict
        no_records = soup.find('td', class_='text-center')
        if no_records:
            if no_records.text != "1":
                msg = no_records.text.replace('\r\n', '').replace(" ", "")
                print(msg)
                return resultDict
        table = soup.find('table', class_='table')
        if table:
            rows = table.find_all('tr')
            for row in rows[1:]: 
                columns = row.find_all('td')
                if len(columns) >= 5:
                    unitName = columns[1].text.strip()
                    serviceLicence = columns[3].text.strip()
                    resultDict = {"domain": self.domain, "unitName": unitName, "unitICP": serviceLicence}
            return resultDict


    def get_ba2(self):
        """
        调用icp.aizhan.com进行查询
        """
        resultDict = self.resultDict
        res = self.get_request(f"https://icp.aizhan.com/{self.domain}/",header=self.header2)
        if res == None:
            print(self.msg1)
            return resultDict
        html = res.content
        soup = BeautifulSoup(html, 'html.parser')
        no_recodes = soup.find("div", class_="cha-default")
        if no_recodes:
            print(self.msg3)
            return resultDict
        table = soup.find("table", class_="table")
        if table:
            rows = table.find_all('tr')
            unitName = rows[0].find_all('td')[1].text.strip()[:-8]
            serviceLicence = rows[2].find_all('td')[1].text.strip()[:-11]
            resultDict = {"domain": self.domain, "unitName": unitName,  "unitICP": serviceLicence}
            return resultDict


    def getICP_icplishi(self, replayNun=0):
        # print(domain)
        resultDict = self.resultDict
        try:
            req = requests.get(url=f"https://icplishi.com/{self.domain}", headers=self.header3, timeout=20)
            if req.status_code != 200 and replayNun < 2:
                replayNun += 1
                return self.getICP_icplishi(replayNun)
            if req.status_code != 200 and replayNun == 2:
                resultDict = {"domain": self.domain, "unitName": f"NtError:{req.status_code}，请加延时",
                              "unitICP": f"NtError:{req.status_code}"}
                # print(resultDict)
                return resultDict
            html = etree.HTML(req.text, etree.HTMLParser())

            # 备案类型、备案时间
            SpanTag = html.xpath(
                '//div[@class="module mod-panel"]/div[@class="bd"]/div[@class="box"]/div[@class="c-bd"]/table/tbody/tr/td/span/text()')
            # 备案号、备案名
            ATag = html.xpath(
                '//div[@class="module mod-panel"]/div[@class="bd"]/div[@class="box"]/div[@class="c-bd"]/table/tbody/tr/td/a/text()')

            token = html.xpath('//div[@id="J_beian"]/@data-token')
            # 直接获取到备案
            if len(ATag) >= 2 and len(SpanTag) >= 2 and (SpanTag[1] != "未备案"):
                resultDict = {"domain": self.domain, "unitName": ATag[0], "unitICP": ATag[1]}
                return resultDict
            if (token and resultDict["unitName"] == "-") or (token and "ICP" not in resultDict["unitICP"]) or (
                    token and '-' in SpanTag[1]):
                resultDict = self.getIcpFromToken(token[0])
        except Exception as e:
            resultDict = {"domain": self.domain, "unitName": "-", "unitICP": "-"}
        return resultDict

    # 两次出现"msg"="暂无结果"，为未查询出结果
    def getIcpFromToken(self, token, replayNun=0):
        try:
            req = requests.get(f"https://icplishi.com/query.do?domain={self.domain}&token={token}", headers=self.header3,
                               timeout=20)
            if (req.status_code != 200 or req.json()["msg"] == "暂无结果") and replayNun < 2:
                replayNun += 1
                return self.getIcpFromToken(token, replayNun)
            data = req.json()["data"]
            if req.status_code != 200 or req.json()["msg"] == "暂无结果" or len(data) == 0 or len(data[0]) == 0 or \
                    data[0][
                        "license"] == "未备案":
                resultDict = {"domain": self.domain, "unitName": "-", "unitICP": "-"}
            else:
                resultDict = {"domain": self.domain, "unitName": data[0]["company"],
                              "unitICP": data[0]["license"]}
        except Exception as e:
            resultDict = {"domain": self.domain, "unitName": "-", "unitICP": "-"}
        return resultDict


if __name__ == "__main__":
    fd = find_icp_by_domain("crccbfjy.com")
    result = fd.getICP_icplishi()
    # result = fd.get_ba1()
    print(result)