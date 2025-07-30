import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command

class OutputCmd(Command):

  name = __name__

  def execute(self):

    browser = self._context['browser'].data
    if browser:
      browser.quit()

    entities = None
    if self._context.get('formatter'):
      entities = self._context['formatter'].data
    self._context['output'] = entities

