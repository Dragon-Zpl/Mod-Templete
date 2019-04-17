from spider.fetcher import Fetch
from spider.filter import Filter
from spider.item import Item
from spider.parse import Parser
from spider.selector import *
from spider.worker import BaseWorker
from config.configs_ import *
mod_pkg_url = "https://www.androeed.ru/index.php?m=files&f=load_comm_dapda_otsosal_2_raza&ui="
host = "https://www.androeed.ru"
class Crawl(BaseWorker):
    def _get_crawler_url(self):
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
        content = etree.HTML(html)
        urls = content.xpath("//div[@class='while_apps']//div[@class='item_holder']/a/@href")
        for url in urls:
            print('url:'+url)
            url_set.add(host+url)

    def _get_apk_tpk_download_url(self, data):
        download_list = data["download_first_url"]
        apk_download_url = download_list[0]
        zip_download_url = ""
        if len(download_list) > 1 and download_list[1] != "need_info":
            zip_download_url = download_list[1]
        return apk_download_url, zip_download_url

class InfoItem(Item):
    categories = Xpath("//div[@class='info']//div[1]//a//text()")
    version = Xpath("//div[@class='info']//div[4]/text()")
    os = Xpath("//div[@class='info']//div[5]/text()")
    internet = Xpath("//div[@class='info']//div[6]/text()")
    size = Xpath("//div[@class='info']//div[7]/text()")
    pkg_name = Xpath("//h1[@itemprop='name']//text()")
    re_img_urls = Regex(r"\('#images_while'\)\.load[\d\D]+?\)")
    description = Xpath("//div[@itemprop='description']//text()")
    icon = Xpath("//meta[@property='og:image']/@content | //div[@class='c in_holder']/img/@data-src")
    app_url = Xpath("//meta[@property='og:type']/@content")
    mod_number = Xpath("//meta[@property='og:image']/@content")
    img_urls = Xpath("//div[@class='inl']/img/@data-src")

class info_parse(Parser):
    def __init__(self):
        self.fetch = Fetch()
    def _parse(self, html):
        item_dict = InfoItem(html)
        if type(item_dict["categories"]) == list:
            item_dict["categories"] = ','.join(item_dict["categories"])

        if item_dict["pkg_name"] and '[' in item_dict["pkg_name"]:
            item_dict["name"] = re.search(r'[\d\D]*\[', item_dict["pkg_name"]).group().replace(' [', "")
            item_dict["what_news"] = re.search("\[[\d\D]+?\]",item_dict["pkg_name"]).group().replace('[','').replace(']','')
        elif item_dict["pkg_name"] and '[' not in item_dict["pkg_name"]:
            item_dict["name"] = item_dict["pkg_name"]
            item_dict["what_news"] = ""
        else:
            item_dict["name"] = ""
            item_dict["what_news"] = ""
        item_dict["version"] = item_dict["version"].strip(" ")
        if type(item_dict["img_urls"]) == list:
            item_dict["img_urls"] = ','.join(item_dict["img_urls"])
        else:
            item_dict["img_urls"] = item_dict["re_img_urls"]
            if item_dict["img_urls"]:
                try:
                    temp = item_dict["img_urls"].replace("('#images_while').load('","").replace("\" ')","").replace("')","")
                    parameter1 = temp.split('&')[-2]
                    parameter2 = temp.split('&')[-1]
                    data = loop.run_until_complete(self.fetch.fetch(host + "/index.php?m=files&f=images_while&" + parameter1 + "&" + parameter2))
                    if data:
                        img_content = etree.HTML(data)
                        if img_content.xpath("//img/@src"):
                            item_dict["img_urls"] = ','.join(img_content.xpath("//img/@src"))
                        else:
                            item_dict["img_urls"] = ""
                    else:
                        item_dict["img_urls"] = ""
                except Exception as e:
                    logger.info("error:{},url:{}".format(e,item_dict["app_url"]))

        if len(item_dict["description"]) > 1:
            item_dict["description"] = ''.join(item_dict["description"])
        
        if item_dict["mod_number"]:
            temp = re.findall("\d+", item_dict["mod_number"])
            if temp:
                download_url = temp[-1]
                data = loop.run_until_complete(self.fetch.fetch(url=mod_pkg_url+download_url))
                if data:
                    try:
                        mod_content = etree.HTML(data)
                        download_url_len = len(mod_content.xpath("//a/@href"))
                        if download_url_len == 1 or download_url_len == 2:
                            temp_apk_download_url = mod_content.xpath("//a/@href")[-1]
                            data = loop.run_until_complete(self.fetch.fetch(url=temp_apk_download_url))
                            temp_apk_download_url_data = etree.HTML(data)
                            apk_download_url = temp_apk_download_url_data.xpath("//div[@class='c']/a[@class='download round30']/@href")[0]
                            if '.apk' in apk_download_url:
                                item_dict["download_first_url"] = [apk_download_url]
                            else:
                                item_dict["download_first_url"] = []
                                # self.bad_pkg_url.add(data_dic["app_url"])
                        elif download_url_len == 3:
                            # 第一个为破解包，第二个为apk包
                            temp_apk_download_url = mod_content.xpath("//a/@href")[-2]
                            data = loop.run_until_complete(self.fetch.fetch(url=temp_apk_download_url))
                            temp_apk_download_url_data = etree.HTML(data)
                            apk_download_url = temp_apk_download_url_data.xpath("//div[@class='c']/a[@class='download round30']/@href")[0]
                            temp_obb_download_url = mod_content.xpath("//a/@href")[-1]
                            data = loop.run_until_complete(self.fetch.fetch(url=temp_obb_download_url))
                            temp_obb_download_url_data = etree.HTML(data)
                            obb_download_url = temp_obb_download_url_data.xpath("//div[@class='c']/a[@class='download round30']/@href")[0]
                            if '.zip' in obb_download_url:
                                item_dict["download_first_url"] = [apk_download_url, obb_download_url]
                            else:
                                item_dict["download_first_url"] = [apk_download_url, 'need_info']
                                # self.bad_pkg_url.add(data_dic["app_url"])
                        elif download_url_len == 4:
                            temp_apk_download_url = mod_content.xpath("//a/@href")[-2]
                            data = loop.run_until_complete(self.fetch.fetch(url=temp_apk_download_url))
                            temp_apk_download_url_data = etree.HTML(data)
                            apk_download_url = temp_apk_download_url_data.xpath("//div[@class='c']/a[@class='download round30']/@href")[0]
                            item_dict["download_first_url"] = [apk_download_url]
                        else:
                            item_dict["download_first_url"] = []
                            logger.info('长度有问题请查看' + item_dict["app_url"])
                    except Exception as e:
                        logger.info("error:{},url:{}".format(e, item_dict["app_url"]))
                        item_dict["download_first_url"] = []
        print(item_dict)
        return item_dict, item_dict["name"]

class mod_filter(Filter):
    def filter(self, *args, **kwargs):
        return True

t = Crawl(info_parse, mod_filter, check_url="https://www.androeed.ru")
t.run()