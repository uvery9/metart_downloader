import urllib.request
import re
import os
import time
import requests
import hashlib
# from bs4 import BeautifulSoup

class Spider:
    def __init__(self, url, path, need_open = True):
        self.url = url
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36"
        self.headers = { "Referer" : self.url, "User-Agent":self.user_agent }
        self.contents = None
        self.time = 0.00
        self.need_open = need_open
        self.model = None
        self.path = path
        self.try_again = True
        self.contents_file = None
        self.succeed_flag = None
        # req.add_header("Host","blog.csdn.net")
        # req.add_header("Referer","http://blog.csdn.net/")

    def getPage(self):
        if os.path.exists(self.contents_file):
            print("RETRY")
            with open(self.contents_file, 'r', encoding='utf-8') as f:
                return f.read()
        request = urllib.request.Request(self.url, headers=self.headers)
        try:
            response = urllib.request.urlopen(request)
            # url_content = response.read().decode("UTF-8")
            # url_content_list = url_content.strip().splitlines()
            contents = response.read()
        except Exception as e:
            print(e)
            return None
        else:
            ret = contents.decode("utf-8")
            if (re.findall(r'<div class="preview-images">.*alt=""/>', ret, re.IGNORECASE)):
                with open(self.contents_file, 'w', encoding='utf-8') as f:
                    f.write(ret)
            return ret

    def getContents(self):
        page = self.getPage()
        # print(page)
        # pattern = re.compile('''<div.*?class='num_1'.*?>.*?<p>.*?<a.*?href='.*?'.*?target='_blank'.*?title='(.*?)'.*?><img.*?src2="(.*?)".*?>.*?</a>.*?</p>.*?</div>''', re.S)
        items = re.findall(r'<div class="preview-images">.*alt=""/>', page, re.IGNORECASE)

        model_name = re.findall(r'<a href="[^"]+">([\w| ]+)</a>\.</p><div class="preview-images">', page)[0]
        # <a href="/model/melena-a">Melena A</a>
        # print(model_name)
        # items = re.findall(r'<img src=.+" alt=""/>', page)
        # print(items)
        contents = list()
        items_grp = re.findall(r'<img src="[^<]+"', items[0])
        p= re.compile('.+?"(.+?)"')
        for item in items_grp:
            # print(item)
            imgUrl = p.findall(item)
            # print(imgUrl[0])
            # re.search(r'<a.*>(.*)</a>',s).group(1)
            filename = re.search(r'filename=(.+\.jpg)', imgUrl[0]).group(1)
            # https://pcdn.metartnetwork.com/E6B595104E3411DF98790800200C9A66/media/9365AE2D434A1064E983A8629DECCB41/l_AA3CBBA100B18E84A197BC882E9B126D.jpg?filename=MetArt_Perfect-Art_Melena-A_low_0004.jpg&type=inline&ttl=1581770973&token=0767a19da53ac35caaf81fddaa06fcf6
            # https://pcdn.metartnetwork.com/E6B595104E3411DF98790800200C9A66/media/9365AE2D434A1064E983A8629DECCB41/l_AA3CBBA100B18E84A197BC882E9B126D.jpg?filename=MetArt_Perfect-Art_Melena-A_low_0004.jpg&amp;type=inline&amp;ttl=1581770973&amp;token=0767a19da53ac35caaf81fddaa06fcf6
            img_url = re.sub(r'&amp;', '&', imgUrl[0])
            # print(img_url)
            # file_size = self.getRemoteFileSize(img_url)
            file = (model_name, filename , img_url)
            # print(file)
            contents.append(file)
        self.contents = contents
        return self.contents

    def mkdir(self, path):
        if os.path.exists(path):
            # print("path exists: %s" % path)
            pass
        else:
            os.makedirs(path)
            print("mkdir path: %s" % path)

    def downImage(self, path, img_name, imageUrl):
        imagePath = path+u"/"+img_name
        if not os.path.exists(imagePath):
            try:
                self.time = self.downloader_process(imageUrl, imagePath)
                # self.downloader(imageUrl, imagePath)
            except Exception as e:
                print("Download FAILED: %s, %s" %(img_name, e))
                if self.try_again:
                    self.try_again = False
                    print("try again!")
                    self.downImage(path, img_name, imageUrl)
                else:
                     return False
            else:
                print("Download SUCCEED!! %s" % img_name)
                return True
        else:
            print("File EXISTS, skip: %s" % img_name)
            return True

    def run(self):
        url_hash = hashlib.md5(self.url.encode("utf8")).hexdigest()
        contents_file = self.path + url_hash + '.txt'
        self.contents_file = contents_file
        self.succeed_flag = self.path + url_hash + '-succeed.txt'
        # print(self.contents_file)
        if os.path.exists(self.succeed_flag):
            with open(self.succeed_flag, 'r', encoding='utf-8') as f:
                print(f.readline())
            return True
        if not self.contents:
            self.getContents()
        contents = self.contents
        self.model = contents[0][0]
        dl_path = self.path + self.model
        self.mkdir(dl_path)
        count = 0
        for content in contents:
            img_name = content[1]
            img_url = content[2]
            if self.downImage(dl_path, img_name, img_url):
                count += 1
        if count == 5:
            print("Path:  %s" % dl_path)
            print("All Download SUCCEED:  %s!\n" % self.model)
            if os.path.exists(self.contents_file):
                os.remove(self.contents_file)
            if self.need_open:
                self.opendir(dl_path)
            with open(self.succeed_flag, 'w', encoding='utf-8') as f:
                f.write("All Download SUCCEED:  %s \nurl:\t%s " % (dl_path.replace('/','\\'), self.url))
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
        request = urllib.request.Request(url, headers = self.headers)
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
        self.headers = { "Referer" : self.url, "User-Agent":self.user_agent}
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
                print("Download FAILED:[%s] %s" %(img_name, e))
                return False
            else:
                print("Download SUCCEED: %s" %imagePath)
                return True
        else:
            print("File EXISTS, skip: %s\n" % imagePath)
            return True

    def run(self):
        request = urllib.request.Request(self.url, headers = self.headers)
        response = urllib.request.urlopen(request)
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
            # print(mp4url)
            ret = re.findall(r"https://assets\.metartnetwork\.[^\.]+\.mp4", mp4url)
            # print(ret)
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
                    print("Slate Url:\t",ret_one[1])
                    imgname = ret_one[0][:-4]+".jpg"
                    # print(imgname)
                    self.downImage(self.path, imgname, ret_one[1])

