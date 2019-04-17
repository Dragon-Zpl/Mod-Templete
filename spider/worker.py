import time
from abc import ABCMeta,abstractmethod

import requests
import schedule
from config.configs_ import *
from spider.download import Downloader
from spider.fetcher import Fetch


class BaseWorker(metaclass=ABCMeta):
    def __init__(self, parser, *, url=None, mysql_helper=None, filter=None, PostModData=None, check_url=None):
        self.crawler_url = url
        self.parser = parser()
        self.mysql_helper = mysql_helper()
        self.fetcher = Fetch(check_url=check_url)
        self.downloader = Downloader()
        self.filter = filter()
        self.PostModData = PostModData()

    @abstractmethod
    def _get_crawler_url(self, *args, **kwargs):
        """
        返回所有app详情的url
        :return: list
        """
        print('this is yuanlei')
        url_list = []
        return url_list

    @abstractmethod
    def _get_apk_tpk_download_url(self, *args, **kwargs):
        """
        获取apk tpk的下载地址 和 类型
        :return:
        """

        url = ()
        app_type = ""
        return url, app_type

    def _info_parser(self, html):
        """
        来解析需要提取的信息
        :param html:
        :return: dict
        """
        print('into info_parse')
        return self.parser.parse(html=html)

    def _compare_version(self, old_version:str, new_version:str) ->bool:
        """
        对比数据库版本
        :param old_version:
        :param new_version:
        :return:
        """
        if type(old_version) is not str or new_version is not str:
            raise Exception("old_version or new_version is not str")

        if old_version == new_version:
            return True
        else:
            return False

    def _downloader(self, apk_url, unique, icon_url=None, app_name=None, zip_url=None, developer=None):
        """
        下载apk/tpk包，并把信息写入数据库
        :return:
        """
        self.downloader.run(apk_url, unique, icon_url, app_name, zip_url, developer)

    def post_to_weapp_(self, pkgname, post_url):
        """
        传到weapp后台
        :return:
        """
        return self.PostModData.run_post(pkgname, post_url)

    def _filter(self, *args, **kwargs):
        """
        过滤应用
        :return:
        """
        return self.filter.filter(*args, **kwargs)

    def _worker(self):
        url_list = self._get_crawler_url()
        # todo 获取html
        tasks = []
        for url in url_list:
            task = self.fetcher.fetch(url)
            tasks.append(task)
        htmls = loop.run_until_complete(asyncio.gather(*tasks))
        results = []
        for html in htmls:
            if html:
                result = self._info_parser(html)
                results.append(result)
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
