import sys
from bs4 import BeautifulSoup
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *

'''
https://stackoverflow.com/questions/21274865/scrape-multiple-urls-using-qwebpage
'''

INDEX_FORMAT = "http://www.newsmth.net/nForum/#!board/Picture?p=%d"

class MainPage(QWebPage):
    def __init__(self, start_page, end_page):
        self.app = QApplication(sys.argv)
        QWebPage.__init__(self)
        self.loadFinished.connect(self._loadFinished)
        self.article_map = {} # {href, article_title}
        # Some ads or non-artical pages
        self.exlusiveList = ['http://ad.newsmth.net/APP20180211.htm',
                             '/nForum/article/Picture/1739783',
                             '/nForum/article/Picture/47600',
                             '/nForum/article/Picture/13329',
                             '/nForum/article/Picture/25352',
                             '/nForum/article/Picture/1431378']
        self.is_index_page = True
        self.index_page_list = [INDEX_FORMAT % x for x in range(start_page, end_page)]
        self.index_page_list = ["http://www.baidu.com",
                                "http://www.baidu.com",
                                "http://www.sina.com.cn",
                                "http://www.163.com"]
        self.index_page_iter = iter(self.index_page_list)
        #self.render = Render()

    def start(self):
        print(self.index_page_list)
        self.crawlNextIndexPage()
        self.app.exec_()

    def crawlNextIndexPage(self):
        try:
            url = next(self.index_page_iter)
        except StopIteration:
            print("No more index page, quit!")
            return False
        else:
            self.is_index_page = True
            print("Load page %s\n" % url)
            self.load(url)
        return True

    def _loadFinished(self, result):
        self.processCurrentPage()
        if not self.crawlNextIndexPage():
            self.app.quit()

    def load(self, url):
        self.mainFrame().load(QUrl(url))

    def toHtmlTextString(self):
        return str(self.mainFrame().toHtml().toUtf8()).decode("utf-8")

    def processCurrentPage(self):
        print("ProcessCurrentPage")
        #print(self.toHtmlTextString())

    def crawl(self, pageNumber):
        self.parseSiteInfo()
        for i in range(1, self.max_entry_page_num):
            page_url = "http://www.newsmth.net/nForum/#!board/Picture?p=%d" % i
            print("Crawling page %d\tURL: %s" % (i, page_url))
            self.parseArticlePages(self.main_entry, pageNumber)
            if len(self.article_map) >= pageNumber:
                break

    def parseArticlePages(self, entry_url, pageNumber):
        '''Parse an entry page and add articles to article_map'''
        render = Render()
        render.load(entry_url)
        #self.render.load(entry_url)
        bs = BeautifulSoup(render.toHtmlTextString(), 'lxml')
        for item in bs.find_all('td', {'class':'title_9'}):
            if len(self.article_map) >= pageNumber:
                break
            link = item.find('a')
            title = link.get_text()
            href = link['href']
            if not href in self.exlusiveList and not self.article_map.has_key(href):
                # some articles may have same title, so append the last 3 characters
                self.article_map[href] = title + "#" + href[-3:] 

    def parseSiteInfo(self):
        '''Parse site information: max ariticle number, max entry page number'''
        render = Render()
        render.load(self.main_entry)
        #self.render.load(self.main_entry)
        bs = BeautifulSoup(render.toHtmlTextString(), 'lxml')
        page_pre = bs.find('li', {'class':'page-pre'})
        self.max_article_num = int(page_pre.find('i').get_text())

        # parse the max entry page number
        entry_page_list = bs.find('ol', {'class':'page-main'}).find_all('li')
        last_entry_page = entry_page_list[-2]
        self.max_entry_page_num = int(last_entry_page.find('a').get_text())

        print("Max ariticle number: %d" % self.max_article_num)
        print("Max entry page number: %d" % self.max_entry_page_num)

    def printArticalMap(self):
        print("Artical Map {Title, Page Link}:")
        for link, title in self.article_map.items():
            print(title + " : " + link)


if __name__ == "__main__":
    start_page = 1
    end_page = 10
    print(sys.argv)
    if len(sys.argv) == 3:
        start_page = int(sys.argv[1])
        end_page = int(sys.argv[2])
    print("Start crawl Newsmth Picture from page %d to page %d" % (start_page, end_page))
    mainpage = MainPage(start_page, end_page)
    mainpage.start()
