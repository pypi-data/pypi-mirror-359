import sys,os,re
from typing import List
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.output.STDOut import STDOut
from type.model.Model import Model
from sele.browser.Browser import Browser
from task.crawler.Crawler import Crawler

class PageCrawler():

  def __init__(self,model:Model,browser:Browser,keep_alive:bool=True) -> None:

    '''
    @param model {Model} : the model of page crawler
    @param browser {Browser} : the browser instance to use
    @param keep_alive {bool} : whether to keep the browser alive after crawl
    '''
    self._model = model
    self._browser = browser
    self._keep_alive = keep_alive
    
    self._meta = model.meta
    self._bizdata = model.bizdata
    self._config = model.config

  def crawl(self)->STDOut:
    try:
      return self._crawl()
    except Exception as e:
      return STDOut(500,'Briefs crawl failed %s' % e)
    finally:
      if self._browser and not self._keep_alive:
        self._browser.quit()
      
  def _crawl(self)->STDOut:
    # firstly : crawl the briefs
    briefs = self._crawl_briefs()
    if not briefs:
      return STDOut(500,'Briefs crawl failed')

    # secondly : loop to crawl the details
    materials = []
    count = int(self._config.get('count',0))

    for brief in briefs:
      self._append(brief,materials)
      if count and len(materials) >= count:
        break
    
    if materials:
      return STDOut(200,'ok',materials)
    else:
      return STDOut(500,'Materials crawl failed')
    
  def _append(self,brief,materials):
    bizdata = {
      'detail_url':brief.get('material_url'),
    }
    entity = self._crawl_detail(bizdata)
    if entity:
      # merge the brief fields
      materials.append({**brief,**entity})

  def _crawl_briefs(self)->List[dict]:
    config = self._config.get('brief') # use the initial config
    model = Model(config)
    crawler = Crawler(model,self._browser,True)
    stdout = crawler.crawl()
    return self._get_entity(stdout)
  
  def _crawl_detail(self,bizdata:dict)->dict:
    meta = self._meta.get('detail') # use the meta
    bd = {**self._bizdata,**bizdata} # interpolate with the mixed bizdata 
    model = Model(meta,bd)
    crawler = Crawler(model,self._browser,True)
    stdout = crawler.crawl()
    return self._get_entity(stdout)

  def _get_entity(self,stdout):
    if stdout.code == 200 and stdout.data:
      return stdout.data.get('entity')
    return None
