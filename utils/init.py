import logging.config
from config.read import *
import lxml.html
import urllib3
import aiohttp
import socket, asyncio
import redis
import yaml

from utils.mysql.AioMysqlHeaper import MysqlHeaper
from utils.mysql.mysql_heaper import MySql
from utils.project_helper import ProjectHepler

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
etree = lxml.html.etree
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:51.0) Gecko/20100101 Firefox/51.0',
}
conn = aiohttp.TCPConnector(family=socket.AF_INET,
                            verify_ssl=False,
                            use_dns_cache=True)
session = aiohttp.ClientSession(connector=conn)
loop = asyncio.get_event_loop()

pool = redis.ConnectionPool(host='192.168.9.149', password="a123456", port=6379, db=1)
rcon = redis.Redis(connection_pool=pool)

with open('./config/config.yaml', 'r') as fr:
    config_file = yaml.load(fr)
redis_topic = config_file["redis_topic"]["test"]

logging.config.dictConfig(configs.logger_dict)
logger = logging.getLogger('project')

VIDEOSTORE = "/home/feng/{}/google_files/video".format(ProjectHepler.get_basic_path(ProjectHepler.get_ip()))
IMGSTORE = "/home/feng/{}/google_files/picture".format(ProjectHepler.get_basic_path(ProjectHepler.get_ip()))

# 初始化数据库连接
tasks_get_db_pool = []
task_google = asyncio.ensure_future(MysqlHeaper().get_pool())
task_we = asyncio.ensure_future(MysqlHeaper().get_pool(config='We_mysql'))
tasks_get_db_pool.append(task_google)
tasks_get_db_pool.append(task_we)
loop.run_until_complete(asyncio.wait(tasks_get_db_pool))
we = task_we.result()
googleplay = task_google.result()

mysql = MySql()
des3 = config_file['DES3']
key = des3['key']
appkey = des3['appkey']