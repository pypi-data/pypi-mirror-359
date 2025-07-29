import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command
from type.output.STDOut import STDOut
from material.dao.mat.MatMutator import MatMutator 

class PersisterCMD(Command):

  name = __name__
  mutator = MatMutator()

  def execute(self):
    model = self._context['input']['crawler_model']
    entities = self._context['formater'].data
    preview = model.config.get('preview','Y')
    
    if preview == 'N':
      self._context['persister'] = STDOut(200,'No need to persistent!')
      return 

    stdout = self.mutator.insert(entities)
    self._context['persister'] = stdout

    if stdout.code != 200:
      raise Exception('Failed to insert the items to the DB!')


