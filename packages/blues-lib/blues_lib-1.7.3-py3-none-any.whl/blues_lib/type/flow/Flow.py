import sys,os,re
from abc import ABC,abstractmethod
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.command.Command import Command
from type.output.STDOut import STDOut

class Flow(ABC):
  
  def __init__(self):
    self._commands:list[Command] = []

  def get_commands(self):
    return self._commands
    
  def add(self,command:Command):
    # add one command
    self._commands.append(command)
    
  def execute(self):

    if not self._commands:
      return STDOut(500,'No commands to execute!')

    try:
      for command in self._commands:
        command.execute()
        
      return STDOut(200,'Succeed to execute the flow.')
    except Exception as e:
      return STDOut(500,str(e))