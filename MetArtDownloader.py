from typing import Any
import urllib.request
import re
import os
import time
import hashlib
from threading import Thread
from configparser import ConfigParser
import pathlib
# from bs4 import BeautifulSoup


def urllib_request_Request(url, port=23333):
    proxy_handler = urllib.request.ProxyHandler({
        'http': 'http://127.0.0.1:' + str(port),
        'https': 'https://127.0.0.1:' + str(port)
    })
    opener = urllib.request.build_opener(proxy_handler)
    # print(response.read())
    return opener.open(url)


def get_config_file() -> str:
    config_file = 'MetArtDownloader.config.ini'
    app_dir = pyinstaller_getcwd()
    return os.path.join(app_dir, config_file)


def get_download_path_not_none(download_path: str, config_file: str):
    if (not pathlib.Path(download_path).exists()):
        if os.name == "nt":
            download_path = f"{os.getenv('USERPROFILE')}\\Downloads"
        else:  # PORT: For *Nix systems
            download_path = f"{os.getenv('HOME')}/Downloads"
        print(
            f'\n!  WARNING: STRONGLY RECOMMENDED TO SPECIFY YOUR download_path in "{config_file}"\n    Now use "{download_path}"')
        save_download_path_to_config(download_path, config_file)
    print(f"> download_path = {download_path}")
    return download_path


def save_download_path_to_config(download_path: str, config_file: str):
    config = ConfigParser()
    if (os.path.exists(config_file)):
        try:
            with open(config_file) as f:
                config.read_file(f)
            config.set('Settings', 'download_path', download_path)
            with open(config_file, 'w') as f:
                config.write(f)
        except Exception as e:
            print(f"! {str(e)}")


def get_download_path(config_file: str):
    config = ConfigParser()
    if (os.path.exists(config_file)):
        try:
            with open(config_file) as f:
                config.read_file(f)
                return get_download_path_not_none(config['Settings']['download_path'], config_file)
        except:
            return get_download_path_not_none("ERROR_OCCUR", config_file)
    else:
        config.add_section('Settings')
        config['Settings']['download_path'] = "NOT_SET"
        with open(config_file, 'w') as f:
            config.write(f)
    return get_download_path_not_none("NOT_SET", config_file)


def pyinstaller_getcwd():
    import os
    import sys
    # determine if the application is a frozen `.exe` (e.g. pyinstaller --onefile)
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    # or a script file (e.g. `.py` / `.pyw`)
    elif __file__:
        application_path = os.path.dirname(os.path.abspath(__file__))
    return application_path


