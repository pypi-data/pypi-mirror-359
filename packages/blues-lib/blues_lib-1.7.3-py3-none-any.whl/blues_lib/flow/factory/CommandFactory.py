import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.factory.Factory import Factory

from flow.command.input.InputCmd import InputCmd
from flow.command.browser.BrowserCmd import BrowserCmd

from flow.command.crawler.CrawlerCmd import CrawlerCmd
from flow.command.crawler.DepthCrawlerCmd import DepthCrawlerCmd

from flow.command.formatter.BriefFmtCmd import BriefFmtCmd
from flow.command.formatter.DetailFmtCmd import DetailFmtCmd
from flow.command.formatter.MatFmtCmd import MatFmtCmd

from flow.command.persister.PersisterCmd import PersisterCmd
from flow.command.output.OutputCmd import OutputCmd

class CommandFactory(Factory):
  
  def __init__(self,context:dict) -> None:
    self._context = context
    
  def create_input(self):
    return InputCmd(self._context)
    
  def create_browser(self):
    return BrowserCmd(self._context)

  def create_crawler(self):
    return CrawlerCmd(self._context)
  
  def create_depth_crawler(self):
    return DepthCrawlerCmd(self._context)

  def create_brief_fmt(self):
    return BriefFmtCmd(self._context)
  
  def create_detail_fmt(self):
    return DetailFmtCmd(self._context)

  def create_mat_fmt(self):
    return MatFmtCmd(self._context)

  def create_persister(self):
    return PersisterCmd(self._context)
  
  def create_output(self):
    return OutputCmd(self._context)
  