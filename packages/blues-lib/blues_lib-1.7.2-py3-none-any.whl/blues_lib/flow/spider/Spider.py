import sys,os,re

from .command.InputCMD import InputCMD
from .command.BrowserCMD import BrowserCMD
from .command.CrawlerCMD import CrawlerCMD
from .command.FormaterCMD import FormaterCMD
from .command.PersisterCMD import PersisterCMD
from .command.OutputCMD import OutputCMD

sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.flow.Flow import Flow

class Spider(Flow):
  
  def load(self):

    input_cmd = InputCMD(self._context)
    browser_cmd = BrowserCMD(self._context)
    crawler_cmd = CrawlerCMD(self._context)
    formater_cmd = FormaterCMD(self._context)
    persister_cmd = PersisterCMD(self._context)
    output_cmd = OutputCMD(self._context)

    # check if the input context is legal
    self.add(input_cmd)
    
    # add the context.browser
    self.add(browser_cmd)

    # add the items
    self.add(crawler_cmd)
    
    # format the entities
    self.add(formater_cmd)

    # save the entities to the db
    self.add(persister_cmd)
    
    # teardown and set the output value     
    self.add(output_cmd)

    