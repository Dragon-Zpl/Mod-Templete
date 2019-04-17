import aiomysql
from config.configs_ import *
from config.read import *

class MysqlOps:
    """
    异步mysql class
    """

    """
    数据库操作
    """
    def __init__(self):
        self.app_table = configs.tables['app_table']
        self.apk_table = configs.tables['apk_table']
        self.icon_table = configs.tables['cover_table']
        self.screen_table = configs.tables['screen_table']
        self.logger = logger
        self.pool = pool

    async def get_pool(self, loop=None):

        local_mysql_config = configs.mysql
        self.pool = await aiomysql.create_pool(host=local_mysql_config["host"], port=local_mysql_config["port"],
                                               user=local_mysql_config["user"], password=local_mysql_config["password"],
                                               db=local_mysql_config["database"], loop=loop,
                                               charset=local_mysql_config["charset"], autocommit=True)
        return self

    def insert_or_update_or_delete_app_info(self, info:dict) -> bool:
        sqlStr = """
                                 insert into {} (category,appsize,contentrating,current_version,description,developer,whatsnew,
                                           instalations,last_updatedate,minimum_os_version,name,pkgname,price,reviewers,url) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                                           ON DUPLICATE KEY UPDATE appsize=VALUES(appsize),category=VALUES(category),contentrating=VALUES(contentrating),
                                           current_version=VALUES(current_version),description=VALUES(description),developer=VALUES(developer),whatsnew=VALUES(whatsnew),
                                           instalations=VALUES(instalations),last_updatedate=VALUES(last_updatedate),minimum_os_version=VALUES(minimum_os_version),name=VALUES(name),price=VALUES(price)
                             """.format(self.app_table)
        # nowtime = (datetime.datetime.now() + datetime.timedelta(hours=13)).strftime("%Y-%m-%d %H:%M:%S")
        params = tuple(info.values())
        task = asyncio.ensure_future(self.insert_or_update_or_delete(sqlStr,params))
        loop.run_until_complete(task)
        if task.result():
            return True
        else:
            return False

    def insert_or_update_or_delete_apk_info(self, info:dict) -> bool:
        sqlStr = """
                                 insert into {} (pkg_name, file_sha1, is_delete, file_path, create_time, update_time) VALUES (%s,%s,%s,%s,%s,%s)
                                 ON DUPLICATE KEY UPDATE file_sha1=VALUES(file_sha1), is_delete=VALUES(is_delete), file_path=VALUES(file_path), update_time=VALUES(update_time)
                             """.format(self.apk_table)
        # nowtime = (datetime.datetime.now() + datetime.timedelta(hours=13)).strftime("%Y-%m-%d %H:%M:%S")
        params = tuple(info.values())
        task = asyncio.ensure_future(self.insert_or_update_or_delete(sqlStr,params))
        loop.run_until_complete(task)
        if task.result():
            return True
        else:
            return False

    def get_app_version(self, pkgname:str) -> str:
        sqlStr = 'select currentversion from crawl_google_play_app_info where pkgname=\'{}\''.format(pkgname)
        task = asyncio.ensure_future(self.fetch_one(sqlStr))
        loop.run_until_complete(task)
        if task.result():
            return task.result()
        else:
            return None

    def insert_or_update_or_delete_icon_info(self, info:dict) -> bool:
        sqlStr = """insert into {}(url,coverimg_path,romote_url,type,is_success_downland,need_update,create_date) VALUES (%s,%s,%s,%s,%s,%s,%s)
                                     ON DUPLICATE KEY UPDATE coverimg_path=VALUES(coverimg_path), type=VALUES(type), is_success_downland=VALUES(is_success_downland), need_update=VALUES(need_update)
                                   """.format(self.icon_table)

        params = tuple(info.values())
        task = asyncio.ensure_future(self.insert_or_update_or_delete(sqlStr,params))
        loop.run_until_complete(task)
        if task.result():
            return True
        else:
            return False

    def insert_or_update_or_delete_screen_info(self, info:dict) -> bool:
        sqlStr = """insert into {}(url,screenshot_path,romote_url,type,is_success_downland,need_update,create_date,update_date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                          ON DUPLICATE KEY UPDATE screenshot_path=VALUES(screenshot_path), type=VALUES(type), is_success_downland=VALUES(is_success_downland), need_update=VALUES(need_update),update_date=VALUES (update_date)
                        """.format(self.screen_table)

        params = tuple(info.values())
        task = asyncio.ensure_future(self.insert_or_update_or_delete(sqlStr, params))
        loop.run_until_complete(task)
        if task.result():
            return True
        else:
            return False

    async def insert_or_update_or_delete(self, sql, params=None):
        try:
            if self.pool:
                pass
            else:
                await self.get_pool()
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cur:
                    results = await cur.execute(sql, params)
                    return results
        except Exception as e:
            self.logger.error("{} {}".format(e,params))
            await self.get_pool()
            return None

    async def fetch_one(self, sql, params=None):
        if self.pool:
            pass
        else:
            await self.get_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(sql, params)
                    recond = await cur.fetchone()
                    return recond
                except Exception as e:
                    print(e)
                    return None


    async def fetch_all(self,sql,params=None):
        if self.pool:
            pass
        else:
            await self.get_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(sql, params)
                    recond = await cur.fetchall()
                    return recond
                except Exception as e:
                    return None