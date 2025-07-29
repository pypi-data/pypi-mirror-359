import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command

class OutputCMD(Command):

  name = __name__

  def execute(self):

    browser = self._context['browser'].data
    if browser:
      browser.quit()

    entities = None
    if self._context.get('formater'):
      entities = self._context['formater'].data
    self._context['output'] = entities