class Spider:
    def __init__(self, url, path, black_list=None, white_list=None, need_open=True):
        self.url = url
        self.user_agent = "user-agent: Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Mobile Safari/537.36 Edg/89.0.774.68"
        self.params = {'utm_source': 'newsletter',
                       'utm_medium': 'email',
                       'utm_campaign': 'Top10'}
        self.headers = {"Referer": self.url, "User-Agent": self.user_agent}
        self.time = 0.00
        self.need_open = need_open
        self.model = None
        self.path = path
        self._black_list = black_list
        self._white_list = white_list
        url_hash = hashlib.md5(self.url.encode("utf8")).hexdigest()
        tmp_folder = os.path.join(self.path, '_tmp')
        self.mkdir(tmp_folder)
        self.contents_file = os.path.join(tmp_folder, url_hash + '.txt')
        self.succeed_flag = os.path.join(tmp_folder, url_hash + '-succeed.txt')
        self.skip_flag = os.path.join(tmp_folder, url_hash + '-skip.txt')
        # req.add_header("Host","blog.csdn.net")
        # req.add_header("Referer","http://blog.csdn.net/")

    def getPage(self):
        if os.path.exists(self.contents_file):
            print("RETRY")
            with open(self.contents_file, 'r', encoding='utf-8') as f:
                return f.read()
        # request = urllib.request.Request(self.url, headers=self.headers)
        try:
            import requests
            # 此处也可以通过列表形式，设置多个代理IP，后面通过random.choice()随机选取一个进行使用
            # proxies = {'http': 'http://127.0.0.1:23333',
            #         'https': 'http://127.0.0.1:23333'}
            # ,
            import urllib
            proxies = urllib.request.getproxies()
            # print(proxies)
            json_url = re.findall('subscription/preview/(.*)/', self.url)[0]
            json_url = 'https://www.metart.com/api/subscription-preview/' + json_url
            # print(json_url)

            self.url = json_url
            # proxies=proxies,
            # params=self.params,
            response = requests.get(url=self.url, headers=self.headers)
            # url_content_list = url_content.strip().splitlines()
            contents = response.text
        except Exception as e:
            print(e)
            return None
        else:
            if (re.findall(r'pcdn\.metartnetwork\.com', contents, re.IGNORECASE)):
                with open(self.contents_file, 'w', encoding='utf-8') as f:
                    f.write(contents)
                return contents
            else:
                print("URL WRONG!")
                return None

    def getContents(self):
        page = self.getPage()
        import json
        user_dic = json.loads(page)
        model_name = user_dic['models'][0]['name']
        model_img_urls = user_dic['images']
        contents = list()
        for url in model_img_urls:
            filename = re.search(r'filename=(.+\.jpg)', url).group(1)
            # https://pcdn.metartnetwork.com/E6B595104E3411DF98790800200C9A66/media/9365AE2D434A1064E983A8629DECCB41/l_AA3CBBA100B18E84A197BC882E9B126D.jpg?filename=MetArt_Perfect-Art_Melena-A_low_0004.jpg&type=inline&ttl=1581770973&token=0767a19da53ac35caaf81fddaa06fcf6
            # https://pcdn.metartnetwork.com/E6B595104E3411DF98790800200C9A66/media/9365AE2D434A1064E983A8629DECCB41/l_AA3CBBA100B18E84A197BC882E9B126D.jpg?filename=MetArt_Perfect-Art_Melena-A_low_0004.jpg&amp;type=inline&amp;ttl=1581770973&amp;token=0767a19da53ac35caaf81fddaa06fcf6
            img_url = re.sub(r'&amp;', '&', url)
            file = (model_name, filename, img_url)
            # print(file)
            contents.append(file)
        return contents

    def mkdir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
            print("mkdir path: %s" % path)

    def downImage(self, path, img_name, imageUrl):
        imagePath = os.path.join(path, img_name)
        if not os.path.exists(imagePath):
            try:
                self.time = self.downloader_process(imageUrl, imagePath)
                # self.downloader(imageUrl, imagePath)
            except Exception as e:
                print("Download FAILED!!: %s, %s" % (img_name, e))
                os.remove(imagePath)
                return False
            else:
                print("Download SUCCEED: %s" % img_name)
                return True
        else:
            print("File EXISTS, skip: %s" % img_name.replace('/', '\\'))
            return True

    def succeed_action(self, skip=False):
        if os.path.exists(self.contents_file):
            os.remove(self.contents_file)
        if skip:
            user_defined_str = 'Skip the model'
            print("%s:  %s!\n" % (user_defined_str, self.model))
            with open(self.skip_flag, 'w', encoding='utf-8') as f:
                f.write("%s:  %s \nurl:\t%s " %
                        (user_defined_str, self.model, self.url))
        else:
            dl_path = os.path.join(self.path, self.model)
            user_defined_str = 'All downloaded successfully'
            print("Path:  %s" % dl_path)
            print("%s:  %s!\n" % (user_defined_str, self.model))
            if self.need_open:
                self.opendir(dl_path)
            with open(self.succeed_flag, 'w', encoding='utf-8') as f:
                f.write("%s:  %s \nurl:\t%s " %
                        (user_defined_str, dl_path.replace('/', '\\'), self.url))

    def run(self):
        fi = None
        if os.path.exists(self.succeed_flag):
            fi = self.succeed_flag
        elif os.path.exists(self.skip_flag):
            fi = self.skip_flag
        if fi:
            with open(fi, 'r', encoding='utf-8') as f:
                print(f.readline().strip('\n'))
            return True

        contents = self.getContents()
        self.model = contents[0][0]
        if self.model in self._black_list:
            self.succeed_action(skip=True)
            return True
        if self.model in self._white_list:
            self.model = "[" + self.model + "]"
        dl_path = os.path.join(self.path, self.model)
        self.mkdir(dl_path)
        count = 0
        for content in contents:
            img_name = content[1]
            img_url = content[2]
            if self.downImage(dl_path, img_name, img_url):
                count += 1
        if count == len(contents):
            self.succeed_action()
            return True
        else:
            print("FAILED[%s]!Some imgs failed to download...\n" % self.model)
            return False

    @staticmethod
    def callbackfunc(blocknum, blocksize, totalsize):
        '''回调函数
        @blocknum: 已经下载的数据块
        @blocksize: 数据块的大小
        @totalsize: 远程文件的大小
        '''
        percent = 100.0 * blocknum * blocksize / totalsize
        if percent > 100:
            percent = 100
        # print("downloading %.2f%%" % percent)

    def downloader(self, url, path):
        start = time.time()
        request = urllib.request.Request(url, headers=self.headers)
        response = urllib.request.urlopen(request)
        imageContents = response.read()
        with open(path, 'wb') as f:
            f.write(imageContents)
        end = time.time()
        print("Run Time:%.2fs" % (end-start))

    def downloader_process(self, url, path):
        start = time.time()
        urllib.request.urlretrieve(url, path, self.callbackfunc)
        end = time.time()
        return end - start
        # print("Run Time:%.2fs" % (end-start))

    def getRemoteFileSize(self, url):
        ''' 通过content-length头获取远程文件大小
        url - 目标文件URL
        proxy - 代理  '''
        start = time.time()
        opener = urllib.request.build_opener()
        try:
            request = urllib.request.Request(url)
            request.get_method = lambda: 'HEAD'
            response = opener.open(request)
            response.read()
        except Exception:
            return 0
        else:
            # print(response.headers)
            fileSize = dict(response.headers).get('Content-Length', 0)
            end = time.time()
            print("url:%d" % int(fileSize))
            print("Run Time:%.2f秒" % (end-start))
            return int(fileSize)

    @staticmethod
    def opendir(path):
        path = path.replace('/', '\\')
        os.system("explorer.exe \"%s\"" % path)


