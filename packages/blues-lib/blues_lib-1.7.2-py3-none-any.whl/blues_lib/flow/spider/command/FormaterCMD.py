import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command
from task.fmt.MaterialFMT import MaterialFMT

class FormaterCMD(Command):

  name = __name__

  def execute(self):
    model = self._context['input']['crawler_model']
    entities = self._context['crawler'].data

    request = {
      'model':model,
      'entities':entities,
    }

    handler = MaterialFMT(request)
    stdout = handler.resolve()
    self._context['formater'] = stdout

    if stdout.code!=200:
      raise Exception('[Spider] Failed to format!')


