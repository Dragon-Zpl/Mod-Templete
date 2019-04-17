import asyncio
import socket

import aiohttp

from lxml import etree


class domestic_proxy:
    def __init__(self, check_url="www.google.com", need_type=None):
        """

        :param check_url: need to check url
        :param need_type:http or https or None
        """
        self.check_url = check_url
        self.need_type = need_type
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
        }

    def build_async_tasks(self, session):
        print('创建任务队列')
        tasks = []
        for page in range(0, 20):
            if page == 0:
                url = 'https://www.xicidaili.com/nn/'
            else:
                url = 'https://www.xicidaili.com/nn/' + str(page)
            task = asyncio.ensure_future(self.crawl_web(url, session))
            tasks.append(task)
        return tasks

    async def crawl_web(self, url, session):
        try:
            print('进入爬取解析')
            async with session.get(url=url, headers=self.headers) as ct:
                text = await ct.text()
                content = etree.HTML(text)
                ip_list = content.xpath("//table[@id='ip_list']//tr[@class='odd']")
                all_proxy = []
                for oneip in ip_list:
                    # if oneip.xpath(".//td[6]/text()")[0].lower() == 'http':
                    if self.need_type:
                        if oneip.xpath(".//td[6]/text()")[0].lower() == self.need_type:
                            ipdic = {}
                            ipdic["ip"] = oneip.xpath(".//td[2]/text()")[0]
                            ipdic["port"] = oneip.xpath(".//td[3]/text()")[0]
                            ipdic["addr"] = ''.join(oneip.xpath(".//td[4]//text()"))
                            ipdic["hide"] = oneip.xpath(".//td[5]/text()")[0]
                            ipdic["type"] = oneip.xpath(".//td[6]/text()")[0].lower()
                            ipdic["savetime"] = oneip.xpath(".//td[9]/text()")[0]
                            ipdic["updatetime"] = oneip.xpath(".//td[10]/text()")[0]
                            all_proxy.append(ipdic)
                    else:
                        ipdic = {}
                        ipdic["ip"] = oneip.xpath(".//td[2]/text()")[0]
                        ipdic["port"] = oneip.xpath(".//td[3]/text()")[0]
                        ipdic["addr"] = ''.join(oneip.xpath(".//td[4]//text()"))
                        ipdic["hide"] = oneip.xpath(".//td[5]/text()")[0]
                        ipdic["type"] = oneip.xpath(".//td[6]/text()")[0].lower()
                        ipdic["savetime"] = oneip.xpath(".//td[9]/text()")[0]
                        ipdic["updatetime"] = oneip.xpath(".//td[10]/text()")[0]
                        all_proxy.append(ipdic)
                return all_proxy
        except Exception as e:
            pass

    async def check_proxy(self, ipdic, session):
        print(ipdic)
        proxy = ipdic["type"] + '://' + ipdic["ip"] + ":" + ipdic["port"]
        print("proxy:" + str(proxy))
        try:
            async with session.get(url=self.check_url, headers=self.headers, proxy=proxy, timeout=10) as ct:
                if ct.status in [200, 201]:
                    print(ct.status)
                    return proxy
        except Exception as e:
            pass

    def run(self, session=None):
        proxies = []
        loop = asyncio.get_event_loop()
        if session is None:
            conn = aiohttp.TCPConnector(family=socket.AF_INET,
                                        verify_ssl=False,
                                        use_dns_cache=True)
            session = aiohttp.ClientSession(connector=conn)
        tasks = self.build_async_tasks(session)
        results = loop.run_until_complete(asyncio.gather(*tasks))
        check_tasks = []
        for proxy in results:
            for ipdic in proxy:
                task = asyncio.ensure_future(self.check_proxy(ipdic, session))
                check_tasks.append(task)
        results = loop.run_until_complete(asyncio.gather(*check_tasks))
        if results:
            for proxy in results:
                if proxy:
                    proxies.append(proxy)
        return proxies