class SpiderMP4:
    def __init__(self, url, path):
        self.url = url
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36"
        self.headers = {"Referer": self.url, "User-Agent": self.user_agent}
        self.path = path

    def downImage(self, path, img_name, imageUrl):
        imagePath = path+u"/"+img_name
        if not os.path.exists(path):
            os.makedirs(path)
            print("mkdir path: %s" % path)
        if not os.path.exists(imagePath):
            try:
                urllib.request.urlretrieve(imageUrl, imagePath)
            except Exception as e:
                print("Download FAILED:[%s] %s" % (img_name, e))
                return False
            else:
                print("Download SUCCEED: %s" % imagePath)
                return True
        else:
            print("File EXISTS, skip: %s\n" % imagePath.replace('/', '\\'))
            return True

    def run(self):
        request = urllib.request.Request(self.url, headers=self.headers)

        # response = urllib.request.urlopen(request)
        response = urllib_request_Request(self.url, 10809)
        url_content = response.read().decode("UTF-8")
        url_content_list = url_content.strip().splitlines()

        mp4url = None
        mp4_cover = None
        for oneurl in url_content_list:
            if "mp4" in oneurl:
                mp4url = oneurl.strip()
                index = url_content_list.index(oneurl)
                mp4_cover = url_content_list[index+1]
        # mp4url = 'file: "https://assets.metartnetwork.com/movies/offer/Godessnudes_Promo_2019.mp4",'
        img_name = list()
        if mp4url:
            # https://assets.metartnetwork.com/movies/offer/Godessnudes_Promo_2019.mp4",
            ret = re.findall(
                r"https://assets\.metartnetwork\.[^\.]+\.mp4", mp4url)
            for ret_one in ret:
                if ret_one:
                    print("Video Url:\t", ret_one)
                    img_name.append(os.path.basename(ret_one))
                    url_txt = os.path.basename(ret_one)[:-4]+".txt"
                    print(url_txt)
                    with open(self.path+u"/" + url_txt, 'w', encoding='utf-8') as f:
                        f.write(ret_one)

        if mp4_cover:
            # image: "https://billing.metartnetwork.com/view/images/offer/vivchef/slate.jpg",
            # print(mp4_cover)
            ret = re.findall(r"http.+jpg", mp4_cover)
            # print(ret)
            mp42jpg = zip(img_name, ret)
            for ret_one in mp42jpg:
                if ret_one:
                    print("Slate Url:\t", ret_one[1])
                    imgname = ret_one[0][:-4]+".jpg"
                    # print(imgname)
                    self.downImage(self.path, imgname, ret_one[1])


