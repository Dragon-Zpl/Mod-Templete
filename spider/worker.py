import time
from abc import ABCMeta,abstractmethod

import requests
import schedule
from config.configs_ import *
from file_post.postModApp import PostModData
from spider.download import Downloader
from spider.fetcher import Fetch


class BaseWorker(metaclass=ABCMeta):
    def __init__(self, parser, filter, check_url=None, post_url=None):
        self.parser = parser()
        self.fetcher = Fetch(check_url=check_url)
        self.downloader = Downloader()
        self.filter = filter()
        self.PostModData = PostModData()
        self.post_url = post_url
    @abstractmethod
    def _get_crawler_url(self, *args, **kwargs)->set:
        """
        返回所有app详情的url
        :return: set
        """
        url_set = set()
        return url_set

    @abstractmethod
    def _get_apk_tpk_download_url(self, data)->(str,str):
        """
        获取apk tpk的下载地址
        :return:
        """

        apk_download_url = ""
        zip_download_url = ""
        return apk_download_url, zip_download_url

    def _info_parser(self, html):
        """
        来解析需要提取的信息
        :param html:
        :return: dict
        """
        return self.parser.parse(html=html)

    def _downloader(self, apk_url, unique, icon_url=None, app_name=None, zip_url=None, developer=None):
        """
        下载apk/tpk包，并把信息写入数据库
        :return:
        """
        self.downloader.run(apk_url, unique, icon_url, app_name, zip_url, developer)

    def post_to_weapp_(self, pkgname):
        """
        传到weapp后台
        :return:
        """
        return self.PostModData.run_post(pkgname,self.post_url)

    def _filter(self, *args, **kwargs):
        """
        过滤应用
        :return:
        """
        return self.filter.filter(*args, **kwargs)

    def _worker(self):
        url_list = self._get_crawler_url()
        tasks = []
        for url in url_list:
            task = self.fetcher.fetch(url)
            tasks.append(task)
        htmls = loop.run_until_complete(asyncio.gather(*tasks))
        results = []
        for html in htmls:
            if html:
                result_dict = {}
                result,unique = self._info_parser(html)
                if self._filter(result):
                    apk_download_url, zip_download_url = self._get_apk_tpk_download_url(result)
                    if "developer" in result.key():
                        download_result = self.downloader.run(apk_url=apk_download_url, unique=unique, icon_url=result["icon"],
                                                              app_name=result["name"], zip_url=zip_download_url, developer=result["developer"])
                    else:
                        download_result = self.downloader.run(apk_url=apk_download_url, unique=unique, icon_url=result["icon"],
                                                              app_name=result["name"], zip_url=zip_download_url)
                    result_dict["download_result"] = download_result
                    result_dict["info_result"] = result
                    self.post_to_weapp_(download_result['pkgname'])
                    results.append(result_dict)
        return results

    def run(self):
        """
        调用worker每天执行一次
        :return:
        """
        self._worker()
        schedule.every(1).days.do(self._worker)
        while True:
            schedule.run_pending()
            time.sleep(1)