class SpiderArt:
    def __init__(self, url, path, opendir_flag = False):
        self.url = url
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36"
        self.headers = { "Referer" : self.url, "User-Agent":self.user_agent}
        self.path = path
        self.titile = None
        self.err_list = list()
        self.opendir_flag = opendir_flag

    def opendir(self):
        path = self.path.replace('/', '\\')
        os.system("explorer.exe \"%s\"" % path)

    def downImages(self, urls):
        for url in urls:
            img_name = str(self.titile) + "_" + str(urls.index(url)+1) + u".webp"
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
                print("Download[%s] FAILED: %s" %(img_basename,e))
                return False
            else:
                # print("Download SUCCEED![%.2fs]" % (end-start))
                print("SUCCEED![%s]" % img_basename)
                return True
        else:
            print("SUCCEED! IMG exists,skip: %s" % imagePath)
            return True

    def set_tittle(self, str):
        # "og:title" content="一组精美性感的女性胶片摄影作品"
        titile = re.search(r'\"og:title\" content=\"([^\"]+)\"', str, re.I).group(1)
        titile = re.sub('\W+', '-', titile)
        if titile[-1] == '-':
            titile = titile[0:-1]
        self.titile = titile
        self.path += u"/" + self.titile
        if not os.path.exists(self.path):
            os.makedirs(self.path)
            print("mkdir path: %s" % self.path)
        return True

    def run(self):
        request = urllib.request.Request(self.url, headers = self.headers)
        url_content = urllib.request.urlopen(self.url)
        response = urllib.request.urlopen(request)
        url_content = response.read().decode("UTF-8")
        self.set_tittle(url_content)
        attr_file = self.path+ u'/' + self.titile+ u".txt"
        if not os.path.exists(attr_file):
            with open(attr_file, "w", encoding='utf-8') as f:
                f.write(url_content)
        all_urls = re.findall(r'data-src=\"([^\"]+)\"', url_content,re.IGNORECASE)
        img_urls = list()
        for url in all_urls:
            # 不要gif
            if not re.search(r'wx_fmt=gif', url, re.IGNORECASE):
                # print(url)
                img_urls.append(url)
        # 不要前三张,最后一张
        #img_urls.pop(0)
        #img_urls.pop(0)
        #img_urls.pop(0)
        img_urls.pop()
        if img_urls:
            self.downImages(img_urls)
        if not self.err_list:
            print("All Succeed!!!")
            if self.opendir_flag:
                self.opendir()


