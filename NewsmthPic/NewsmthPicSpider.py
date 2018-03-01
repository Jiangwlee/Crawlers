import sys, time
from bs4 import BeautifulSoup
from PyQt5.QtCore import QUrl, QByteArray
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
from PyQt5.QtWebEngineCore import *
from PyQt5.QtWidgets import QApplication

INDEX_FORMAT = "http://www.newsmth.net/nForum/#!board/Picture?p=%d"

class NewsmthRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self):
        QWebEngineUrlRequestInterceptor.__init__(self)

    def interceptRequest(self, info):
        self._addHeader(info, "Accept", "*/*")
        self._addHeader(info, "Pragma", "no-cache")
        self._addHeader(info, "Cache-Control", "max-age=0, no-cache")
        if not info.requestUrl().matches(QUrl("http://www.newsmth.net/nForum/board/Picture"), QUrl.RemoveQuery):
            return
        #    return
        print("Remove If-Modified-Since header for URL: %s" % info.requestUrl())
        self._addHeader(info, "X-Requested-With", "XMLHttpRequest")

    def _addHeader(self, info, header, value):
        h= QByteArray()
        v= QByteArray()
        h.append(header)
        v.append(value)
        info.setHttpHeader(h, v)

class NewsmthWebPage(QWebEngineView):
    def __init__(self, start_page, end_page):
        self.app = QApplication(sys.argv)
        QWebEngineView.__init__(self)
        self.is_index_page = True
        self.index_page_list = [INDEX_FORMAT % x for x in range(start_page, end_page)]
        # self.index_page_list = [#"http://www.baidu.com",
        #                         #"http://www.baidu.com",
        #                         "http://www.newsmth.net/nForum/#!board/Picture?p=3",
        #                         "http://www.newsmth.net/nForum/#!board/Picture?p=2",
        #                         "http://www.newsmth.net/nForum/#!board/Picture?p=2",
        #                         "http://www.newsmth.net/nForum/#!board/Picture?p=1"]
        #                         #"http://www.sina.com.cn",
        #                         #"http://www.baidu.com"]
        self.index_page_list = ["http://www.newsmth.net/nForum/board/Picture?ajax&p=1"]
        self.index_page_iter = iter(self.index_page_list)
        self.loadFinished.connect(self.handleLoadFinished)
        self.loadStarted.connect(self.handleLoadStarted)
        self.renderProcessTerminated.connect(self.handleRenderProcessTerminated)
        self.interceptor = NewsmthRequestInterceptor()
        self.profile = QWebEngineProfile()
        self.profile.setRequestInterceptor(self.interceptor)
        self.profile.setHttpCacheType(QWebEngineProfile.NoCache)
        self.profile.setHttpAcceptLanguage("zh-CN,zh;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2")

    def start(self):
        print(self.index_page_list)
        self.crawlNextIndexPage()
        self.app.exec_()

    def crawlNextIndexPage(self):
        try:
            url = next(self.index_page_iter)
        except StopIteration:
            return False
        else:
            self.is_index_page = True
            #self.setPage(QWebEnginePage(self.profile))
            self.setPage(QWebEnginePage())
            self.page().profile().setRequestInterceptor(self.interceptor)
            self.page().profile().setHttpCacheType(QWebEngineProfile.NoCache)
            self.page().profile().setHttpAcceptLanguage("zh-CN,zh;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2")
            self.load(QUrl(url))
        return True


    def handleLoadFinished(self):
        print("Load page success!\n")
        self.page().toHtml(self.processPage)
        #self.page().toPlainText(self.processPage)

    def handleLoadStarted(self):
        print("Load started, url: %s\n" % self.url().toString())

    def handleRenderProcessTerminated(self, status, exitcode):
        print("\nRender process terminated. Status: %s, Exit code: %d\n" % (status, exitcode))

    def processPage(self, data):
        #self.html = str(data.decode("utf-8"))
        if self.is_index_page:
            self.processIndexPage(data)
            if not self.crawlNextIndexPage():
                print("All index pages have been processed, quit!")
                self.app.quit()
        else:
            self.processArticalPage(data)
            self.app.quit()

    def processIndexPage(self, data):
        print(len(data))
        print(data)
        print("\n" * 3)
        #self.show()
        #time.sleep(10)

    def processArticalPage(self, data):
        print(data)

if __name__ == "__main__":
    start_page = 1
    end_page = 10
    print(sys.argv)
    if len(sys.argv) == 3:
        start_page = int(sys.argv[1])
        end_page = int(sys.argv[2])
    print("Start crawl Newsmth Picture from page %d to page %d" % (start_page, end_page))
    webpage = NewsmthWebPage(start_page, end_page)
    webpage.start()
