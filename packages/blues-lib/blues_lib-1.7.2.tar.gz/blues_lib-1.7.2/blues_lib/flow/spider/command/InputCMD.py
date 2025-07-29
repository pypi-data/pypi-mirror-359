import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command

class InputCMD(Command):

  name = __name__

  def execute(self):

    input = self._context.get('input')
    if not input:
      raise Exception('[Spider] The param input is missing!')

    if not input.get('crawler_model'):
      raise Exception('[Spider] The param input.crawler_model is missing!')