class SpiderArt:
    def __init__(self, url, path, opendir_flag=False):
        self.url = url
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36"
        self.headers = {"Referer": self.url, "User-Agent": self.user_agent}
        self.path = path
        self.titile = None
        self.err_list = list()
        self.opendir_flag = opendir_flag

    def opendir(self):
        path = self.path.replace('/', '\\')
        os.system("explorer.exe \"%s\"" % path)

    def downImages(self, urls):
        for url in urls:
            img_name = str(self.titile) + "_" + \
                str(urls.index(url)+1) + u".webp"
            # print(img_name)
            imagePath = self.path+u"/"+img_name
            if not self.downImage(imagePath, url):
                self.err_list.append(url)

    def downImage(self, imagePath, imageUrl):
        if not os.path.exists(imagePath):
            img_basename = os.path.basename(imagePath)
            try:
                # print("Downloading: %s" % img_basename)
                # start = time.time()
                urllib.request.urlretrieve(imageUrl, imagePath)
                # end = time.time()
                # print("Run Time:%.2fs" % (end-start))
            except Exception as e:
                print("Download[%s] FAILED: %s" % (img_basename, e))
                return False
            else:
                # print("Download SUCCEED![%.2fs]" % (end-start))
                print("SUCCEED[%s]" % img_basename)
                return True
        else:
            print("SUCCEED, IMG exists,skip: %s" % imagePath)
            return True

    def set_tittle(self, str):
        # "og:title" content="一组精美性感的女性胶片摄影作品"
        titile = re.search(
            r'\"og:title\" content=\"([^\"]+)\"', str, re.I).group(1)
        titile = re.sub('\W+', '-', titile)
        if titile[-1] == '-':
            titile = titile[0:-1]
        self.titile = titile
        self.path = os.path.join(self.path, self.titile)
        if not os.path.exists(self.path):
            os.makedirs(self.path)
            print("mkdir path: %s" % self.path)
        return True

    def run(self):
        request = urllib.request.Request(self.url, headers=self.headers)
        url_content = urllib.request.urlopen(self.url)
        response = urllib.request.urlopen(request)
        url_content = response.read().decode("UTF-8")
        self.set_tittle(url_content)
        attr_file = os.path.join(self.path, self.titile + ".txt")
        if not os.path.exists(attr_file):
            with open(attr_file, "w", encoding='utf-8') as f:
                f.write(url_content)
        all_urls = re.findall(
            r'data-src=\"([^\"]+)\"', url_content, re.IGNORECASE)
        img_urls = list()
        for url in all_urls:
            # 不要gif
            if not re.search(r'wx_fmt=gif', url, re.IGNORECASE):
                # print(url)
                img_urls.append(url)
        # 不要前三张,最后一张
        # img_urls.pop(0)
        # img_urls.pop(0)
        # img_urls.pop(0)
        img_urls.pop()
        if img_urls:
            self.downImages(img_urls)
        if not self.err_list:
            print("All Succeed.")
            if self.opendir_flag:
                self.opendir()


