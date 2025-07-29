import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from behavior.BhvExecutor import BhvExecutor
from type.output.STDOut import STDOut
from type.model.Model import Model
from sele.browser.Browser import Browser

class Crawler():

  def __init__(self,model:Model,browser:Browser,keep_alive:bool=True) -> None:
    '''
    @param model {Model} : the model of crawler
    @param browser {Browser} : the browser instance to use
    @param keep_alive {bool} : whether to keep the browser alive after crawl
    '''
    self._model = model
    self._browser = browser
    self._keep_alive = keep_alive

  def crawl(self)->STDOut:
    
    try:
      executor = BhvExecutor(self._model,self._browser)
      return executor.execute()
    except Exception as e:
      return STDOut(500,'Crawl failed %s' % e)
    finally:
      if self._browser and not self._keep_alive:
        self._browser.quit()


