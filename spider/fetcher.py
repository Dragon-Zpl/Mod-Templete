from proxy.Domestic_Proxy import domestic_proxy
from proxy.Foreign_Proxy import foreign_Proxy
from config.configs_ import *
from asyncio import Lock
import random


class Fetch:

    def __init__(self, is_foreign: bool = True, check_url: str = None):
        if is_foreign:
            self.crawlProxy = foreign_Proxy(check_url)
        else:
            self.crawlProxy = domestic_proxy(check_url)
        self.proxies = []
        self.lock = Lock()

    async def fetch(self, url, headers=headers, proxy=None, times=3, etree_html=False):
        try:
            async with session.get(url, headers=headers, proxy=proxy, timeout=15) as r:
                if r.status in [200, 201]:
                    data = await r.text()
                    if etree_html:
                        data = etree.HTML(data)
                    return data
                elif r.status in [403, 400, 500, 502, 503, 429]:
                    if times > 0:
                        if proxy is not None:
                            proxy = await self.get_proxy()
                        return await self.fetch(url, headers=headers, proxy=proxy, times=times - 1, etree_html=True)
                    else:
                        return None
                else:
                    return None
        except Exception as e:
            # logger.info("error:{},url:{}".format(e, url))
            if times > 0:
                if proxy is not None:
                    proxy = await self.get_proxy()
                return await self.fetch(url, headers=headers, proxy=proxy, times=times - 1, etree_html=True)
            else:
                return None

    async def get_proxy_pool(self):
        async with self.lock:
            if len(self.proxies) <= 3:
                self.proxies = await self.crawlProxy.run(session)
                return self.proxies

    async def get_proxy(self):
        try:
            proxy = random.choice(self.proxies)
        except:
            await self.get_proxy_pool()
            if self.proxies:
                proxy = random.choice(self.proxies)
                return proxy
            else:
                return None
        return proxy
