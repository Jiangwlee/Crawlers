import sys, os, requests
from bs4 import BeautifulSoup

INDEX_FORMAT = "http://www.newsmth.net/nForum/board/Picture?ajax&p=%d"
ARTICLE_PAGE_FORMAT = "http://www.newsmth.net/nForum/article/Picture/%s?ajax"
DOWNLOAD_DIR = "./NewsmthImages/"
NEWSMTH_DIR = ".newsmth/"
VISITED_URLS = os.path.join(NEWSMTH_DIR, "visited_urls.txt")

class NewsmthCrawler():
    '''A crawler to download images from http://www.newsmth.net'''
    def __init__(self, start_page, end_page):
        self.index_page_list = [INDEX_FORMAT % x for x in range(start_page, end_page)]
        self.article_page_dict = {}
        # Some ads or non-artical pages
        self.exlusiveList = ['http://ad.newsmth.net/APP20180211.htm',
                             '/nForum/article/Picture/1739783',
                             '/nForum/article/Picture/47600',
                             '/nForum/article/Picture/13329',
                             '/nForum/article/Picture/25352',
                             '/nForum/article/Picture/1431378']
        self._createDirIfNotExist(DOWNLOAD_DIR)
        self._createDirIfNotExist(NEWSMTH_DIR)
        self._loadVisitedUrls()

    def crawlIndexPages(self):
        for url in self.index_page_list:
            print("Crawling index page: %s" % (url))
            response = requests.get(url)
            self.parseIndexPage(response.text)

    def parseIndexPage(self, html):
        bs = BeautifulSoup(html, 'lxml')
        for item in bs.find_all('td', {'class':'title_9'}):
            link = item.find('a')
            title = link.get_text().replace("/", "")
            href = link['href']
            self._putArticleLink(href, title)

    def crawlArticlePages(self):
        for href, title in self.article_page_dict.items():
            article_id = os.path.basename(href)
            url = ARTICLE_PAGE_FORMAT % article_id
            if self._isVisited(url):
                print("Skip visited page (%s): %s" % (title, url))
                continue
            print("Crawling article page %s, URL: %s" % (title, url))
            dst_dir = DOWNLOAD_DIR + title
            self._createDirIfNotExist(dst_dir)
            response = requests.get(url)
            self.parseArticlePage(response.text, dst_dir)
            self._markVisited(url)

    def parseArticlePage(self, html, dst_dir):
        bs = BeautifulSoup(html, 'lxml')
        for item in bs.find_all('img', {'class':'resizeable'}):
            img = item['src']
            url = "http://" + img[2:-6]
            self.downloadImages(url, dst_dir)

    def downloadImages(self, url, dst_dir):
        response = requests.get(url)
        filename = response.headers['Content-Disposition'].split('=')[1]
        filepath = os.path.join(dst_dir, filename)
        with open(filepath, "wb") as outfile:
            outfile.write(response.content)
        print("Download image from %s to %s" % (url, filepath))

    def saveVisitedUrls(self):
        with open(VISITED_URLS, "w") as outfile:
            for url in self.visited_urls:
                outfile.write(url + "\n")
        print("Save visited URLs. %d URLs are saved!" % (len(self.visited_urls)))

    def _putArticleLink(self, href, title):
        if href in self.exlusiveList:
            return
        if not href in self.article_page_dict:
            self.article_page_dict[href] = title + href[-5:]

    def _createDirIfNotExist(self, path):
        if not os.path.exists(path) or not os.path.isdir(path):
            print("Create directory %s for images" % (path))
            os.mkdir(path)

    def _loadVisitedUrls(self):
        self.visited_urls = set([])
        if not os.path.exists(VISITED_URLS):
            visited_urls = open(VISITED_URLS, "w")
            visited_urls.close()
        with open(VISITED_URLS) as inputfile:
            for line in inputfile:
                self.visited_urls.add(line.strip())
        print("Load %d visited URLs" % (len(self.visited_urls)))

    def _markVisited(self, url):
        self.visited_urls.add(url)

    def _isVisited(self, url):
        return url in self.visited_urls

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python NewsmthCrawler.py start end\n")
        print("E.g. \"python NewsmthCrawler.py 1 5\" will crawl all articles from page 1 to page 5")
        exit(0)
    crawler = NewsmthCrawler(int(sys.argv[1]), int(sys.argv[2]))
    try:
        crawler.crawlIndexPages()
        crawler.crawlArticlePages()
    except Exception as ex:
        print("Exception catched: %s" % ex)
    finally:
        crawler.saveVisitedUrls()