class SpiderTiktok:
    def __init__(self, url, path, opendir_flag=False):
        self.url = url
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36"
        self.headers = {"Referer": self.url, "User-Agent": self.user_agent}
        self.path = path
        self.titile = None
        self.err_list = list()
        self.opendir_flag = opendir_flag

    def opendir(self):
        path = self.path.replace('/', '\\')
        os.system("explorer.exe \"%s\"" % path)

    def down_file(self, file_path, file_url):
        if not os.path.exists(file_path):
            file_basename = os.path.basename(file_path)
            try:
                # start = time.time()
                urllib.request.urlretrieve(file_url, file_path)
                # end = time.time()
                # print("Run Time:%.2fs" % (end-start))
            except Exception as e:
                print("Download[%s] FAILED: %s\nurl:%s" %
                      (file_basename, e, file_url))
                self.err_list.append(file_basename)
                return False
            else:
                # print("Download SUCCEED![%.2fs]" % (end-start))
                print("SUCCEED[%s]" % file_basename)
                return True
        else:
            print("SUCCEED, IMG exists,skip: %s" % file_path)
            return True

    def set_tittle(self, str):
        # <p class="desc">#期待夏天 #魔鬼身材#你的女孩 好想和你一起过夏天啊～</p>
        # <div class="info"><p class="name nowrap">@猫宁 Baby</p></div>
        sep = '_'
        titile = re.search(
            r'<p class=\"desc\">([^<]+)</p>', str, re.I).group(1)
        titile = re.sub('\W+', sep, titile)
        author = re.search(
            r'<p class=\"name nowrap\">@([^<]+)</p>', str, re.I).group(1)
        author = re.sub('\W+', sep, author)
        if titile[0] == sep:
            titile = titile[1:]
        if titile[-1] == sep:
            titile = titile[0:-1]

        if author[0] == sep:
            author = author[1:]
        if author[-1] == sep:
            author = author[0:-1]

        self.titile = author + '-' + titile
        # print(titile, author)
        if len(self.path) > 260:
            raise RuntimeError
        if not os.path.exists(self.path):
            os.makedirs(self.path)
            print("mkdir path: %s" % self.path)
        return True

    def get_location(self, url):
        import requests
        res = requests.post(url=url, headers=self.headers,
                            allow_redirects=False)
        url = res.headers['location']
        return url

    def run(self):
        self.url = self.get_location(self.url)
        # print(self.url)
        request = urllib.request.Request(self.url, headers=self.headers)
        response = urllib.request.urlopen(request)
        url_content = response.read().decode("UTF-8")
        print(url_content)
        # soup = BeautifulSoup(url_content, "html.parser")
        # print("soup = %s" % soup)
        self.set_tittle(url_content)
        inspector_folder = os.path.join(self.path, 'inspector')
        if not os.path.exists(inspector_folder):
            os.makedirs(inspector_folder)
        attr_file = os.path.join(inspector_folder, self.titile + u".txt")
        if not os.path.exists(attr_file):
            with open(attr_file, "w", encoding='utf-8') as f:
                f.write(url_content)

        video_url = re.search(
            r'playAddr: ?\"([^\"]+)\"', url_content, re.IGNORECASE).group(1)
        cover_url = re.search(
            r'cover: ?\"([^\"]+)\"', url_content, re.IGNORECASE).group(1)
        suffix = '.' + cover_url[-8:].split('.')[1]  # .jpg/.png
        if cover_url:
            self.down_file(os.path.join(
                self.path, self.titile + suffix), cover_url)
        if video_url:
            video_url = self.get_location(video_url)
            mp4_file = os.path.join(self.path, self.titile + '.mp4')
            self.down_file(mp4_file, video_url)
        if not self.err_list:
            print("All Succeed!\n")
            if self.opendir_flag:
                self.opendir()


