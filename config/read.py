
import collections


# todo read 配置文件


configs = collections.namedtuple("configs", "mysql, DES3, redis, logger_dict, email, tables, es, path")

configs.redis = {
    "host": "192.168.9.149",
    "password": "a123456",
    "port": "6379",
    "db": "1",
}

configs.mysql = {"host": "120.79.2.95",
                 "port": "3306",
                 "user": "root",
                 "password": "",
                 "database": "google_play",
                 "charset": "utf8"}

configs.DES3 = {"key": "4d9f0c946572aa6e6d34f2db",
                "appkey": "tutuappandroidweb"}

configs.logger_dict = {'version': 1, 'disable_existing_loggers': False, 'formatters': {'simple': {'format': '%(asctime)s - %(filename)s - %(lineno)s %(levelname)s - %(message)s'}}, 'handlers': {'console': {'class': 'logging.StreamHandler', 'level': 'DEBUG', 'formatter': 'simple', 'stream': 'ext://sys.stdout'}}, 'loggers': {'my_module': {'level': 'ERROR', 'handlers': ['console'], 'propagate': False}}, 'root': {'level': 'INFO', 'handlers': ['console']}}

configs.email = {
    "sender": "786283772@qq.com",
    "host": "smtp.qq.com",
    "user": "786283772@qq.com",
    "password": "lxnctbyxqaupbbha",
    "from": "破解包测试",
    "subject": "这就是个测试",
}

configs.tables = {
    "app_table": "crawl_androeed_app_info",
    "apk_table": "crawl_androeed_apk_info",
    "cover_table": "crawl_androeed_coverimg",
    "screen_table": "crawl_androeed_screenshots",
}

configs.es = {
    "ip": "",
    "port": "",
    "index": "",
    "doc_type": "",
}

configs.path = {
    "basic_path": "/home/feng/pkgtest/",
    "apk_path": "/home/feng/pkgtest/app_page/",
    "cover_path": "/home/feng/pkgtest/picture/coverimg",
    "screen_path": "/home/feng/pkgtest/picture/screenshot",
}