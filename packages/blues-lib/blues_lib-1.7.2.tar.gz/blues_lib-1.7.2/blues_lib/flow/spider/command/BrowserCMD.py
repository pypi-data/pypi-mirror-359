import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command
from type.output.STDOut import STDOut
from sele.browser.BrowserFactory import BrowserFactory   

class BrowserCMD(Command):

  name = __name__

  def execute(self):

    crawler_model = self._context['input']['crawler_model']
    crawler_config = crawler_model.config

    browser_mode = crawler_config.get('browser').get('mode')
    executable_path = crawler_config.get('browser').get('path')

    loginer_model = self._context['input'].get('loginer_model')
    stdout = self._get_browser(browser_mode,executable_path,loginer_model)
    self._context['browser'] = stdout

    if stdout.code!=200:
      raise Exception(f'[Spider] Failed to create a browser!')

    
  def _get_browser(self,mode:str,path:str,loginer_model=None)->STDOut:
    kwargs = {
      'executable_path':path,
    }
    if loginer_model:
      kwargs['loginer_schema'] = loginer_model.config

    browser = BrowserFactory(mode).create(**kwargs)
    if browser:
      return STDOut(200,'ok',browser)
    else:
      return STDOut(500,'Failed to create the browser!')
