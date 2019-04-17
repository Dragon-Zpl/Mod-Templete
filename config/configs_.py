import logging.config
import asyncio
import socket

import aiohttp
import redis
from lxml import etree
import aiomysql

from config.read import configs

logging.config.dictConfig(configs.logger_dict)
logger = logging.getLogger('project')
loop = asyncio.get_event_loop()


async def get_pool(loop=None):
    local_mysql_config = configs.mysql
    pool = await aiomysql.create_pool(host=local_mysql_config["host"], port=local_mysql_config["port"],
                                           user=local_mysql_config["user"], password=local_mysql_config["password"],
                                           db=local_mysql_config["database"], loop=loop,
                                           charset=local_mysql_config["charset"], autocommit=True)
    return pool


pool = loop.run_until_complete(get_pool(loop))

etree = etree

_connect = redis.ConnectionPool(host=configs.redis["host"], password=configs.redis["password"], port=configs.redis["port"], db=configs.redis["db"])
rcon = redis.Redis(connection_pool=_connect)

conn = aiohttp.TCPConnector(family=socket.AF_INET,
                            verify_ssl=False,
                            use_dns_cache=True)
session = aiohttp.ClientSession(connector=conn)

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:51.0) Gecko/20100101 Firefox/51.0',
}