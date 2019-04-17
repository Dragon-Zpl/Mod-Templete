import json, requests
import random, base64, hashlib
from datetime import datetime, date
from spider.mysql_ops import MysqlOps
from config.configs_ import *

class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        else:
            return json.JSONEncoder.default(self, obj)


class PostModData:
    def __init__(self):
        self.mysql_op = MysqlOps()


    def run_post(self, pkgname, post_url):
        data_list = []
        pkgname_url_list = []
        # 查询未同步的app
        # sql = "SELECT detail_url FROM androidmod_app_info WHERE is_info_synced=0 AND is_sync_failed=0"
        sql = "select pkg_name from {} WHERE pkg_name=\'{}\' and is_delete=0".format(configs.tables["apk_table"], pkgname)
        # sql = "select pkg_name from apkdlmod_apk_info WHERE id<800"
        url_reconds = loop.run_until_complete(self.mysql_op.fetch_one(sql))
        if url_reconds != None:
            sql = "select * from {} WHERE pkgname=\'{}\'".format(configs.tables["app_table"],
                pkgname)  # AND is_info_synced=0 AND is_sync_failed=0"
            recond_all = loop.run_until_complete(self.mysql_op.fetch_all(sql))
            if recond_all:
                recond_all = recond_all[0]
                appinfo_dict = {}
                appinfo_dict['filebundleid'] = pkgname
                appinfo_dict['appDevelopers'] = recond_all[6]
                appinfo_dict['categoryCode'] = recond_all[2]
                appinfo_dict['appUpdateDate'] = recond_all[8]
                appinfo_dict['storeCode'] = 'en'
                sql_cover = "select {} from crawl_androeed_coverimg where url=\'{}\'".format(configs.tables["cover_table"],
                    recond_all[-3])
                coverRomoteUrl = loop.run_until_complete(self.mysql_op.fetch_all(sql_cover))
                if coverRomoteUrl:
                    appinfo_dict['coverRomoteUrl'] = coverRomoteUrl[0][0].replace('/home/feng/android_files1',
                                                                                  'http://crawer2.tutuapp.net:8080/')
                else:
                    appinfo_dict['coverRomoteUrl'] = ""
                sql_screens = "select {} from crawl_androeed_screenshots where url=\'{}\'".format(configs.tables["screen_table"],
                    recond_all[-3])
                recond_screens = loop.run_until_complete(self.mysql_op.fetch_all(sql_screens))
                logger.info(recond_screens)
                if recond_screens:
                    recond_screens = recond_screens[0][0]
                    recond_screens = recond_screens.split(',')
                    re_reconds = []
                    try:
                        for recond in recond_screens:
                            recond = ''.join(recond)
                            recond = recond.replace('/home/feng/android_files1', 'http://crawer2.tutuapp.net:8080/')
                            re_reconds.append(recond)
                        appinfo_dict['screenshots'] = re_reconds
                    except:
                        appinfo_dict['screenshots'] = ""
                else:
                    appinfo_dict['screenshots'] = ""
                country_appinfo = {}

                country_appinfo['en'] = {'appName': recond_all[10] + ' MOD', 'appIntroduction': recond_all[5],
                                         'appRecentChanges': '', 'currencyCode': 'USD', 'appPrice': '0',
                                         'compatibility': ""}
                appinfo_dict['localization'] = country_appinfo
                appinfo_dict['source'] = 'p'
                if appinfo_dict['filebundleid']:
                    appinfo_dict['filebundleid'] = appinfo_dict['filebundleid']
                    sql_apk = "select file_path,file_sha1 from {} WHERE pkg_name=\'{}\' and is_delete=0".format(configs.tables["apk_table"],
                        appinfo_dict['filebundleid'])
                    file_info = {}
                    recond = loop.run_until_complete(self.mysql_op.fetch_all(sql_apk))
                    logger.info(recond)
                    if recond:
                        recond = recond[0]
                        apk_path = ''.join(recond[0])
                        apk_path = apk_path.replace('/home/feng/android_files1', 'http://crawer2.tutuapp.net:8080/')
                        file_info['downloadUrl'] = apk_path
                        file_info['fileMd5'] = ''.join(recond[1])
                        file_info['callbackUrl'] = 'http://23.236.115.227:5000/api/v1.0/deleteapk/p/' + appinfo_dict[
                            'filebundleid']
                        file_info["weight"] = 5
                    appinfo_dict['fileInfo'] = file_info
                    data_list.append(appinfo_dict)
                    # print(appinfo_dict)
                    return self.pack_data(data_list,post_url)
                else:
                    # 丢弃未下载到apk的数据
                    return None

    def pack_data(self, data_list, url):
        rdstr = self.randonstr()
        skey = "OHDKD*&HJldhkfg"
        # 转化为json格式
        appinfo = json.dumps(data_list, ensure_ascii=False, cls=CJsonEncoder)
        data = base64.b64encode(appinfo.encode('utf-8'))
        sign = hashlib.md5((str(data, encoding='utf-8') + skey + rdstr).encode('utf-8')).hexdigest()
        post_data = {
            'data': data,
            'sign': sign,
            'oncestr': rdstr
        }
        try:
            r = requests.post(url, data=post_data,
                              timeout=60)
            return r.text
        except Exception as e:
            return None



    def randonstr(self):
        seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        sa = []
        for i in range(8):
            sa.append(random.choice(seed))
        salt = ''.join(sa)
        return salt