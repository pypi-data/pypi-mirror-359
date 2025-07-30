import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command
from material.chain.BriefFmt import BriefFmt
from type.model.Model import Model

class BriefFmtCmd(Command):

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

    handler = BriefFmt(request)
    stdout = handler.resolve()
    self._context['formatter'] = stdout

    if stdout.code!=200:
      raise Exception('[Spider] Failed to format!')