class SpiderTiktok:
    def __init__(self, url, path, opendir_flag = False):
        self.url = url
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36"
        self.headers = { "Referer" : self.url, "User-Agent":self.user_agent}
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
                print("Download[%s] FAILED: %s\nurl:%s" %(file_basename,e, file_url))
                self.err_list.append(file_basename)
                return False
            else:
                # print("Download SUCCEED![%.2fs]" % (end-start))
                print("SUCCEED![%s]" % file_basename)
                return True
        else:
            print("SUCCEED! IMG exists,skip: %s" % file_path)
            return True

    def set_tittle(self, str):
        # <p class="desc">#期待夏天 #魔鬼身材#你的女孩 好想和你一起过夏天啊～</p>
        # <div class="info"><p class="name nowrap">@猫宁 Baby</p></div>
        sep = '_'
        titile = re.search(r'<p class=\"desc\">([^<]+)</p>', str, re.I).group(1)
        titile = re.sub('\W+', sep, titile)
        author = re.search(r'<p class=\"name nowrap\">@([^<]+)</p>', str, re.I).group(1)
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
        res = requests.post(url=url, headers=self.headers, allow_redirects=False)
        url = res.headers['location']
        return url

    def run(self):
        self.url = self.get_location(self.url)
        # print(self.url)
        request = urllib.request.Request(self.url, headers = self.headers)
        response = urllib.request.urlopen(request)
        url_content = response.read().decode("UTF-8")
        print(url_content)
        # soup = BeautifulSoup(url_content, "html.parser")
        # print("soup = %s" % soup)
        self.set_tittle(url_content)
        if not os.path.exists(self.path+ u'/inspector/'):
            os.makedirs(self.path+ u'/inspector/')
        attr_file = self.path+ u'/inspector/' + self.titile+ u".txt"
        if not os.path.exists(attr_file):
            with open(attr_file, "w", encoding='utf-8') as f:
                f.write(url_content)

        video_url = re.search(r'playAddr: ?\"([^\"]+)\"', url_content,re.IGNORECASE).group(1)
        cover_url = re.search(r'cover: ?\"([^\"]+)\"', url_content,re.IGNORECASE).group(1)
        suffix = '.' + cover_url[-8:].split('.')[1] # .jpg/.png
        if cover_url:
            self.down_file(self.path+ u'/' + self.titile + suffix, cover_url)
        if video_url:
            video_url = self.get_location(video_url)
            # print(video_url)
            self.down_file(self.path+ u'/' + self.titile + u'.mp4', video_url)
        if not self.err_list:
            print("All Succeed!!!\n")
            if self.opendir_flag:
                self.opendir()

def get_urls(tmp_str):
    # return set(re.findall(r'http[^\s]+', tmp_str, re.IGNORECASE))
    return set(re.findall(r'http[^\s]+', tmp_str, re.IGNORECASE))

def change_drive(path):
    # path = u"D:\\jared\\Pictures\\photo_of_the_day"
    root = os.path.abspath(path)[:3]  # 获取当前目录所在硬盘的根目录
    rest = os.path.abspath(path)[3:]
    if not os.path.exists(root):
        path = "C:\\" + rest
        print("drive {} doesn't exist. \nUSE new path: {}".format(root, path))
    if not os.path.exists(path):
        os.makedirs(path)
        print("mkdir path: %s" % path)
    return path

def main(urls):
    if len(urls) == 1:
        opendir_flag = True
    else:
        opendir_flag = False
    for url in urls:
        print("[{}]:\t{}".format(urls.index(url) + 1, url))
        if re.search(r"subscription/preview", url):
            path = u"D:/jared/erotic/metart/"
            path = change_drive(path)
            spider = Spider(url, path, need_open = True)
        elif re.search(r'weixin', url, re.I):
            path = u"D:/jared/erotic/painting_art"
            path = change_drive(path)
            spider = SpiderArt(url, path, opendir_flag)
        elif re.search(r'douyin', url, re.IGNORECASE) or re.search(r'xigua', url, re.I):
            path = u"D:/jared/tiktok"
            path = change_drive(path)
            spider = SpiderTiktok(url, path, opendir_flag)
        else:
            path = u"D:/jared/erotic/metart_mp4"
            path = change_drive(path)
            spider = SpiderMP4(url, path)
        spider.run()

# path
def write_urls_to_txt(path = "./urls.txt"):
    with open(path, 'w') as f:
        for url in urls:
            f.write(url + '\n')

def read_urls_from_txt(path = "./urls.txt"):
    urls = list()
    if os.path.exists(path):
        with open(path, 'r') as f:
            urls_str = f.readlines()
            for url in urls_str:
                url = url.strip('\n')
                urls.append(url)
    else:
        print("file doesn't exist:{}".format(path))
        raise Exception("file doesn't exist")
    return urls

def clean_txt(path = 'D:\\jared\\erotic\\metart'):
    print('clean start...')
    path = change_drive(path)
    dir = os.listdir(path)
    for item in dir:
        if item.endswith("succeed.txt"):
            full_path = path + '\\' + item
            if os.path.exists(full_path):
                print("delete file: {}".format(full_path))
                os.remove(full_path)
    print('clean completed.')


if __name__ == '__main__':

    need_clean = False

    if need_clean:
        clean_txt(path = 'D:\\jared\\erotic\\metart')

    urls = read_urls_from_txt('./urls.txt')
    main(urls)

