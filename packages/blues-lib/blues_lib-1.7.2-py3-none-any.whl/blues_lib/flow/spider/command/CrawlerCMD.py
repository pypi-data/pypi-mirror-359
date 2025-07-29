import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command
from task.crawler.PageCrawler import PageCrawler

class CrawlerCMD(Command):

  name = __name__

  def execute(self):

    model = self._context['input']['crawler_model']
    browser = self._context['browser'].data

    crawler = PageCrawler(model,browser)
    stdout = crawler.crawl()
    self._context['crawler'] = stdout

    if stdout.code!=200 or not stdout.data:
      raise Exception('[Spider] Failed to crawl available entities!')


