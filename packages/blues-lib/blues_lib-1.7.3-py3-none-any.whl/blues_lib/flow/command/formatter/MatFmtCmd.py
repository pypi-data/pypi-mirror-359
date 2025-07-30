import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command
from task.fmt.MaterialFmt import MaterialFmt
from type.model.Model import Model

class MatFmtCmd(Command):

  name = __name__

  def execute(self):
    model = self._context['input']['crawler_model']
    node_meta = model.meta.get('formatter',{})
    entities = self._context['crawler'].data

    # use the meta
    node_model = Model(node_meta,model.bizdata)
    request = {
      'model':node_model,
      'entities':entities,
    }

    handler = MaterialFmt(request)
    stdout = handler.resolve()
    self._context['formatter'] = stdout

    if stdout.code!=200:
      raise Exception('[Spider] Failed to format!')


