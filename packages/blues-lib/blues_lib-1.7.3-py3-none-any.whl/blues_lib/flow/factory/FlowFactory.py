import sys,os,re
from typing import Union,List
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.factory.Factory import Factory
from type.flow.Flow import Flow
from flow.factory.CommandFactory import CommandFactory

class FlowFactory(Factory):
  
  def __init__(self,context:dict) -> None:
    self._context = context
    
  def create(self,arg:Union[List[str],str])->Flow:
    if isinstance(arg,str):
      return super().create(arg)
    else:
      return self.make(arg)
    
  def make(self,command_names:List[str])->Flow:
    flow = Flow()
    for command_name in command_names:
      command = CommandFactory(self._context).create(command_name)
      if command:
        flow.add(command)
    return flow
  
  def create_depth_spider(self):
    command_names = ['input','browser','depth_crawler','mat_fmt','persister','output']
    flow = self.make(command_names)
    return flow

  def create_spider(self):
    command_names = ['input','browser','crawler','brief_fmt','persister','output']

    flow = self.make(command_names)
    return flow

    
    
    