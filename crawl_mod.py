from spider.item import Item
from spider.parse import Parser
from spider.selector import Xpath
from spider.worker import BaseWorker
from config.configs_ import *

class Crawl(BaseWorker):
    def _get_crawler_url(self):
        print('start')
        tasks = []
        mods_urls = ["https://www.androeed.ru/files/vzlomannie_igri_na_android-" + str(page) + ".html?hl=en" for
                          page in range(1, 6)]
        app_url = "https://www.androeed.ru/android/programmy.html?hl=en"
        task = asyncio.ensure_future(self.fetcher.fetch(url=mods_urls[0]))
        tasks.append(task)
        task = asyncio.ensure_future(self.fetcher.fetch(app_url))
        tasks.append(task)
        results = loop.run_until_complete(asyncio.gather(*tasks))
        url_set = set()
        for html in results:
            if html:
                self.get_url_parse(html, url_set)
        return url_set

    def get_url_parse(self, html, url_set):
        host = "https://www.androeed.ru"
        content = etree.HTML(html)
        urls = content.xpath("//div[@class='while_apps']//div[@class='item_holder']/a/@href")
        for url in urls:
            print('url:'+url)
            url_set.add(host+url)
    def _get_apk_tpk_download_url(self):
        pass


class InfoItem(Item):
    get_app_urls = Xpath("//div[@class='while_apps']//div[@class='item_holder']/a/@href")
    categories = Xpath("//div[@class='info']//div[1]//a//text()")
    version = Xpath("//div[@class='info']//div[4]/text()")
    os = Xpath("//div[@class='info']//div[5]/text()")
    internet = Xpath("//div[@class='info']//div[6]/text()")
    size = Xpath("//div[@class='info']//div[7]/text()")
    raiting = Xpath("//div[@class='info']//div[8]/text()")
    russian = Xpath("//div[@class='info']//div[9]/text()")
    pkg_name = Xpath("//h1[@itemprop='name']//text()")
    img_urls = Xpath("//img/@src")
    description = Xpath("//div[@itemprop='description']//text()")
    icon = Xpath("//meta[@property='og:image']/@content | //div[@class='c in_holder']/img/@data-src")
    download_first_url = Xpath("//a/@href")
    download_second_url = Xpath("//a[@id='download_up']/@href")
    md5 = Xpath("//div[@class='c']//strong/text()")
    app_url = Xpath("//meta[@property='og:type']/@content")
    mod_number1 = Xpath("//a[@class='google_play round5']/@href")
    mod_number2 = Xpath("//meta[@property='og:image']/@content")
    pkg_download_url = Xpath("//div[@class='c']/a[@class='download round30']/@href")
    img_urls2 = Xpath("//div[@class='inl']/img/@data-src")

class info_parse(Parser):
    def _parse(self, html:str):
        item_dict = InfoItem(html)
        print('item_dict:'+str(item_dict))
        return item_dict

t = Crawl(info_parse)
t.run()