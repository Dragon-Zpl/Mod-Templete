import base64
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import time
from Crypto.Cipher import DES3
import requests
from config.configs_ import *
PKGSTORE = configs.path["apk_path"]
key = configs.DES3["key"]
appkey = configs.DES3["appkey"]
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        return json.JSONEncoder.default(self, obj)

class Downloader:
    """
    下载apk 合成tpk包 wget
    """
    def _file_path_detail(self):
        now = datetime.datetime.now()
        now_date = now.strftime('%Y-%m-%d')
        download_dir = PKGSTORE + now_date + "/"
        return download_dir

    def _runProcess(self, commandString):
        p = subprocess.Popen(commandString, shell=True, stderr=subprocess.PIPE)
        err, output = p.communicate()
        if err:
            return False
        else:
            return True

    def _download_pkg(self, download_url, apk_path):
        msg = self._runProcess("wget --no-check-certificate --output-document \"" + apk_path + "\" \"" + download_url + "\"")
        if msg:
            return apk_path
        else:
            return None

    def _download_zip(self, download_url, zip_path):
        msg = self._runProcess("wget --no-check-certificate --output-document \"" + zip_path + "\" \"" + download_url + "\"")
        if msg:
            return zip_path
        else:
            return None

    def configinfo(self, name, apk_path, zip_path, developer=None):
        """

        :param name:
        :param apk_path:
        :param zip_path:
        :param developer:
        :return:apk_info and obb_path
        """
        aapk_str = 'aapt dump badging {} > tmp.txt'.format(apk_path)
        os.system(aapk_str)
        with open('tmp.txt', 'r', encoding='utf8', errors='ignore') as f:
            result = f.readlines()
        results = ''.join(result)
        try:
            pkgname = re.search(r'package: name=\'(.*?)\'', results).group(1)
        except:
            os.remove(apk_path)
            os.remove(zip_path)
            return
        file_dir = zip_path.split('/')[:-1]
        file_dir = '/'.join(file_dir)
        sys_str = "cd " + file_dir + " && unzip -t {}".format(zip_path)
        f = os.popen(sys_str)
        # 删除zip文件
        result_unzip = f.readlines()
        result_unzip = ''.join(result_unzip)
        try:
            obbname = re.search(r'.*?ing.*?/(.*?obb).*', result_unzip).group(1)
        except:
            return None,None
        unzip_str = 'cd ' + file_dir + " && unzip -j {}".format(zip_path)
        os.system(unzip_str)
        new_obb_path = file_dir + '/' + obbname

        delete_command = 'rm -rf {} {} {}'.format(zip_path, file_dir + '/' + 'Read*', file_dir + '/' + 'ReXdl.com.url')
        os.system(delete_command)

        app_version_code = re.search(r'versionCode=\'(.*?)\'', results).group(1)
        app_version = re.search(r'versionName=\'(.*?)\'', results).group(1)
        apkfile_size = os.path.getsize(apk_path)
        obbfile_size = os.path.getsize(new_obb_path)
        if developer is None:
            developer = self.get_app_other_info(pkgname)
        data_path = '/sdcard/android/obb/' + pkgname + '/'
        dict_tpk = {
            'app_name': name,
            'pkg_name': pkgname,
            'app_version': app_version,
            'app_version_code': app_version_code,
            'developer': developer,
            'apksize': str(apkfile_size),
            'data_path': data_path,
            'data_size': str(obbfile_size)
        }
        return dict_tpk,new_obb_path

    def get_app_other_info(self,pkgname):
        #开发者信息
        url = 'https://play.google.com/store/apps/details?id=' + pkgname
        google_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36',
            'origin': 'https://play.google.com',
            'x-client-data': 'CKC1yQEIlrbJAQiitskBCMG2yQEImpjKAQipncoBCKijygE=',
            'Content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'upgrade-insecure-requests': '1'
        }
        response = requests.get(url, headers=google_headers)
        if response.status_code == 200:
            html = etree.HTML(response.text)
            developer = html.xpath("//span[@class='T32cc UAO9ie'][1]/a[@class='hrTbp R8zArc']/text() | //div[@class='info-container']//div[@itemprop='author']/a/span[@itemprop='name']/text()")[0]
            return developer

    def _build_tpk(self, basic_dir, obbpath, dict_tpk, image_url, unique):
        tpkdir = basic_dir + hashlib.md5((unique).encode('utf-8')).hexdigest()
        config_info = self.encryptapkinfo(dict_tpk, key, appkey)
        self._writeencryptapkinfo(config_info, tpkdir)
        self.downIcon(tpkdir,image_url)
        obbname = obbpath.split('/')[-1]
        logger.info(obbname)
        detfile_obb = tpkdir + '/data/' + obbname
        self._mymovefile(obbpath, detfile_obb)

        apkpath = tpkdir + ".apk"

        detfile_apk = tpkdir + '/pkg.apk'
        self._mymovefile(apkpath, detfile_apk)

        tpkfilename = tpkdir.split('/')[-1]
        tpkfilename = ''.join(tpkfilename)
        zip_str = 'cd ' + tpkdir + ' && zip -r ' + tpkfilename + '.tpk *'

        os.system(zip_str)

        self._mymovefile(tpkdir + '/' + tpkfilename + '.tpk', basic_dir + tpkfilename + '.tpk')
        del_srcfile = 'rm -fr ' + tpkdir
        os.system(del_srcfile)
        return basic_dir + tpkfilename + '.tpk'

    def encryptapkinfo(self, data, key, appkey):
        data['expired_date'] = int(time.time()) + 12 * 60 * 60
        data = json.dumps(data)
        iv = 'wEiphTn!'
        block_size = DES3.block_size
        logger.info('block_size is {} is {}'.format(block_size, block_size % 8 == 0))
        PADDING = lambda s: s + (block_size - len(s) % block_size) * chr(block_size - len(s) % block_size)
        des3 = DES3.new(key, DES3.MODE_CBC, iv)
        ciphertext = base64.b64encode(des3.encrypt(PADDING(data)))
        str_ciphertext = str(ciphertext, encoding='utf-8')
        verify = hashlib.md5(
            (hashlib.md5(appkey.encode('utf-8')).hexdigest() + key + str_ciphertext).encode(
                'utf-8')).hexdigest()
        cbc_base = base64.b64encode((json.dumps(
            {'app_key': hashlib.md5(appkey.encode('utf-8')).hexdigest(), 'encrypt_data': ciphertext,
             'verify': verify}, cls=MyEncoder)).encode('utf-8'))
        return cbc_base

    def _writeencryptapkinfo(self, config_info, tpkdir):
        des3_configinfo = config_info
        if not os.path.exists(tpkdir):
            os.makedirs(tpkdir)
        config_path = os.path.join(tpkdir, 'config')
        with open(config_path, 'w') as fp:
            fp.write(des3_configinfo.decode())

    def downIcon(self, tpkdir, image_url):
        try:
            image_response = requests.get(image_url, verify=False).content
            image_path = os.path.join(tpkdir, r'icon.png')
            with open(image_path, 'wb') as fp:
                fp.write(image_response)
            return True
        except Exception as e:
            return False
    
    def _mymovefile(self, srcfile, dstfile):
        if not os.path.isfile(srcfile):
            logger.info("%s, %s not exist!" % (srcfile,dstfile))
        else:
            fpath, fname = os.path.split(dstfile)  # 分离文件名和路径
            if not os.path.exists(fpath):
                os.makedirs(fpath)  # 创建路径
            shutil.move(srcfile, dstfile)  # 移动文件
            logger.info("move %s -> %s" % (srcfile, dstfile))

    def run(self, apk_url, unique, icon_url=None, app_name=None, zip_url=None, developer=None):
        """
        暴露的接口
        :return: apk的信息
        """
        logger.info('{} start download'.format(app_name))
        msg = {"apkpath": "", "error": ""}
        try:
            basic_dir = self._file_path_detail()
            if not os.path.exists(basic_dir):
                os.makedirs(basic_dir)
            basic = basic_dir + hashlib.md5((unique).encode('utf-8')).hexdigest()
            apk_path = basic + '.apk'
            self._download_pkg(apk_url, apk_path)
            msg["apkpath"] = apk_path
            if zip_url:
                zip_path = basic + '.zip'
                self._download_zip(zip_url, zip_path)
                dict_tpk, obb_path = self.configinfo(app_name, apk_path, zip_path, developer)
                msg["pkgname"] = dict_tpk["pkg_name"]
                if dict_tpk and obb_path:
                    tpk_path = self._build_tpk(basic_dir, obb_path, dict_tpk, icon_url, unique)
                    msg["apkpath"] = tpk_path
                else:
                    msg["error"] = "obb download faile,can,t build tpk"
            else:
                aapk_str = 'aapt dump badging {} > tmp.txt'.format(apk_path)
                os.system(aapk_str)
                with open('tmp.txt', 'r', encoding='utf8', errors='ignore') as f:
                    result = f.readlines()
                results = ''.join(result)
                try:
                    pkgname = re.search(r'package: name=\'(.*?)\'', results).group(1)
                    msg["pkgname"] = pkgname
                    logger.info("pkgname is {}".format(pkgname))
                except:
                    logger.info("re pkgname error")
                    return
        except Exception as e:
            msg["error"] = str(e)
        logger.info('download end :{}'.format(str(msg)))
        return msg