def get_urls(tmp_str):
    # return set(re.findall(r'http[^\s]+', tmp_str, re.IGNORECASE))
    return set(re.findall(r'http[^\s]+', tmp_str, re.IGNORECASE))


def main(url, black_list, white_list, download_path, opendir_flag=True):
    print("[{}]:  {}".format(urls.index(url) + 1, url))
    if re.search(r"subscription/preview", url):
        download_folder = os.path.join(download_path, "metart")
        spider = Spider(url, download_folder, black_list,
                        white_list, need_open=True)
    elif re.search(r'weixin', url, re.I):
        download_folder = os.path.join(download_path, "painting_art")
        spider = SpiderArt(url, download_folder, opendir_flag)
    elif re.search(r'douyin', url, re.IGNORECASE) or re.search(r'xigua', url, re.I):
        download_folder = os.path.join(
            download_path, "../douyin-xigua.download")
        spider = SpiderTiktok(url, download_folder, opendir_flag)
    else:
        download_folder = os.path.join(download_path, "metart_mp4")
        spider = SpiderMP4(url, download_folder)
    spider.run()


def get_list_from_txt(path):
    if os.path.exists(path):
        l = list()
        with open(path, 'r') as f:
            list_str = f.readlines()
            for item in list_str:
                item = item.strip('\n')
                if item:
                    item = item.split(' //', 1)[0]
                    item = item.split(' //', 1)[0]
                    l.append(item)
        return l
    else:
        with open(path, 'w') as f:
            f.write('')
        print("file doesn't exist: [{0}] .\nBut create.".format(path))
        return list()


def clean_succeed_flag_txt():
    print('clean start...')
    download_path = get_download_path(get_config_file())
    download_folder = os.path.join(download_path, "metart")
    dir = os.listdir(download_folder)
    for item in dir:
        if item.endswith("succeed.txt"):
            succeed_txt = os.path.join(download_folder, item)
            if os.path.exists(succeed_txt):
                print("delete file: {}".format(succeed_txt))
                os.remove(succeed_txt)
    print('clean completed.')


# def take_over_browser():
#     from selenium import webdriver
#     from selenium.webdriver.chrome.options import Options
#     chrome_options = Options()
#     # "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" - -remote - debugging - port = 9222 - -user - data - dir = "D:\HDC\coding\edgedriver_win64\data-dir"
#     chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
#     chrome_driver = "D:\\HDC\\coding\\chromedriver_win32\\chromedriver.exe"
#     driver = webdriver.Chrome(chrome_driver, options=chrome_options)
#     print(driver.current_url)
#     # driver.close()


class DownThread(Thread):
    def __init__(self, url, black_list, white_list, path):  # 可以通过初始化来传递参数
        super(DownThread, self).__init__()
        self._url = url
        self._black_list = black_list
        self._white_list = white_list
        self._path = path

    def run(self):
        main(self._url, self._black_list, self._white_list, self._path)


if __name__ == '__main__':

    # 是否使用多线程
    # use_thread = False
    config_file = get_config_file()
    print("*** MetArtDownloader version 1.0.2 Copyright (c) 2022 Carlo R. All Rights Reserved. ***")
    print("*** Contact us at uvery6@gmail.com ")
    print("> START...")
    print(f"> You could configure software in:\n    {config_file}")
    download_path = get_download_path(config_file)
    print("\n")
    use_thread = True

    need_clean = False
    if need_clean:
        clean_succeed_flag_txt()
    urls = get_list_from_txt('./urls.txt')
    black_list = get_list_from_txt('./blacklist.txt')
    white_list = get_list_from_txt('./whitelist.txt')
    if use_thread:
        threads = list()
        for url in urls:
            t = DownThread(url, black_list, white_list, download_path)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        print("全部结束.")
    else:
        for url in urls:
            main(url, black_list, white_list, download_path)
